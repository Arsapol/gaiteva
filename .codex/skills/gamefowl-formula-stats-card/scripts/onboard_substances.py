#!/usr/bin/env python3
"""Detect unknown substances in formula JSON and create draft registry records.

This script does NOT invent physical constants or biological effects.  It writes
review-gated draft JSON files that the agent must fill after formula-safety-check
research and independent verification.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Make calculated_stats_card importable from the same scripts directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import calculated_stats_card as calc  # noqa: E402


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "unknown_substance"


def load_formulas(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "ingredients" in raw:
        return [raw]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict) and "ingredients" in x]
    raise ValueError("formula JSON must be a formula object or list of formula objects")


def effect_template(key: str, label: str) -> dict[str, Any]:
    return {
        key: {
            "ref": 100,
            "unit": "mg",
            "evidence": "unknown",
            "effects": {
                "focus": 0.0,
                "energy": 0.0,
                "fatigue": 0.0,
                "recovery": 0.0,
                "atp": 0.0,
                "antiox": 0.0,
                "resp": 0.0,
                "hydration": 0.0,
                "onset": 0.0,
            },
            "chronic_only": False,
            "wet_reactive_class": None,
            "solubility_key": key,
            "notes": f"DRAFT for {label}. Fill only after formula-safety-check dossier + verifier review.",
            "review_status": "draft",
            "source_wiki": None,
            "sources": [
                {
                    "id": "wiki:new-substance-dossier",
                    "type": "dossier",
                    "path": None,
                    "note": "Replace with omx_wiki/substance-*.md after formula-safety-check research.",
                },
                {
                    "id": "rubric:stats-card-v0.2",
                    "type": "scoring-model",
                    "path": "references/rubric.md",
                    "note": "Effect numbers are rubric-calibrated contribution points, not published efficacy constants.",
                },
            ],
            "source_refs": {
                "ref": ["wiki:new-substance-dossier", "rubric:stats-card-v0.2"],
                "evidence": ["wiki:new-substance-dossier"],
                "effects": {m: ["wiki:new-substance-dossier", "rubric:stats-card-v0.2"] for m in [
                    "focus", "energy", "fatigue", "recovery", "atp", "antiox", "resp", "hydration", "onset"
                ]},
                "chronic_only": ["wiki:new-substance-dossier"],
                "wet_reactive_class": ["wiki:new-substance-dossier"],
                "solubility_key": ["wiki:new-substance-dossier"],
                "notes": ["wiki:new-substance-dossier"],
            },
            "required_research": [
                "avian/poultry evidence and dose relevance",
                "acute vs preload timing",
                "mechanism boundaries and no pain-tolerance claims",
            ],
        }
    }


def physical_template(key: str, label: str) -> dict[str, Any]:
    return {
        key: {
            "key": key,
            "compat_key": key,
            "name": label,
            "formula": "UNKNOWN",
            "molar_mass_g_per_mol": None,
            "osmotic_n": None,
            "solubility_g_per_100ml_25c": None,
            "density_kg_m3": None,
            "pka": [],
            "ions_mmol_per_g": {},
            "wet_reactive_class_hint": None,
            "review_status": "draft",
            "source_wiki": None,
            "sources": [
                {
                    "id": "wiki:new-substance-dossier",
                    "type": "dossier",
                    "path": None,
                    "note": "Replace with omx_wiki/substance-*.md after formula-safety-check research.",
                },
                {
                    "id": "calc:ion-stoichiometry-from-mw",
                    "type": "calculation-method",
                    "note": "Ion mmol/g is calculated as ion count * 1000 / molar_mass_g_per_mol.",
                },
                {
                    "id": "osmotic-model:screening-v0.2",
                    "type": "calculation-method",
                    "note": "Osmotic_n is a screening dissociation-particle count at formula pH, not a measured osmolality.",
                },
            ],
            "source_refs": {
                "formula": ["wiki:new-substance-dossier"],
                "molar_mass_g_per_mol": ["wiki:new-substance-dossier"],
                "osmotic_n": ["wiki:new-substance-dossier", "osmotic-model:screening-v0.2"],
                "solubility_g_per_100ml_25c": ["wiki:new-substance-dossier"],
                "density_kg_m3": ["wiki:new-substance-dossier"],
                "pka": ["wiki:new-substance-dossier"],
                "ions_mmol_per_g": ["wiki:new-substance-dossier", "calc:ion-stoichiometry-from-mw"],
                "wet_reactive_class_hint": ["wiki:new-substance-dossier"],
                "note": ["wiki:new-substance-dossier"],
            },
            "required_research": [
                "CAS/form/salt/hydrate identity",
                "molar mass on salt-as-weighed basis",
                "aqueous solubility at ~25C",
                "osmotic particle count at formula pH",
                "electrolyte ion mmol/g if salt",
                "pH/stability/degradation in water",
                "compatibility conflicts: precipitation, redox, Maillard, pH, DEB",
            ],
            "note": "DRAFT — do not use for scoring until reviewed/verified.",
        }
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-in", required=True, help="Formula JSON object or list")
    ap.add_argument("--out-dir", default="substances", help="Registry root to write draft files")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    formulas = load_formulas(Path(args.json_in))
    out = Path(args.out_dir)
    effects_dir = out / "effects"
    physical_dir = out / "physical"
    effects_dir.mkdir(parents=True, exist_ok=True)
    physical_dir.mkdir(parents=True, exist_ok=True)

    unknown_effects: dict[str, str] = {}
    unknown_physical: dict[str, str] = {}

    for formula in formulas:
        for ing in formula.get("ingredients", []):
            key = str(ing.get("key") or slug(str(ing.get("label", "unknown"))))
            label = str(ing.get("label") or key)
            phase = str(ing.get("phase", "wet"))
            if key not in calc.PROFILES:
                unknown_effects[key] = label
            prof = calc.PROFILES.get(key)
            compat_key = (prof.solubility_key if prof else None) or calc.COMPAT_KEY_MAP.get(key) or key
            if phase in {"wet", "drink", "make_fresh"}:
                # Unknown unless project/skill physical registry or compat.data has enough constants.
                try:
                    calc.load_physical_registry_overlays()
                    from compat import data as compat_data  # type: ignore
                    has_physical = (
                        compat_key in compat_data.SUBSTANCES
                        and compat_key in compat_data.MOLAR_MASS_G_PER_MOL
                        and compat_key in compat_data.OSMOTIC_N
                    )
                except Exception:
                    has_physical = False
                if not has_physical:
                    unknown_physical[compat_key] = label

    written: list[str] = []
    for key, label in unknown_effects.items():
        path = effects_dir / f"{slug(key)}.json"
        if args.overwrite or not path.exists():
            path.write_text(json.dumps(effect_template(key, label), indent=2, sort_keys=True), encoding="utf-8")
            written.append(str(path))
    for key, label in unknown_physical.items():
        path = physical_dir / f"{slug(key)}.json"
        if args.overwrite or not path.exists():
            path.write_text(json.dumps(physical_template(key, label), indent=2, sort_keys=True), encoding="utf-8")
            written.append(str(path))

    print(json.dumps({
        "unknown_effect_profiles": unknown_effects,
        "unknown_physical_profiles": unknown_physical,
        "written": written,
        "next_step": "Research each draft with formula-safety-check, fill field-level source_refs, run audit_provenance.py, verify, then change review_status to reviewed/verified.",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
