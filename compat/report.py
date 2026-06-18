"""Unified compatibility report facade.

This module intentionally stays thin: it orchestrates the existing focused
``compat`` calculators, preserves their raw outputs, and adds a small,
versioned normalization layer for downstream reports/tests.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from hashlib import sha256
import json
from typing import Any

from compat.arrhenius import all_pathways
from compat.osmolality import osmolality_report
from compat.ph_module import degradation_vs_ph, ph_window_check
from compat.redox import flag_from_components
from compat.solubility import additive_report
from compat.water_activity import aw_report

SCHEMA_VERSION = "compat-eval-v0.1"

_STANDING_SOLUTION_TYPES = {
    "hydration_drink",
    "acute_sublingual_or_drench",
    "oral_drench",
    "wet_concentrate",
    "wet_core_plus_dry_activator",
    "reconstituted_drink",
}
_HYDRATION_TYPES = {"hydration_drink", "reconstituted_drink", "wet_concentrate"}
_DRY_TYPES = {"dry_capsule", "dry_premix"}


def _components_as_tuples(components: Sequence[Mapping[str, Any] | Sequence[Any]]) -> list[tuple[str, float]]:
    """Accept ``[(name, grams)]`` or ``[{name/key/id, grams/g/mass_g}]`` inputs."""
    normalized: list[tuple[str, float]] = []
    for item in components:
        if isinstance(item, Mapping):
            name = item.get("name") or item.get("key") or item.get("id")
            grams = item.get("grams", item.get("g", item.get("mass_g")))
        else:
            name, grams = item[0], item[1]
        if name is None or grams is None:
            raise ValueError(f"component must include name and grams: {item!r}")
        normalized.append((str(name), float(grams)))
    return normalized


def _registry_snapshot() -> str:
    """Return a stable lightweight stamp for the in-repo physical registry."""
    try:
        from compat.data import MOLAR_MASS_G_PER_MOL, SUBSTANCES
    except Exception:  # pragma: no cover - defensive only
        return "compat-data@unknown"
    payload = json.dumps(
        {
            "substances": sorted(SUBSTANCES),
            "molar_masses": sorted(MOLAR_MASS_G_PER_MOL),
        },
        sort_keys=True,
    ).encode("utf-8")
    return f"compat-data@{sha256(payload).hexdigest()[:12]}"


def _finding(
    *,
    id: str,
    module: str,
    severity: str,
    applies: bool,
    metric: str,
    message: str,
    evidence: Mapping[str, Any] | None = None,
    next_action: str = "No action required.",
    score_delta: float = 0.0,
    cap: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": id,
        "module": module,
        "severity": severity,
        "applies": applies,
        "metric": metric,
        "score_delta": score_delta,
        "message": message,
        "evidence": dict(evidence or {}),
        "next_action": next_action,
    }
    if cap is not None:
        result["cap"] = dict(cap)
    return result


def _applicability(product_type: str, water_ml: float | None, delivered_water_ml: float | None) -> dict[str, Any]:
    standing = product_type in _STANDING_SOLUTION_TYPES and (water_ml or delivered_water_ml) is not None
    hydration = product_type in _HYDRATION_TYPES
    dry = product_type in _DRY_TYPES
    notes: list[str] = []
    if dry:
        notes.append("dry product: standing-solution osmolality is not applied unless reconstituted water is supplied")
    elif standing:
        notes.append("aqueous standing-solution gates apply at the evaluated concentration")
    else:
        notes.append("limited aqueous gates: no water volume supplied")
    if product_type == "wet_concentrate":
        notes.append("wet concentrate should be evaluated both in-bottle and at delivered dilution")
    return {
        "standing_solution": standing,
        "hydration_claim": hydration,
        "dry_ingestion": dry,
        "notes": notes,
    }


def _score_osmolality(osmo: Mapping[str, Any] | None, applies: bool) -> tuple[float, float, list[dict[str, Any]]]:
    if not applies or osmo is None:
        return 10.0, 10.0, [
            _finding(
                id="osmolality.not_applicable",
                module="compat.osmolality",
                severity="INFO",
                applies=False,
                metric="hydration",
                message="Standing-solution osmolality gate is not applicable for this product mode/input.",
            )
        ]

    gate = osmo["ors_gate"]
    electro = osmo["electrolyte_balance"]
    verdict = gate["verdict"]
    if verdict == "PASS" and electro["complete_ors"]:
        score, cap, severity, delta = 9.0, 10.0, "INFO", 0.0
    elif verdict == "MARGINAL" and electro["complete_ors"]:
        score, cap, severity, delta = 7.0, 7.5, "WARNING", -1.5
    elif verdict == "BLOCK":
        score, cap, severity, delta = 2.5, 2.5, "BLOCKER", -4.0
    else:
        score, cap, severity, delta = 4.0, 4.0, "BLOCKER", -3.0

    findings = [
        _finding(
            id="osmolality.ors_gate",
            module="compat.osmolality",
            severity=severity,
            applies=True,
            metric="hydration",
            score_delta=delta,
            cap={"metric": "hydration", "max_score": cap},
            message=f"{gate['total_mosm_per_l']:.0f} mOsm/L -> {verdict}",
            evidence={
                "value": gate["total_mosm_per_l"],
                "unit": "mOsm/L",
                "threshold": 350.0,
                "source": "compat.osmolality.HYPERTONIC_GATE",
                "raw_note": gate["note"],
            },
            next_action=(
                "Dilute, cut osmotic load, or move high-osmotic actives to a dry SKU."
                if severity == "BLOCKER"
                else "Keep delivered concentration inside the isotonic hydration band."
            ),
        )
    ]
    if not electro["complete_ors"]:
        findings.append(
            _finding(
                id="osmolality.electrolytes_incomplete",
                module="compat.osmolality",
                severity="BLOCKER",
                applies=True,
                metric="hydration",
                score_delta=-3.0,
                cap={"metric": "hydration", "max_score": min(cap, 4.0)},
                message="No sodium/electrolyte source present; not a complete ORS.",
                evidence={"raw_reason": electro["reason"], "na_mmol": electro["na_mmol"], "k_mmol": electro["k_mmol"], "cl_mmol": electro["cl_mmol"]},
                next_action="Add a Na/K/Cl premix before claiming hydration/ORS function.",
            )
        )
        cap = min(cap, 4.0)
        score = min(score, 4.0)
    unknown = osmo["osmolarity"].get("unknown_molar_mass", [])
    for name in unknown:
        findings.append(
            _finding(
                id=f"unknown.molar_mass.{name}",
                module="compat.osmolality",
                severity="INSUFFICIENT_DATA",
                applies=True,
                metric="hydration",
                score_delta=-0.5,
                message=f"{name} is missing molar mass; osmoles omitted from total.",
                evidence={"substance": name},
                next_action="Add reviewed molar-mass data before treating the osmolality pass as final.",
            )
        )
    return score, cap, findings


def _score_solubility(sol: Mapping[str, Any] | None, applies: bool) -> tuple[float, list[dict[str, Any]]]:
    if not applies or sol is None:
        return 10.0, [
            _finding(
                id="solubility.not_applicable",
                module="compat.solubility",
                severity="INFO",
                applies=False,
                metric="solubility",
                message="Aqueous solubility gate is not applicable for this product mode/input.",
            )
        ]
    findings: list[dict[str, Any]] = []
    score = 10.0
    if sol["bottlenecks"]:
        score = 5.0
        for i, bottleneck in enumerate(sol["bottlenecks"], start=1):
            findings.append(
                _finding(
                    id=f"solubility.bottleneck.{i}",
                    module="compat.solubility",
                    severity="WARNING",
                    applies=True,
                    metric="solubility",
                    score_delta=-2.0,
                    message=bottleneck,
                    evidence={"raw": bottleneck},
                    next_action="Reduce dose, increase solvent, use suspension labeling, or move insoluble actives to dry SKU.",
                )
            )
    else:
        findings.append(
            _finding(
                id="solubility.all_dissolved",
                module="compat.solubility",
                severity="INFO",
                applies=True,
                metric="solubility",
                message="No solubility bottlenecks at the evaluated concentration.",
                evidence={"tds_w_v_pct": sol["tds"]["w_v_pct"]},
            )
        )
    if sol["tds"].get("salting_out_flag"):
        score = min(score, 7.0)
        findings.append(
            _finding(
                id="solubility.high_tds",
                module="compat.solubility",
                severity="WARNING",
                applies=True,
                metric="solubility",
                score_delta=-1.5,
                message=f"TDS {sol['tds']['w_v_pct']:.2f}% w/v exceeds salting-out screen.",
                evidence=sol["tds"],
                next_action="Lower dissolved solids or validate salting-out experimentally.",
            )
        )
    for i, warning in enumerate(sol.get("supersaturation_warnings", []), start=1):
        findings.append(
            _finding(
                id=f"solubility.supersaturation.{i}",
                module="compat.solubility",
                severity="ADVISORY",
                applies=True,
                metric="solubility",
                message=warning,
                evidence={"raw": warning},
                next_action="Check crystallization after cooling/storage.",
            )
        )
    return score, findings


def evaluate_formula(
    components: Sequence[Mapping[str, Any] | Sequence[Any]],
    *,
    product_type: str = "hydration_drink",
    water_ml: float | None = None,
    delivered_water_ml: float | None = None,
    phase_map: Mapping[str, str] | None = None,
    target_ph: float | None = None,
    storage: Mapping[str, Any] | None = None,
    packaging: Mapping[str, Any] | None = None,
    use_case: str = "oral_hydration",
    evidence_level: str = "screening",
    assumptions: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return a normalized compatibility/stability/readiness report.

    The facade is intentionally conservative: existing raw module outputs are
    preserved under ``gates`` while normalized ``findings``/``scores`` provide a
    stable contract for tests and future report consumers.
    """
    comp = _components_as_tuples(components)
    eval_water_ml = delivered_water_ml if delivered_water_ml is not None else water_ml
    app = _applicability(product_type, water_ml, delivered_water_ml)
    aqueous_applies = app["standing_solution"] and eval_water_ml is not None

    gates: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    validation: list[str] = []

    osmo = sol = aw = None
    if aqueous_applies:
        osmo = osmolality_report(comp, water_ml=float(eval_water_ml))
        sol = additive_report(comp, water_ml=float(eval_water_ml))
        aw = aw_report(comp, water_ml=float(eval_water_ml))
        gates["osmolality"] = osmo
        gates["solubility"] = sol
        gates["water_activity"] = aw
    else:
        gates["osmolality"] = {"applicable": False, "reason": "dry/no standing solution water volume"}
        gates["solubility"] = {"applicable": False, "reason": "dry/no aqueous solvent volume"}

    hydration_score, hydration_cap, osmo_findings = _score_osmolality(osmo, aqueous_applies and app["hydration_claim"])
    solubility_score, sol_findings = _score_solubility(sol, aqueous_applies)
    findings.extend(osmo_findings)
    findings.extend(sol_findings)

    if target_ph is not None:
        ph = ph_window_check(float(target_ph))
        gates["ph"] = {"window": ph, "degradation": degradation_vs_ph(float(target_ph))}
        findings.append(
            _finding(
                id="ph.window",
                module="compat.ph_module",
                severity="INFO" if ph["in_window"] else "WARNING",
                applies=True,
                metric="stability",
                score_delta=0.0 if ph["in_window"] else -1.0,
                message=ph["reason"],
                evidence=ph,
                next_action="Keep pH in the validated target window or justify with stability data.",
            )
        )
    else:
        unknowns.append({"id": "ph.target", "message": "No target pH supplied; pH-window stability gate not evaluated."})

    gates["arrhenius"] = all_pathways()
    findings.append(
        _finding(
            id="shelf.arrhenius_screening_only",
            module="compat.arrhenius",
            severity="ADVISORY",
            applies=True,
            metric="shelf",
            message="Arrhenius projections are screening estimates; shelf-life claims require stability studies.",
            evidence={"pathways": sorted(gates["arrhenius"])},
            next_action="Run stress and real-time stability studies before assigning shelf life.",
        )
    )
    validation.append("Bench/real-time stability data required for shelf-life claims; calculations are screening only.")

    oxygen = (packaging or storage or {}).get("oxygen_exposure", "headspace")
    light = (packaging or storage or {}).get("light_exposure", "opaque")
    redox = flag_from_components(comp, oxygen_exposure=oxygen, light_exposure=light)
    gates["redox"] = redox
    if redox.get("applicable", True):
        sev = "WARNING" if redox.get("risk_level") in {"MODERATE", "HIGH", "SEVERE"} else "ADVISORY"
        findings.append(
            _finding(
                id="redox.ascorbate",
                module="compat.redox",
                severity=sev,
                applies=True,
                metric="shelf",
                score_delta=-1.0 if sev == "WARNING" else 0.0,
                message=f"Ascorbate redox risk: {redox.get('risk_level')}",
                evidence={"drivers": redox.get("drivers", []), "mitigations": redox.get("mitigations", [])},
                next_action="Control O2/light/metals and verify ascorbate retention.",
            )
        )
    else:
        findings.append(
            _finding(
                id="redox.not_applicable",
                module="compat.redox",
                severity="INFO",
                applies=False,
                metric="shelf",
                message="Ascorbate redox screen not applicable to this formula.",
                evidence=redox,
            )
        )

    commercial_score = 8.0
    if aw is not None:
        if aw["microbial_class"] == "HIGH_RISK":
            commercial_score = 5.0
            findings.append(
                _finding(
                    id="water_activity.high_aw",
                    module="compat.water_activity",
                    severity="WARNING",
                    applies=True,
                    metric="commercial_readiness",
                    score_delta=-2.0,
                    message=aw["preservation_flag"],
                    evidence=aw,
                    next_action="Use make-fresh/discard instructions or validate preservation with micro/challenge testing.",
                )
            )
            validation.append("High-aw wet product requires preservative/challenge-test evidence for commercial shelf claims.")

    unknown_names = set()
    for name in (osmo or {}).get("osmolarity", {}).get("unknown_molar_mass", []):
        unknown_names.add(name)
    for name in (aw or {}).get("unknown_mw", []):
        unknown_names.add(name)
    for name in sorted(unknown_names):
        unknowns.append({"id": f"unknown.molar_mass.{name}", "substance": name, "message": "Missing molar mass in compat registry."})

    blocker = any(f["applies"] and f["severity"] == "BLOCKER" for f in findings)
    warning = any(f["applies"] and f["severity"] == "WARNING" for f in findings)
    insufficient = bool(unknowns) or any(f["severity"] == "INSUFFICIENT_DATA" for f in findings)
    if blocker:
        verdict = "BLOCK"
        overall_score = min(hydration_score, solubility_score, commercial_score, 4.0)
    elif insufficient:
        verdict = "INSUFFICIENT_DATA"
        overall_score = min(hydration_score, solubility_score, commercial_score, 6.0)
    elif warning:
        verdict = "MARGINAL"
        overall_score = min(hydration_score, solubility_score, commercial_score, 7.5)
    else:
        verdict = "PASS"
        overall_score = min(hydration_score, solubility_score, commercial_score, 9.0)

    confidence = "Low" if insufficient else ("Medium" if warning or product_type in {"wet_concentrate", "wet_core_plus_dry_activator"} else "High")
    scores = {
        "compatibility": round(solubility_score, 2),
        "stability": 7.0 if warning else 8.0,
        "commercial_readiness": round(commercial_score, 2),
        "hydration_cap": round(hydration_cap, 2),
        "score_0_10": round(overall_score, 2),
        "stats_card_adjustments": [
            {"finding_id": f["id"], "score_delta": f["score_delta"], "cap": f.get("cap")}
            for f in findings
            if f.get("score_delta") or f.get("cap")
        ],
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "product_type": product_type,
        "use_case": use_case,
        "evidence_level": evidence_level,
        "registry_snapshot": _registry_snapshot(),
        "components": [{"name": name, "grams": grams} for name, grams in comp],
        "water_ml": water_ml,
        "delivered_water_ml": delivered_water_ml,
        "phase_map": dict(phase_map or {}),
        "applicability": app,
        "overall": {
            "verdict": verdict,
            "blocking": blocker,
            "score_0_10": round(overall_score, 2),
            "confidence": confidence,
            "summary": f"{verdict}: {len([f for f in findings if f['severity'] == 'BLOCKER'])} blocker(s), {len([f for f in findings if f['severity'] == 'WARNING'])} warning(s).",
        },
        "scores": scores,
        "findings": findings,
        "gates": gates,
        "assumptions": list(assumptions or []) + ["screening calculation only; not lab validation"],
        "unknowns": unknowns,
        "validation_checklist": validation,
        "provenance": [
            {"module": "compat.osmolality", "function": "osmolality_report"},
            {"module": "compat.solubility", "function": "additive_report"},
            {"module": "compat.ph_module", "function": "ph_window_check/degradation_vs_ph"},
            {"module": "compat.arrhenius", "function": "all_pathways"},
            {"module": "compat.redox", "function": "flag_from_components"},
            {"module": "compat.water_activity", "function": "aw_report"},
        ],
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render a concise Markdown summary from an ``evaluate_formula`` report."""
    lines = [
        f"# Compatibility report ({report['schema_version']})",
        "",
        f"- Product type: `{report['product_type']}`",
        f"- Verdict: **{report['overall']['verdict']}** ({report['overall']['confidence']} confidence)",
        f"- Score: {report['overall']['score_0_10']}/10",
        f"- Registry: `{report['registry_snapshot']}`",
        "",
        "## Findings",
    ]
    for finding in report.get("findings", []):
        applies = "applies" if finding["applies"] else "n/a"
        lines.append(f"- **{finding['severity']}** `{finding['id']}` ({applies}): {finding['message']}")
    if report.get("unknowns"):
        lines.extend(["", "## Unknowns"])
        for unknown in report["unknowns"]:
            lines.append(f"- `{unknown['id']}`: {unknown['message']}")
    if report.get("validation_checklist"):
        lines.extend(["", "## Next validation"])
        for item in report["validation_checklist"]:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
