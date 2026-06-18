"""Normalized compatibility/stability/commercial-readiness scoring.

This module is a thin report/scoring facade over the focused chemistry
calculators in :mod:`compat`.  It intentionally does not recalculate
solubility or osmolality chemistry; callers may either pass precomputed module
reports or use :func:`evaluate_formula` to run the existing module APIs once.

The schema is screening-grade decision support, not a safety certificate.
Hard gates stay explicit as findings/caps so they cannot be averaged away by a
strong aggregate score.
"""

from __future__ import annotations

from typing import Any, Iterable

SCHEMA_VERSION = "compat-eval-v0.1"

SEVERITIES = {"BLOCKER", "WARNING", "ADVISORY", "INFO", "INSUFFICIENT_DATA"}

HYDRATION_PRODUCT_TYPES = {"hydration_drink", "reconstituted_ors", "wet_concentrate", "wet_core_plus_dry_activator"}
AQUEOUS_PRODUCT_TYPES = HYDRATION_PRODUCT_TYPES | {"acute_sublingual_or_drench"}
DRY_PRODUCT_TYPES = {"dry_capsule", "dry_premix"}
WET_STORED_PRODUCT_TYPES = {"hydration_drink", "wet_concentrate", "wet_core_plus_dry_activator", "acute_sublingual_or_drench"}
KNOWN_PRODUCT_TYPES = HYDRATION_PRODUCT_TYPES | AQUEOUS_PRODUCT_TYPES | DRY_PRODUCT_TYPES


def clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    """Clamp a 0-10 score."""

    return max(lo, min(hi, value))


def confidence_from_findings(findings: Iterable[dict[str, Any]]) -> str:
    severities = {f.get("severity") for f in findings if f.get("applies", True)}
    if "INSUFFICIENT_DATA" in severities:
        return "Low"
    if "BLOCKER" in severities or "WARNING" in severities:
        return "Medium"
    return "High"


def make_finding(
    *,
    id: str,
    module: str,
    severity: str,
    metric: str,
    message: str,
    applies: bool = True,
    score_delta: float = 0.0,
    cap: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    next_action: str = "",
) -> dict[str, Any]:
    if severity not in SEVERITIES:
        raise ValueError(f"unknown severity {severity!r}")
    return {
        "id": id,
        "module": module,
        "severity": severity,
        "applies": applies,
        "metric": metric,
        "score_delta": round(score_delta, 2),
        "cap": cap,
        "message": message,
        "evidence": evidence or {},
        "next_action": next_action,
    }


def score_solubility_report(report: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize an existing ``compat.solubility.additive_report`` result.

    Returns a score, findings, and notes without rerunning solubility checks.
    The mapping mirrors the stats-card v0.2 physical gate: full dissolve = 10,
    unknown physical constants = 4, bottlenecks cap by worst dissolved fraction,
    salting-out = 7, supersaturation = 8.
    """

    if report is None:
        return {"score": 10.0, "findings": [], "notes": []}

    findings: list[dict[str, Any]] = []
    notes: list[str] = []
    unknown = list(report.get("unknown_physical") or [])
    bottlenecks = list(report.get("bottlenecks") or [])
    supersat = list(report.get("supersaturation_warnings") or [])
    tds = report.get("tds") or {}
    salting_out = bool(tds.get("salting_out_flag"))

    worst_fraction = 1.0
    water_ml = float(report.get("water_ml", 0.0) or 0.0)
    substance_rows = list(report.get("substances") or [])
    for context in (report.get("contexts") or {}).values():
        if isinstance(context, dict):
            substance_rows.extend(context.get("substances") or [])
    for substance in substance_rows:
        grams_value = substance.get("grams")
        if grams_value is None and water_ml > 0 and substance.get("conc_g_per_100ml") is not None:
            grams_value = float(substance.get("conc_g_per_100ml") or 0.0) * water_ml / 100.0
        if grams_value is None and substance.get("undissolved_g") is not None and substance.get("dissolved_g") is not None:
            grams_value = float(substance.get("undissolved_g") or 0.0) + float(substance.get("dissolved_g") or 0.0)
        grams = float(grams_value or 0.0)
        undissolved = float(substance.get("undissolved_g", 0.0) or 0.0)
        if grams > 0:
            worst_fraction = min(worst_fraction, max(0.0, min(1.0, (grams - undissolved) / grams)))

    score = 10.0
    if unknown:
        score = 4.0
        findings.append(make_finding(
            id="solubility.insufficient_profile",
            module="compat.solubility",
            severity="INSUFFICIENT_DATA",
            metric="solubility",
            score_delta=-6.0,
            message="solution-phase ingredient lacks reviewed physical solubility profile",
            evidence={"unknown_physical": unknown},
            next_action="add reviewed physical solubility/molar-mass registry data before claiming solution delivery",
        ))
        notes.extend("UNKNOWN solution solubility: " + item for item in unknown)
    if bottlenecks:
        score = min(score, max(0.0, 4.0 * worst_fraction))
        findings.append(make_finding(
            id="solubility.bottleneck",
            module="compat.solubility",
            severity="WARNING",
            metric="solubility",
            score_delta=round(score - 10.0, 2),
            cap={"metric": "compatibility", "max_score": round(score, 2)},
            message="one or more solution-phase ingredients exceed solubility ceiling",
            evidence={"bottlenecks": bottlenecks, "worst_dissolved_fraction": round(worst_fraction, 4)},
            next_action="reduce dose, increase delivered water, move insoluble actives to dry phase, or validate suspension",
        ))
        notes.extend(bottlenecks)
    elif salting_out:
        score = min(score, 7.0)
        findings.append(make_finding(
            id="solubility.high_tds_salting_out",
            module="compat.solubility",
            severity="WARNING",
            metric="solubility",
            score_delta=-3.0,
            cap={"metric": "compatibility", "max_score": 7.0},
            message="TDS exceeds salting-out/crystallization screening threshold",
            evidence={"tds_w_v_pct": tds.get("w_v_pct")},
            next_action="dilute, lower total dissolved solids, or validate cold/aging crystallization behavior",
        ))
        notes.append("TDS >20% w/v: salting-out / crystallization risk")
    elif supersat:
        score = min(score, 8.0)
        findings.append(make_finding(
            id="solubility.supersaturation_cooling",
            module="compat.solubility",
            severity="ADVISORY",
            metric="solubility",
            score_delta=-2.0,
            cap={"metric": "compatibility", "max_score": 8.0},
            message="cooling may cause supersaturation/crystallization",
            evidence={"warnings": supersat},
            next_action="verify cold storage and post-dilution clarity",
        ))
        notes.extend(supersat)

    return {"score": round(clamp(score), 2), "findings": findings, "notes": notes}


def score_osmolality_report(report: dict[str, Any] | None, *, hydration_claim: bool = True) -> dict[str, Any]:
    """Normalize an existing ``compat.osmolality.osmolality_report`` result.

    The mapping intentionally matches the existing stats-card hydration cap
    behavior to avoid double-counting or score drift during integration.
    """

    if report is None or not hydration_claim:
        finding = make_finding(
            id="osmolality.not_applicable",
            module="compat.osmolality",
            severity="INFO",
            metric="hydration",
            applies=False,
            message="standing-solution ORS osmolality gate is not applicable to this product mode",
            next_action="apply only if the dry product is reconstituted or claims hydration delivery",
        )
        return {"score": 10.0, "hydration_cap": 10.0, "findings": [finding] if report is None else [], "notes": []}

    gate = report.get("ors_gate") or {}
    electro = report.get("electrolyte_balance") or {}
    osm = report.get("osmolarity") or {}
    mosm = float(gate.get("total_mosm_per_l", 0.0) or 0.0)
    verdict = str(gate.get("verdict", "INSUFFICIENT_DATA"))
    complete_ors = bool(electro.get("complete_ors"))
    notes = [f"{mosm:.0f} mOsm/L -> {verdict}: {gate.get('note', '')}".strip()]
    findings: list[dict[str, Any]] = []

    unknown_mw = list(osm.get("unknown_molar_mass") or [])
    if unknown_mw:
        notes.append("UNKNOWN osmoles for: " + ", ".join(unknown_mw) + " (molar mass missing in registry; osmolarity is under-estimated)")
        findings.append(make_finding(
            id="osmolality.insufficient_molar_mass",
            module="compat.osmolality",
            severity="INSUFFICIENT_DATA",
            metric="hydration",
            score_delta=-3.0,
            message="one or more solutes are missing molar mass, so osmolality is under-estimated",
            evidence={"unknown_molar_mass": unknown_mw},
            next_action="add reviewed molar mass/osmotic particle registry data",
        ))
    if not complete_ors:
        reason = str(electro.get("reason", "ORS electrolyte completeness not demonstrated"))
        notes.append(reason)
        findings.append(make_finding(
            id="osmolality.incomplete_ors",
            module="compat.osmolality",
            severity="BLOCKER" if hydration_claim else "WARNING",
            metric="hydration",
            score_delta=-6.0,
            cap={"metric": "hydration", "max_score": 4.0},
            message=reason,
            evidence={"electrolyte_balance": electro},
            next_action="add sodium/potassium/chloride at delivered concentration or drop hydration/ORS claim",
        ))

    if verdict == "PASS" and complete_ors:
        score, cap = 9.0, 10.0
        findings.append(make_finding(
            id="osmolality.ors_pass",
            module="compat.osmolality",
            severity="INFO",
            metric="hydration",
            message="delivered osmolality and electrolyte completeness pass hydration screen",
            evidence={"total_mosm_per_l": mosm, "verdict": verdict},
        ))
    elif verdict == "MARGINAL" and complete_ors:
        score, cap = 7.0, 7.5
        findings.append(make_finding(
            id="osmolality.marginal",
            module="compat.osmolality",
            severity="WARNING",
            metric="hydration",
            score_delta=-2.0,
            cap={"metric": "hydration", "max_score": cap},
            message="delivered osmolality is marginal for hydration use",
            evidence={"total_mosm_per_l": mosm, "verdict": verdict},
            next_action="dilute or lower osmotic load",
        ))
    else:
        cap = 4.0 if mosm <= 700 else 2.5
        if not complete_ors:
            cap = min(cap, 4.0)
        score = cap
        findings.append(make_finding(
            id="osmolality.hypertonic_or_blocked",
            module="compat.osmolality",
            severity="BLOCKER",
            metric="hydration",
            score_delta=round(score - 9.0, 2),
            cap={"metric": "hydration", "max_score": cap},
            message=f"{mosm:.0f} mOsm/L yields {verdict}; hydration claim is capped",
            evidence={"total_mosm_per_l": mosm, "verdict": verdict, "threshold_mosm_per_l": 350.0},
            next_action="dilute, cut osmotic load, or move high-osmotic actives to a dry/non-hydration SKU",
        ))

    return {"score": round(clamp(score), 2), "hydration_cap": round(clamp(cap), 2), "findings": findings, "notes": notes}


def score_readiness(
    *,
    product_type: str,
    solubility_score: float,
    osmolality_score: float,
    preservative_validated: bool | None = None,
    emulsion_validated: bool | None = None,
    evidence_level: str = "screening",
) -> dict[str, Any]:
    """Compute aggregate compatibility/stability/commercial readiness scores.

    This layer uses normalized module scores and validation flags only; it does
    not inspect ingredients or rerun chemistry.
    """

    findings: list[dict[str, Any]] = []
    compatibility = (float(solubility_score) + float(osmolality_score)) / 2.0
    stability = 8.0
    commercial = 7.0

    if product_type in WET_STORED_PRODUCT_TYPES and preservative_validated is not True:
        stability -= 0.8
        commercial -= 1.2
        findings.append(make_finding(
            id="commercial.preservative_challenge_missing",
            module="compat.scoring",
            severity="WARNING",
            metric="commercial_readiness",
            score_delta=-1.2,
            message="wet/high-aw commercial shelf claim lacks preservative challenge validation",
            next_action="run microbial spec and preservative/challenge testing or label make-fresh use",
        ))
    if emulsion_validated is False:
        stability -= 0.8
        commercial -= 0.8
        findings.append(make_finding(
            id="commercial.emulsion_validation_missing",
            module="compat.scoring",
            severity="WARNING",
            metric="commercial_readiness",
            score_delta=-0.8,
            message="emulsion/separation stability is not validated",
            next_action="run separation, dose-uniformity, oxidation, and potency/distribution checks",
        ))
    if evidence_level == "screening":
        commercial -= 0.5
        findings.append(make_finding(
            id="commercial.screening_only",
            module="compat.scoring",
            severity="ADVISORY",
            metric="commercial_readiness",
            score_delta=-0.5,
            message="scores are screening calculations without lab/field validation",
            next_action="calibrate against stress assay, real-time stability, microbial, and field data",
        ))

    return {
        "compatibility": round(clamp(compatibility), 2),
        "stability": round(clamp(stability), 2),
        "commercial_readiness": round(clamp(commercial), 2),
        "findings": findings,
    }


def evaluate_formula(
    components: list[dict[str, Any]] | list[tuple[str, float]],
    *,
    product_type: str,
    water_ml: float | None = None,
    delivered_water_ml: float | None = None,
    hydration_claim: bool | None = None,
    preservative_validated: bool | None = None,
    emulsion_validated: bool | None = None,
    evidence_level: str = "screening",
    solubility_report: dict[str, Any] | None = None,
    osmolality_report_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a normalized compatibility/stability/readiness report.

    ``components`` are ``(compat_key, grams)`` pairs or dicts with ``name`` and
    ``grams`` keys.  Dry product types do not apply standing-solution gates
    unless the caller supplies delivered water and explicitly makes a hydration
    claim.
    """

    normalized_components: list[tuple[str, float]] = []
    for item in components:
        if isinstance(item, dict):
            normalized_components.append((str(item.get("name") or item.get("key")), float(item.get("grams", 0.0))))
        else:
            name, grams = item
            normalized_components.append((str(name), float(grams)))

    if product_type not in KNOWN_PRODUCT_TYPES:
        raise ValueError(f"unknown product_type {product_type!r}; expected one of {sorted(KNOWN_PRODUCT_TYPES)}")
    if hydration_claim is None:
        hydration_claim = product_type in HYDRATION_PRODUCT_TYPES
    supplied_water = delivered_water_ml is not None or water_ml is not None
    solution_applies = product_type in AQUEOUS_PRODUCT_TYPES or (product_type not in DRY_PRODUCT_TYPES and supplied_water) or (product_type in DRY_PRODUCT_TYPES and bool(hydration_claim) and supplied_water)
    dry_mode = product_type in DRY_PRODUCT_TYPES and not solution_applies

    run_water_ml = delivered_water_ml if delivered_water_ml is not None else water_ml
    if solution_applies and run_water_ml is None:
        raise ValueError("water_ml or delivered_water_ml is required for aqueous compatibility scoring")

    if solubility_report is None and solution_applies and run_water_ml is not None:
        from compat.solubility import additive_report

        solubility_report = additive_report(normalized_components, float(run_water_ml))
    if osmolality_report_data is None and hydration_claim and solution_applies and run_water_ml is not None:
        from compat.osmolality import osmolality_report as _osmolality_report

        osmolality_report_data = _osmolality_report(normalized_components, water_ml=float(run_water_ml))

    sol_score = score_solubility_report(solubility_report if solution_applies else None)
    osmo_score = score_osmolality_report(osmolality_report_data, hydration_claim=bool(hydration_claim and solution_applies))
    readiness = score_readiness(
        product_type=product_type,
        solubility_score=float(sol_score["score"]),
        osmolality_score=float(osmo_score["score"]),
        preservative_validated=preservative_validated,
        emulsion_validated=emulsion_validated,
        evidence_level=evidence_level,
    )
    findings = [*sol_score["findings"], *osmo_score["findings"], *readiness["findings"]]
    blocking = any(f.get("severity") == "BLOCKER" and f.get("applies", True) for f in findings)
    verdict = "BLOCK" if blocking else ("INSUFFICIENT_DATA" if any(f.get("severity") == "INSUFFICIENT_DATA" for f in findings) else ("MARGINAL" if any(f.get("severity") == "WARNING" for f in findings) else "PASS"))

    score_0_10 = min(readiness["compatibility"], readiness["stability"], readiness["commercial_readiness"]) if blocking else (readiness["compatibility"] + readiness["stability"] + readiness["commercial_readiness"]) / 3.0

    validation_checklist = [f["next_action"] for f in findings if f.get("next_action")]
    unknowns = [f for f in findings if f.get("severity") == "INSUFFICIENT_DATA"]

    return {
        "schema_version": SCHEMA_VERSION,
        "product_type": product_type,
        "applicability": {
            "solution_applies": bool(solution_applies),
            "standing_solution": bool(solution_applies and not dry_mode),
            "hydration_claim": bool(hydration_claim),
            "dry_ingestion": bool(product_type in DRY_PRODUCT_TYPES),
            "notes": (["dry product: standing-solution osmolality not applied"] if dry_mode else []),
        },
        "overall": {
            "verdict": verdict,
            "blocking": blocking,
            "score_0_10": round(clamp(score_0_10), 2),
            "confidence": confidence_from_findings(findings),
            "summary": "hard blocker present; redesign before optimizing efficacy" if blocking else "screening compatibility report generated",
        },
        "scores": {
            "compatibility": readiness["compatibility"],
            "stability": readiness["stability"],
            "commercial_readiness": readiness["commercial_readiness"],
            "hydration_cap": osmo_score["hydration_cap"],
            "stats_card_adjustments": [
                {"target": f.get("cap", {}).get("metric"), "cap": f.get("cap", {}).get("max_score"), "reason": f.get("message")}
                for f in findings
                if isinstance(f.get("cap"), dict)
            ],
        },
        "findings": findings,
        "gates": {"solubility": solubility_report, "osmolality": osmolality_report_data},
        "unknowns": unknowns,
        "validation_checklist": validation_checklist,
        "provenance": [
            {"module": "compat.scoring", "schema_version": SCHEMA_VERSION},
            {"module": "compat.solubility", "role": "source report; no chemistry recalculated"},
            {"module": "compat.osmolality", "role": "source report; no chemistry recalculated"},
        ],
    }
