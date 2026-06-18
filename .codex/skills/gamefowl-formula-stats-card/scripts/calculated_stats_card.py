#!/usr/bin/env python3
"""
Calculated gamefowl/avian formula stats card.

This is a transparent v0.2 scoring engine: not a proof of efficacy, but a
repeatable calculation that turns a formula table into comparable numbers.

It combines:
  1) ingredient contribution profiles by metric
  2) dose saturation vs a reference dose
  3) evidence multipliers
  4) timing/architecture multipliers (acute vs preload; wet vs dry)
  5) physical-chemistry gates: solubility, osmolality, oil load, wet
     reducing-sugar/amine/vitamin risk, and shelf-readiness penalties
  6) explicit cap/penalty ledger + metric confidence labels

Run from a project that has the gaiteva compat/ package for deeper
solubility/osmolality checks; otherwise it falls back to the built-in
heuristics.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# When this skill script is executed by absolute path, Python puts the skill's
# script directory on sys.path, not the user's project cwd. Add cwd explicitly
# so project-local calculators such as gaiteva/compat are importable.
sys.path.insert(0, str(Path.cwd()))

METRICS = [
    "Focus / alertness",
    "Energy availability",
    "Fatigue/stress tolerance",
    "Fast recovery",
    "ATP regeneration",
    "Anti-inflammatory / antioxidant support",
    "Respiratory / acid-base support",
    "Hydration / electrolyte balance",
    "GI tolerance",
    "Onset speed",
    "Shelf stability / commercial readiness",
]

SHORT = {
    "Focus / alertness": "focus",
    "Energy availability": "energy",
    "Fatigue/stress tolerance": "fatigue",
    "Fast recovery": "recovery",
    "ATP regeneration": "atp",
    "Anti-inflammatory / antioxidant support": "antiox",
    "Respiratory / acid-base support": "resp",
    "Hydration / electrolyte balance": "hydration",
    "GI tolerance": "gi",
    "Onset speed": "onset",
    "Shelf stability / commercial readiness": "shelf",
}

EVIDENCE_MULT = {
    "avian": 1.00,
    "field": 0.85,
    "avian_indirect": 0.80,
    "mechanism": 0.65,
    "non_avian": 0.50,
    "unknown": 0.35,
}

EVIDENCE_CONFIDENCE = {
    "avian": 0.95,
    "field": 0.80,
    "avian_indirect": 0.72,
    "mechanism": 0.55,
    "non_avian": 0.45,
    "unknown": 0.25,
}

# Map scoring-profile keys to the project compat package keys.  Keep this
# outside the profile object so external profile JSON can still override with
# `solubility_key` when a new dossier adds a new compat constant.
ACTIVE_REVIEW_STATUSES = {"reviewed", "verified"}

# Only these phases represent an aqueous solution where solubility must be
# demonstrated. Dry/powder/capsule phases are intentionally excluded: they may
# be swallowed or mixed as solids, so aqueous solubility is not a formula gate
# unless the formula author labels them as drink/make_fresh/solution.
SOLUTION_PHASES = {"wet", "solution", "drink", "make_fresh"}
STORED_SOLUTION_PHASES = {"wet", "solution"}
USE_SOLUTION_PHASES = {"drink", "make_fresh"}

COMPAT_KEY_MAP = {
    "d_ribose": "d_ribose",
    "dmg": "dmg",
    "lclt": "l_carnitine_l_tartrate",
    "magnesium_chloride": "magnesium_chloride",
    "sodium_chloride": "sodium_chloride",
    "potassium_chloride": "potassium_chloride",
    "sodium_citrate": "trisodium_citrate",
    "ascorbate": "ascorbic_acid",
    "taurine": "taurine",
    "betaine": "betaine_anhydrous",
    "l_tyrosine": "l_tyrosine",
    "creatine": "creatine_monohydrate",
    "gaa": "gaa",
}


@dataclass(frozen=True)
class Ingredient:
    key: str
    label: str
    amount: float
    unit: str = "mg"  # mg or mL per event dose
    phase: str = "wet"  # wet, dry, oil, preservative, excipient
    timing: str = "acute"  # acute, preload, chronic, excipient


@dataclass(frozen=True)
class Profile:
    ref: float
    unit: str
    evidence: str
    effects: dict[str, float]
    chronic_only: bool = False
    wet_reactive_class: str | None = None  # reducing_sugar, primary_amine, vitamin, redox, thiol
    solubility_key: str | None = None  # optional key in project compat.data.SUBSTANCES
    notes: str = ""


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()



def profile_from_dict(data: dict[str, Any]) -> Profile:
    evidence = str(data.get("evidence", "unknown"))
    if evidence not in EVIDENCE_MULT:
        evidence = "unknown"
    return Profile(
        ref=float(data["ref"]),
        unit=str(data.get("unit", "mg")),
        evidence=evidence,
        effects={str(k): float(v) for k, v in dict(data.get("effects", {})).items()},
        chronic_only=bool(data.get("chronic_only", False)),
        wet_reactive_class=data.get("wet_reactive_class"),
        solubility_key=data.get("solubility_key"),
        notes=str(data.get("notes", "")),
    )


def load_profile_file(path: str | Path) -> dict[str, Profile]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"profile file must be a JSON object: {path}")
    profiles: dict[str, Profile] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        status = str(value.get("review_status", "draft")).lower()
        if status not in ACTIVE_REVIEW_STATUSES:
            # Draft/rejected/blocked/unset records must not create benefit points.
            # The formula scorer will report the ingredient as UNKNOWN PROFILE.
            continue
        profiles[str(key)] = profile_from_dict(value)
    return profiles


def _registry_json_files(*roots: Path) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(sorted(root.glob("*.json")))
    return files


def load_default_profiles() -> dict[str, Profile]:
    profiles: dict[str, Profile] = {}
    roots = [SKILL_ROOT / "registry" / "effects", PROJECT_ROOT / "substances" / "effects"]
    for f in _registry_json_files(*roots):
        profiles.update(load_profile_file(f))
    return profiles


PROFILES: dict[str, Profile] = load_default_profiles()


PRESETS: dict[str, dict[str, Any]] = {
    "route_a": {
        "name": "Route A Wet Core",
        "architecture": "single_wet_bottle",
        "target_shelf_months": 6,
        "dose_ml": 5.0,
        "oil_pct": 30.0,
        "wet_water_ml_per_100ml": 60.0,
        "preservative_validated": False,
        "emulsion_validated": False,
        "ingredients": [
            Ingredient("mct_oil", "MCT oil", 1.5, "mL", "oil"),
            Ingredient("d_ribose", "D-ribose", 500, "mg", "wet"),
            Ingredient("dmg", "DMG", 150, "mg", "wet"),
            Ingredient("lclt", "LCLT", 100, "mg", "wet", "acute"),
            Ingredient("magnesium_chloride", "MgCl2", 40, "mg", "wet"),
            Ingredient("sodium_citrate", "Sodium citrate", 125, "mg", "wet"),
            Ingredient("taurine", "Taurine", 75, "mg", "wet"),
            Ingredient("ascorbate", "Sodium ascorbate", 40, "mg", "wet"),
        ],
    },
    "v3_hybrid": {
        "name": "V3 Hybrid Core Emulsion + Dry Activator",
        "architecture": "wet_core_plus_dry_activator",
        "target_shelf_months": 6,
        "dose_ml": 5.0,
        "oil_pct": 20.0,
        "wet_water_ml_per_100ml": 70.0,
        "preservative_validated": False,
        "emulsion_validated": False,
        "ingredients": [
            Ingredient("mct_oil", "MCT oil", 1.0, "mL", "oil"),
            Ingredient("d_ribose", "D-ribose", 300, "mg", "wet"),
            Ingredient("dmg", "DMG", 100, "mg", "wet"),
            Ingredient("lclt", "LCLT", 50, "mg", "wet", "acute"),
            Ingredient("coq10", "CoQ10", 5, "mg", "oil", "chronic"),
            Ingredient("vitamin_e_acetate", "Vitamin E acetate", 10, "mg", "oil", "chronic"),
            Ingredient("magnesium_chloride", "MgCl2", 40, "mg", "wet"),
            Ingredient("sodium_chloride", "NaCl", 25, "mg", "wet"),
            Ingredient("potassium_chloride", "KCl", 10, "mg", "wet"),
            Ingredient("sodium_citrate", "Sodium citrate", 12.5, "mg", "wet"),
            Ingredient("l_tyrosine", "L-tyrosine", 200, "mg", "dry"),
            Ingredient("b6", "B6/P5P", 2.5, "mg", "dry"),
            Ingredient("ascorbate", "Vitamin C", 75, "mg", "dry"),
            Ingredient("taurine", "Taurine", 125, "mg", "dry"),
            Ingredient("betaine", "Betaine", 250, "mg", "dry"),
            Ingredient("creatine", "Creatine/GAA preload equivalent", 200, "mg", "dry", "preload"),
        ],
    },
}


def clamp(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, x))


def dose_factor(ing: Ingredient, prof: Profile) -> float:
    if ing.amount <= 0 or prof.ref <= 0:
        return 0.0
    return min(1.35, math.sqrt(ing.amount / prof.ref))


def timing_factor(metric: str, ing: Ingredient, prof: Profile) -> float:
    if prof.chronic_only and ing.timing not in {"preload", "chronic"}:
        if metric in {"onset", "focus"}:
            return 0.15
        return 0.45
    if ing.timing == "preload" and metric == "onset":
        return 0.30
    return 1.0


def _wet_multiplier_per_100ml(formula: dict[str, Any]) -> float:
    dose_ml = float(formula.get("dose_ml", 5.0))
    return 100.0 / dose_ml if dose_ml > 0 else 20.0


def _wet_water_ml_per_dose(formula: dict[str, Any]) -> float:
    if formula.get("delivered_water_ml") is not None:
        return float(formula["delivered_water_ml"])
    dose_ml = float(formula.get("dose_ml", 5.0))
    wet_water_ml_per_100ml = float(formula.get("wet_water_ml_per_100ml", 70.0))
    return wet_water_ml_per_100ml * dose_ml / 100.0


def _compat_key(ing: Ingredient, prof: Profile | None = None) -> str | None:
    return (prof.solubility_key if prof else None) or COMPAT_KEY_MAP.get(ing.key) or ing.key


def _is_solution_phase(phase: str) -> bool:
    return phase in SOLUTION_PHASES


def load_physical_registry_overlays() -> None:
    """Overlay physical constants from JSON registries into compat.data at runtime.

    This prevents future substances from requiring edits to compat/data.py.  Project
    records under `substances/physical/*.json` override skill defaults.
    """
    files = _registry_json_files(
        SKILL_ROOT / "registry" / "physical",
        PROJECT_ROOT / "substances" / "physical",
    )
    if not files:
        return
    try:
        from compat import data as compat_data  # type: ignore
    except Exception:
        return
    for f in files:
        raw = json.loads(f.read_text(encoding="utf-8"))
        records = raw.values() if isinstance(raw, dict) and "compat_key" not in raw else [raw]
        for rec in records:
            if not isinstance(rec, dict):
                continue
            status = str(rec.get("review_status", "draft")).lower()
            if status not in ACTIVE_REVIEW_STATUSES:
                continue
            key = str(rec.get("compat_key") or rec.get("key") or "").strip()
            if not key:
                continue
            if "solubility_g_per_100ml_25c" in rec:
                compat_data.SUBSTANCES.setdefault(key, {})["solubility_g_per_100ml_25c"] = rec["solubility_g_per_100ml_25c"]
                compat_data.SUBSTANCES[key].setdefault("density_kg_m3", rec.get("density_kg_m3"))
                compat_data.SUBSTANCES[key].setdefault("pka", rec.get("pka", []))
                compat_data.SUBSTANCES[key]["note"] = rec.get("note", f"registry overlay from {f}")
            if "molar_mass_g_per_mol" in rec:
                compat_data.MOLAR_MASS_G_PER_MOL[key] = float(rec["molar_mass_g_per_mol"])
            if "osmotic_n" in rec:
                compat_data.OSMOTIC_N[key] = float(rec["osmotic_n"])
            ions = rec.get("ions_mmol_per_g")
            if isinstance(ions, dict):
                compat_data.ELECTROLYTE_IONS[key] = {f"{ion}_mmol_per_g": float(v) for ion, v in ions.items()}


def _solution_contexts(formula: dict[str, Any]) -> list[dict[str, Any]]:
    """Return aqueous-solution contexts that must pass solubility.

    Stored wet concentrates are checked at in-bottle concentration. Ingredients
    explicitly marked drink/make_fresh are checked at the delivered water volume.
    Dry/powder/oil/excipient phases are intentionally absent from this list.
    """
    contexts: list[dict[str, Any]] = []
    if any(i.phase in STORED_SOLUTION_PHASES and i.unit == "mg" for i in formula["ingredients"]):
        contexts.append({
            "name": "stored_solution",
            "phases": STORED_SOLUTION_PHASES,
            "water_ml": float(formula.get("wet_water_ml_per_100ml", 70.0)),
            "amount_multiplier": _wet_multiplier_per_100ml(formula),
            "concentration_note": "stored wet concentration",
        })
    if any(i.phase in USE_SOLUTION_PHASES and i.unit == "mg" for i in formula["ingredients"]):
        contexts.append({
            "name": "use_solution",
            "phases": USE_SOLUTION_PHASES,
            "water_ml": float(formula.get("delivered_water_ml") or _wet_water_ml_per_dose(formula)),
            "amount_multiplier": 1.0,
            "concentration_note": "use-solution concentration",
        })
    return contexts


def solubility_analysis(formula: dict[str, Any]) -> dict[str, Any]:
    fractions = {ing.key: 1.0 for ing in formula["ingredients"]}
    try:
        load_physical_registry_overlays()
        from compat import data as compat_data  # type: ignore
        from compat.solubility import additive_report  # type: ignore

        contexts = _solution_contexts(formula)
        if not contexts:
            return {"fractions": fractions, "report": None, "score": 10.0, "notes": []}

        reports: list[dict[str, Any]] = []
        notes: list[str] = []
        all_bottlenecks: list[str] = []
        all_supersaturation: list[str] = []
        unknown_physical: list[str] = []
        worst_fraction = 1.0
        max_tds = 0.0
        salting_out = False

        for context in contexts:
            compat_components: list[tuple[str, float]] = []
            by_key: dict[str, tuple[str, float, str]] = {}
            for ing in formula["ingredients"]:
                if ing.phase not in context["phases"] or ing.unit != "mg":
                    continue
                prof = PROFILES.get(ing.key)
                mapped = _compat_key(ing, prof)
                if not mapped or mapped not in compat_data.SUBSTANCES:
                    # Solution case: no physical record means we cannot prove the
                    # ingredient dissolves, so it gets no solution-delivered benefit.
                    fractions[ing.key] = 0.0
                    unknown_physical.append(
                        f"{ing.label} ({ing.key}) in {context['name']}: missing physical solubility profile"
                    )
                    continue
                grams = ing.amount * float(context["amount_multiplier"]) / 1000.0
                compat_components.append((mapped, grams))
                by_key[ing.key] = (mapped, grams, str(context["concentration_note"]))

            if not compat_components:
                continue

            report = additive_report(compat_components, float(context["water_ml"]))
            report["context"] = context["name"]
            reports.append(report)
            all_bottlenecks.extend(f"{context['name']}: {b}" for b in report.get("bottlenecks") or [])
            all_supersaturation.extend(
                f"{context['name']}: {w}" for w in report.get("supersaturation_warnings") or []
            )
            tds = float(report.get("tds", {}).get("w_v_pct", 0.0) or 0.0)
            max_tds = max(max_tds, tds)
            salting_out = salting_out or bool(report.get("tds", {}).get("salting_out_flag"))

            check_by_name = {c["name"]: c for c in report.get("substances", [])}
            for ing in formula["ingredients"]:
                mapped_tuple = by_key.get(ing.key)
                if not mapped_tuple:
                    continue
                mapped, grams, concentration_note = mapped_tuple
                check = check_by_name.get(mapped)
                if not check:
                    continue
                undissolved = float(check.get("undissolved_g", 0.0) or 0.0)
                if grams > 0:
                    fraction = max(0.0, min(1.0, (grams - undissolved) / grams))
                    fractions[ing.key] = min(fractions.get(ing.key, 1.0), fraction)
                worst_fraction = min(worst_fraction, fractions.get(ing.key, 1.0))
                if fractions.get(ing.key, 1.0) < 0.999:
                    notes.append(
                        f"{ing.label}: only {fractions[ing.key] * 100:.1f}% dissolved at {concentration_note}"
                    )

        if unknown_physical:
            notes.extend("UNKNOWN solution solubility: " + item for item in unknown_physical)
            worst_fraction = 0.0

        aggregate_report: dict[str, Any] = {
            "contexts": reports,
            "tds": {"w_v_pct": round(max_tds, 4), "salting_out_flag": salting_out},
            "bottlenecks": all_bottlenecks,
            "supersaturation_warnings": all_supersaturation,
            "unknown_physical": unknown_physical,
        }
        if len(reports) == 1:
            # Preserve the old top-level shape for report consumers while adding
            # explicit context metadata.
            single = dict(reports[0])
            single.update({
                "contexts": reports,
                "unknown_physical": unknown_physical,
                "bottlenecks": all_bottlenecks,
                "supersaturation_warnings": all_supersaturation,
            })
            aggregate_report = single

        score = 10.0
        if unknown_physical:
            score = 4.0
        if all_bottlenecks:
            score = min(score, max(0.0, 4.0 * worst_fraction))
        elif salting_out:
            score = min(score, 7.0)
            notes.append("TDS >20% w/v: salting-out / crystallization risk")
        elif all_supersaturation:
            score = min(score, 8.0)
            notes.extend(all_supersaturation)
        return {"fractions": fractions, "report": aggregate_report, "score": round(score, 2), "notes": notes}
    except Exception as exc:
        return {"fractions": fractions, "report": {"warning": f"compat.solubility unavailable: {exc}"}, "score": 6.0, "notes": [f"solubility calculator unavailable: {exc}"]}


def osmolality_analysis(formula: dict[str, Any]) -> dict[str, Any]:
    try:
        load_physical_registry_overlays()
        from compat.osmolality import osmolality_report  # type: ignore

        components: list[tuple[str, float]] = []
        for ing in formula["ingredients"]:
            if not _is_solution_phase(ing.phase) or ing.unit != "mg":
                continue
            prof = PROFILES.get(ing.key)
            mapped = _compat_key(ing, prof)
            if mapped:
                components.append((mapped, ing.amount / 1000.0))
        if not components:
            return {"report": None, "score": 10.0, "hydration_cap": 10.0, "notes": []}
        water_ml = _wet_water_ml_per_dose(formula)
        report = osmolality_report(components, water_ml=water_ml)
        gate = report["ors_gate"]
        electro = report["electrolyte_balance"]
        mosm = float(gate["total_mosm_per_l"])
        verdict = gate["verdict"]
        notes = [f"{mosm:.0f} mOsm/L -> {verdict}: {gate['note']}"]
        unknown_mw = report.get("osmolarity", {}).get("unknown_molar_mass") or []
        if unknown_mw:
            notes.append("UNKNOWN osmoles for: " + ", ".join(unknown_mw) + " (molar mass missing in registry; osmolarity is under-estimated)")
        if not electro["complete_ors"]:
            notes.append(electro["reason"])
        from compat.scoring import score_osmolality_report  # type: ignore

        normalized = score_osmolality_report(report, hydration_claim=True)
        return {"report": report, "score": normalized["score"], "hydration_cap": normalized["hydration_cap"], "notes": notes}
    except Exception as exc:
        return {"report": {"warning": f"compat.osmolality unavailable: {exc}"}, "score": 5.0, "hydration_cap": 6.0, "notes": [f"osmolality calculator unavailable: {exc}"]}



def contribution_points(
    formula: dict[str, Any],
    solubility_fractions: dict[str, float] | None = None,
) -> tuple[dict[str, float], list[dict[str, Any]], list[str], dict[str, list[tuple[float, float]]]]:
    raw = {SHORT[m]: 0.0 for m in METRICS if SHORT[m] not in {"gi", "shelf"}}
    rows: list[dict[str, Any]] = []
    unknowns: list[str] = []
    confidence_inputs: dict[str, list[tuple[float, float]]] = {SHORT[m]: [] for m in METRICS}
    solubility_fractions = solubility_fractions or {}
    for ing in formula["ingredients"]:
        prof = PROFILES.get(ing.key)
        if not prof:
            unknowns.append(ing.key)
            rows.append({
                "ingredient": ing.label,
                "dose": f"{ing.amount:g} {ing.unit}",
                "phase": ing.phase,
                "evidence": "unknown",
                "dose_factor": 0.0,
                "solubility_factor": 1.0,
                "contribs": {},
                "notes": "UNKNOWN PROFILE — no score contribution; add via --profiles after safety/evidence review.",
            })
            continue
        ev = EVIDENCE_MULT.get(prof.evidence, 0.5)
        df = dose_factor(ing, prof)
        sf = solubility_fractions.get(ing.key, 1.0) if _is_solution_phase(ing.phase) else 1.0
        contribs = {}
        for metric, base in prof.effects.items():
            tf = timing_factor(metric, ing, prof)
            pts = base * df * ev * tf * sf
            raw[metric] = raw.get(metric, 0.0) + pts
            contribs[metric] = round(pts, 3)
            if pts > 0:
                confidence_inputs.setdefault(metric, []).append((pts, EVIDENCE_CONFIDENCE.get(prof.evidence, 0.35)))
                if sf < 0.999:
                    # Undissolved fraction lowers confidence as well as points.
                    confidence_inputs.setdefault(metric, []).append((pts * (1.0 - sf), 0.25))
        notes = prof.notes
        if sf < 0.999:
            notes += f" SOLUBILITY CAP: {sf * 100:.1f}% dissolved in declared solution phase."
        rows.append({
            "ingredient": ing.label,
            "dose": f"{ing.amount:g} {ing.unit}",
            "phase": ing.phase,
            "evidence": prof.evidence,
            "dose_factor": round(df, 3),
            "solubility_factor": round(sf, 3),
            "contribs": contribs,
            "notes": notes,
        })
    return raw, rows, unknowns, confidence_inputs


def raw_to_score(raw: float, scale: float = 3.0) -> float:
    return 10.0 * (1.0 - math.exp(-raw / scale))


def confidence_label(value: float) -> str:
    if value >= 0.82:
        return "High"
    if value >= 0.60:
        return "Medium"
    return "Low"


def metric_confidences(
    confidence_inputs: dict[str, list[tuple[float, float]]],
    scores: dict[str, float],
    physical: dict[str, Any],
) -> dict[str, str]:
    conf: dict[str, str] = {}
    for metric_name in METRICS:
        short = SHORT[metric_name]
        if short == "gi":
            base = 0.62
            if physical.get("gi", 0) < 6.5 or any("not validated" in n for n in physical.get("gi_notes", [])):
                base -= 0.12
        elif short == "shelf":
            base = 0.72
            if not physical.get("solubility"):
                base -= 0.05
            if physical.get("shelf", 0) < 7.0:
                base -= 0.12
            if any("not validated" in n for n in physical.get("shelf_notes", [])):
                base -= 0.12
        else:
            inputs = confidence_inputs.get(short, [])
            if not inputs or scores.get(metric_name, 0.0) <= 0.25:
                base = 0.25
            else:
                total_weight = sum(weight for weight, _ in inputs) or 1.0
                base = sum(weight * c for weight, c in inputs) / total_weight
            if short == "hydration" and physical.get("hydration_cap", 10.0) < 6.0:
                base -= 0.18
        conf[metric_name] = confidence_label(max(0.0, min(1.0, base)))
    return conf


def wet_risk_penalty(formula: dict[str, Any]) -> tuple[float, list[str]]:
    wet_classes: dict[str, list[str]] = {}
    for ing in formula["ingredients"]:
        prof = PROFILES.get(ing.key)
        if not prof or ing.phase != "wet" or not prof.wet_reactive_class:
            continue
        wet_classes.setdefault(prof.wet_reactive_class, []).append(ing.label)

    penalties = 0.0
    notes: list[str] = []
    has_sugar = "reducing_sugar" in wet_classes
    if has_sugar and "primary_amine" in wet_classes:
        penalties += 1.4
        notes.append("wet reducing sugar + primary amine Maillard/browning risk")
    if has_sugar and "vitamin" in wet_classes:
        penalties += 0.8
        notes.append("wet reducing sugar + vitamin potency/browning risk")
    if has_sugar and "redox" in wet_classes:
        penalties += 0.9
        notes.append("wet ribose + ascorbate/redox shelf risk")
    if "redox" in wet_classes and "thiol" in wet_classes:
        penalties += 0.8
        notes.append("wet redox + thiol risk")
    return penalties, notes


def physical_scores(formula: dict[str, Any]) -> dict[str, Any]:
    oil_pct = float(formula.get("oil_pct", 0.0))
    mct_ml = sum(i.amount for i in formula["ingredients"] if i.key == "mct_oil")
    mg_mg = sum(i.amount for i in formula["ingredients"] if i.key == "magnesium_chloride")
    ledger: list[dict[str, Any]] = []

    # GI score: starts high, penalties for oil burden, Mg, and concentrated/emulsion uncertainty.
    gi = 8.0
    gi_notes: list[str] = []
    if mct_ml > 1.0:
        penalty = min(2.2, (mct_ml - 1.0) * 1.4)
        gi -= penalty
        gi_notes.append(f"MCT {mct_ml:g} mL/dose adds oil/GI burden")
        ledger.append({"target": "GI", "delta": -round(penalty, 2), "reason": "MCT oil burden"})
    if mg_mg > 75:
        gi -= 0.7
        gi_notes.append("Mg dose may affect droppings/GI tolerance")
        ledger.append({"target": "GI", "delta": -0.7, "reason": "Mg dose droppings/GI risk"})
    if oil_pct >= 30:
        gi -= 0.8
        gi_notes.append("high-oil emulsion burden")
        ledger.append({"target": "GI", "delta": -0.8, "reason": "high-oil emulsion burden"})
    elif oil_pct >= 20:
        gi -= 0.35
        gi_notes.append("moderate oil emulsion burden")
        ledger.append({"target": "GI", "delta": -0.35, "reason": "moderate oil emulsion burden"})
    if not formula.get("emulsion_validated", False) and oil_pct > 0:
        gi -= 0.4
        gi_notes.append("emulsion not validated")
        ledger.append({"target": "GI", "delta": -0.4, "reason": "emulsion not validated"})

    # Shelf score: deterministic gate, not effect contribution.
    shelf = 9.0
    shelf_notes: list[str] = []
    if formula.get("target_shelf_months", 0) >= 6:
        shelf_notes.append("6+ month target active")
    wrp, wr_notes = wet_risk_penalty(formula)
    shelf -= wrp
    shelf_notes.extend(wr_notes)
    if wrp:
        ledger.append({"target": "Shelf", "delta": -round(wrp, 2), "reason": "; ".join(wr_notes)})
    if oil_pct > 0:
        if oil_pct > 20:
            oil_pen = 0.6 + (oil_pct - 20) / 10 * 0.5
        else:
            oil_pen = 0.45
        shelf -= oil_pen
        shelf_notes.append(f"{oil_pct:g}% oil emulsion needs separation/oxidation testing")
        ledger.append({"target": "Shelf", "delta": -round(oil_pen, 2), "reason": f"{oil_pct:g}% oil emulsion risk"})
    if not formula.get("emulsion_validated", False) and oil_pct > 0:
        shelf -= 0.8
        shelf_notes.append("emulsion stability not validated")
        ledger.append({"target": "Shelf", "delta": -0.8, "reason": "emulsion stability not validated"})
    if not formula.get("preservative_validated", False):
        shelf -= 0.8
        shelf_notes.append("preservative challenge not validated")
        ledger.append({"target": "Shelf", "delta": -0.8, "reason": "preservative challenge not validated"})
    if formula.get("architecture") == "wet_core_plus_dry_activator":
        shelf += 0.8
        shelf_notes.append("dry activator removes high-risk wet amines/vitamins")
        ledger.append({"target": "Shelf", "delta": 0.8, "reason": "dry activator removes wet incompatibilities"})
    if any(i.key in {"coq10", "vitamin_e_acetate"} for i in formula["ingredients"]):
        shelf -= 0.3
        shelf_notes.append("oil-phase actives need potency/distribution assay")
        ledger.append({"target": "Shelf", "delta": -0.3, "reason": "oil-phase active distribution assay needed"})

    sol = solubility_analysis(formula)
    solubility = sol["report"]
    if sol.get("score", 10.0) < 10.0:
        reason = "; ".join(sol.get("notes") or []) or "solution solubility/TDS risk"
        shelf_notes.extend(sol.get("notes") or [])
        unknown_physical = sol.get("report", {}).get("unknown_physical") if isinstance(sol.get("report"), dict) else []
        bottlenecks = sol.get("report", {}).get("bottlenecks") if isinstance(sol.get("report"), dict) else []
        if unknown_physical:
            shelf -= 1.2
            gi -= 0.8
            shelf_notes.append("solution solubility profile missing: " + "; ".join(unknown_physical))
            ledger.append({"target": "Shelf", "delta": -1.2, "reason": "unknown solution solubility profile"})
            ledger.append({"target": "GI", "delta": -0.8, "reason": "unknown solution solubility/delivery"})
        elif bottlenecks:
            shelf -= 1.2
            gi -= 0.8
            shelf_notes.append("solution solubility bottleneck(s): " + "; ".join(bottlenecks))
            ledger.append({"target": "Shelf", "delta": -1.2, "reason": "solution solubility bottleneck"})
            ledger.append({"target": "GI", "delta": -0.8, "reason": "undissolved solution solids"})
        else:
            shelf -= 0.3
            ledger.append({"target": "Shelf", "delta": -0.3, "reason": reason[:160]})

    osmo = osmolality_analysis(formula)
    if osmo.get("score", 10.0) < 9.0:
        for note in osmo.get("notes", []):
            ledger.append({"target": "Hydration cap", "delta": f"cap {osmo['hydration_cap']}", "reason": note})

    normalized_report = None
    try:
        from compat.scoring import evaluate_formula  # type: ignore

        product_type = "wet_core_plus_dry_activator" if formula.get("architecture") == "wet_core_plus_dry_activator" else "wet_concentrate"
        normalized_report = evaluate_formula(
            [],
            product_type=product_type,
            water_ml=_wet_water_ml_per_dose(formula),
            hydration_claim=bool(osmo.get("report")),
            preservative_validated=bool(formula.get("preservative_validated", False)),
            emulsion_validated=bool(formula.get("emulsion_validated", False)) if oil_pct > 0 else None,
            solubility_report=solubility,
            osmolality_report_data=osmo["report"],
        )
    except Exception as exc:
        normalized_report = {"warning": f"compat.scoring unavailable: {exc}"}

    return {
        "gi": round(clamp(gi), 2),
        "gi_notes": gi_notes,
        "shelf": round(clamp(shelf), 2),
        "shelf_notes": shelf_notes,
        "solubility": solubility,
        "solubility_score": sol["score"],
        "solubility_fractions": sol["fractions"],
        "solubility_notes": sol["notes"],
        "osmolality": osmo["report"],
        "osmolality_score": osmo["score"],
        "hydration_cap": osmo["hydration_cap"],
        "osmolality_notes": osmo["notes"],
        "normalized_compat_report": normalized_report,
        "penalty_ledger": ledger,
    }


def score_formula(formula: dict[str, Any]) -> dict[str, Any]:
    physical = physical_scores(formula)
    raw, rows, unknowns, confidence_inputs = contribution_points(
        formula,
        physical.get("solubility_fractions", {}),
    )
    scores: dict[str, float] = {}
    potential_scores: dict[str, float] = {}
    score_notes: dict[str, list[str]] = {}
    cap_notes: dict[str, list[str]] = {}

    for metric_name in METRICS:
        short = SHORT[metric_name]
        if short == "gi":
            scores[metric_name] = physical["gi"]
            potential_scores[metric_name] = 8.0
            score_notes[metric_name] = physical["gi_notes"]
        elif short == "shelf":
            scores[metric_name] = physical["shelf"]
            potential_scores[metric_name] = 9.0
            score_notes[metric_name] = physical["shelf_notes"]
        else:
            potential = round(clamp(raw_to_score(raw.get(short, 0.0))), 2)
            potential_scores[metric_name] = potential
            final = potential
            if short == "hydration":
                cap = float(physical.get("hydration_cap", 10.0))
                if potential > cap:
                    final = cap
                    cap_notes[metric_name] = [f"hydration capped at {cap:.2f} by osmolality/electrolyte gate"]
            scores[metric_name] = round(clamp(final), 2)
            score_notes[metric_name] = []
        if metric_name in cap_notes:
            score_notes[metric_name].extend(cap_notes[metric_name])

    performance = sum(scores[m] for m in METRICS[:4]) / 4
    recovery = sum(scores[m] for m in [
        "Fast recovery",
        "Anti-inflammatory / antioxidant support",
        "Respiratory / acid-base support",
        "Hydration / electrolyte balance",
        "GI tolerance",
    ]) / 5
    overall = sum(scores.values()) / len(scores)
    bio_metrics = [m for m in METRICS if SHORT[m] not in {"gi", "shelf"}]
    biological_potential = sum(potential_scores[m] for m in bio_metrics) / len(bio_metrics)
    feasibility_parts = [
        float(physical.get("solubility_score", 6.0)),
        float(physical.get("osmolality_score", 5.0)),
        float(physical.get("gi", 0.0)),
        float(physical.get("shelf", 0.0)),
    ]
    formulation_feasibility = sum(feasibility_parts) / len(feasibility_parts)
    confidences = metric_confidences(confidence_inputs, scores, physical)

    return {
        "name": formula["name"],
        "architecture": formula["architecture"],
        "scores": scores,
        "potential_scores": potential_scores,
        "overall": round(overall, 2),
        "biological_potential": round(biological_potential, 2),
        "formulation_feasibility": round(formulation_feasibility, 2),
        "rollups": {
            "performance_support": round(performance, 2),
            "recovery_welfare": round(recovery, 2),
            "commercial_readiness": scores["Shelf stability / commercial readiness"],
        },
        "confidence": confidences,
        "ingredient_rows": rows,
        "unknown_ingredients": unknowns,
        "raw_points": {k: round(v, 3) for k, v in raw.items()},
        "physical": physical,
        "score_notes": score_notes,
    }


def md_report(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Calculated Formula Stats Card",
        "",
        "> v0.2 calculation: deterministic expert-scoring from ingredient dose profiles + evidence multipliers + physical-chemistry gates. Scores are comparable estimates, not proof of efficacy.",
        "",
        "## Model layers",
        "",
        "- **Biological potential**: what the active profile could do before delivery/stability caps.",
        "- **Formulation feasibility**: solubility + osmolality + GI/emulsion + shelf-readiness gate score.",
        "- **Final deliverable score**: the score after physical caps/penalties.",
        "",
        "## Score comparison",
        "",
        "| Metric | " + " | ".join(r["name"] for r in results) + " |",
        "|---|" + "|".join(["---:"] * len(results)) + "|",
    ]
    for metric in METRICS:
        lines.append("| " + metric + " | " + " | ".join(f"{r['scores'][metric]:.2f}" for r in results) + " |")
    lines += [
        "| **Overall average** | " + " | ".join(f"**{r['overall']:.2f}**" for r in results) + " |",
        "",
        "## Layer comparison",
        "",
        "| Formula | Biological potential | Formulation feasibility | Final deliverable average |",
        "|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['name']} | {r['biological_potential']:.2f} | "
            f"{r['formulation_feasibility']:.2f} | {r['overall']:.2f} |"
        )
    lines += [
        "",
        "## Rollups",
        "",
        "| Formula | Performance support | Recovery/welfare | Commercial readiness |",
        "|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['name']} | {r['rollups']['performance_support']:.2f} | "
            f"{r['rollups']['recovery_welfare']:.2f} | {r['rollups']['commercial_readiness']:.2f} |"
        )
    for r in results:
        lines += [
            "",
            f"## {r['name']} — calculation notes",
            "",
            f"- Architecture: `{r['architecture']}`",
            f"- Final deliverable overall: **{r['overall']:.2f}/10**",
            f"- Biological potential: **{r['biological_potential']:.2f}/10**",
            f"- Formulation feasibility: **{r['formulation_feasibility']:.2f}/10**",
            f"- Raw contribution points: `{json.dumps(r['raw_points'], sort_keys=True)}`",
        ]
        if r.get("unknown_ingredients"):
            lines.append(
                "- Unknown/unscored ingredients: "
                + ", ".join(f"`{x}`" for x in r["unknown_ingredients"])
                + " — add a profile JSON with `--profiles`."
            )
        lines += [
            "",
            "### Physical chemistry gate",
            "",
            "| Gate | Result | Score / cap |",
            "|---|---|---:|",
        ]
        phys = r["physical"]
        sol = phys.get("solubility")
        if isinstance(sol, dict) and "tds" in sol:
            bottlenecks = sol.get("bottlenecks") or []
            sol_result = "FAIL" if bottlenecks else ("TIGHT" if sol.get("tds", {}).get("salting_out_flag") else "PASS")
            lines.append(f"| Solubility/TDS | {sol_result}; TDS {sol['tds']['w_v_pct']:.2f}% w/v | {phys.get('solubility_score', 0):.2f} |")
        elif isinstance(sol, dict) and "warning" in sol:
            lines.append(f"| Solubility/TDS | UNKNOWN — {sol['warning']} | {phys.get('solubility_score', 0):.2f} |")
        else:
            lines.append(f"| Solubility/TDS | n/a | {phys.get('solubility_score', 0):.2f} |")
        osmo = phys.get("osmolality")
        if isinstance(osmo, dict) and "ors_gate" in osmo:
            gate = osmo["ors_gate"]
            lines.append(
                f"| Osmolality / ORS | {gate['total_mosm_per_l']:.0f} mOsm/L → {gate['verdict']} | "
                f"hydration cap {phys.get('hydration_cap', 10):.2f} |"
            )
        elif isinstance(osmo, dict) and "warning" in osmo:
            lines.append(f"| Osmolality / ORS | UNKNOWN — {osmo['warning']} | hydration cap {phys.get('hydration_cap', 10):.2f} |")
        else:
            lines.append(f"| Osmolality / ORS | n/a | hydration cap {phys.get('hydration_cap', 10):.2f} |")
        lines.append(f"| GI / emulsion burden | see notes | {phys['gi']:.2f} |")
        lines.append(f"| Shelf / commercial readiness | see notes | {phys['shelf']:.2f} |")

        lines += [
            "",
            "### Penalty / cap ledger",
            "",
        ]
        if phys.get("penalty_ledger"):
            lines += ["| Target | Delta / cap | Reason |", "|---|---:|---|"]
            for item in phys["penalty_ledger"]:
                lines.append(f"| {item['target']} | {item['delta']} | {item['reason']} |")
        else:
            lines.append("- No physical penalties/caps recorded.")

        lines += [
            "",
            "### Physical gate notes",
        ]
        for note in r["physical"].get("gi_notes", []):
            lines.append(f"- GI: {note}")
        for note in r["physical"].get("shelf_notes", []):
            lines.append(f"- Shelf: {note}")
        for note in r["physical"].get("osmolality_notes", []):
            lines.append(f"- Osmolality: {note}")
        sol = r["physical"].get("solubility")
        if isinstance(sol, dict):
            bottlenecks = sol.get("bottlenecks") or []
            if bottlenecks:
                for b in bottlenecks:
                    lines.append(f"- Solubility bottleneck: {b}")
            elif "tds" in sol:
                lines.append(
                    f"- Solubility: no bottlenecks; TDS {sol['tds']['w_v_pct']:.2f}% w/v"
                )
        lines += [
            "",
            "### Metric confidence",
            "",
            "| Metric | Final score | Biological potential | Confidence | Notes |",
            "|---|---:|---:|---|---|",
        ]
        for metric in METRICS:
            notes = "; ".join(r["score_notes"].get(metric, []))
            lines.append(
                f"| {metric} | {r['scores'][metric]:.2f} | "
                f"{r['potential_scores'][metric]:.2f} | {r['confidence'][metric]} | {notes} |"
            )
        lines += [
            "",
            "### Ingredient contribution rows",
            "",
            "| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |",
            "|---|---:|---|---|---:|---:|---|---|",
        ]
        for row in r["ingredient_rows"]:
            contrib = ", ".join(f"{k}:{v}" for k, v in row["contribs"].items())
            lines.append(
                f"| {row['ingredient']} | {row['dose']} | {row['phase']} | "
                f"{row['evidence']} | {row['dose_factor']:.2f} | {row['solubility_factor']:.2f} | "
                f"{contrib} | {row['notes']} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", action="append", choices=sorted(PRESETS), help="Preset formula; repeatable")
    ap.add_argument("--json-in", help="Custom formula JSON file")
    ap.add_argument("--profiles", action="append", help="External substance profile JSON; repeatable")
    ap.add_argument("--out", default="calculated-stats-card.md")
    ap.add_argument("--json-out", help="Optional JSON result path")
    args = ap.parse_args()

    if args.profiles:
        for profile_path in args.profiles:
            PROFILES.update(load_profile_file(profile_path))

    formulas: list[dict[str, Any]] = []
    if args.preset:
        formulas.extend(PRESETS[p] for p in args.preset)
    if args.json_in:
        raw = json.loads(Path(args.json_in).read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "ingredients" in raw:
            # JSON custom ingredients must be dicts; convert to Ingredient.
            raw = dict(raw)
            raw["ingredients"] = [Ingredient(**i) if isinstance(i, dict) else i for i in raw["ingredients"]]
            formulas.append(raw)
        elif isinstance(raw, list):
            for f in raw:
                f = dict(f)
                f["ingredients"] = [Ingredient(**i) if isinstance(i, dict) else i for i in f["ingredients"]]
                formulas.append(f)
    if not formulas:
        formulas = [PRESETS["route_a"], PRESETS["v3_hybrid"]]

    results = [score_formula(f) for f in formulas]
    Path(args.out).write_text(md_report(results), encoding="utf-8")
    if args.json_out:
        # Convert any non-JSON dataclass remnants defensively.
        Path(args.json_out).write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(Path(args.out).resolve())


if __name__ == "__main__":
    main()
