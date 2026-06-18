#!/usr/bin/env python3
"""Audit stats-card registries for field-level provenance.

Reviewed/verified records must carry source refs beside the values that the
calculator can use. Draft records may keep empty refs because they are not
allowed to create benefit points.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_STATUSES = {"reviewed", "verified"}
INACTIVE_STATUSES = {"draft", "rejected", "blocked"}


def load_json_files(paths: list[Path]) -> dict[str, tuple[dict[str, Any], Path]]:
    records: dict[str, tuple[dict[str, Any], Path]] = {}
    for root in paths:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError(f"{path} must contain a JSON object")
            if "key" in raw or "compat_key" in raw:
                key = str(raw.get("key") or raw.get("compat_key"))
                records[key] = (raw, path)
            else:
                for key, rec in raw.items():
                    if isinstance(rec, dict):
                        records[str(key)] = (rec, path)
    return records


def is_active(rec: dict[str, Any]) -> bool:
    return str(rec.get("review_status", "draft")).lower() in ACTIVE_STATUSES


def has_refs(refs: Any) -> bool:
    if isinstance(refs, list):
        return any(bool(x) for x in refs)
    if isinstance(refs, dict):
        return any(has_refs(v) for v in refs.values())
    return bool(refs)


def effect_errors(key: str, rec: dict[str, Any], path: Path) -> list[str]:
    if not is_active(rec):
        return []
    errs: list[str] = []
    srefs = rec.get("source_refs")
    if not isinstance(srefs, dict):
        return [f"effects:{key} ({path}): missing source_refs object"]
    if not rec.get("source_wiki"):
        errs.append(f"effects:{key} ({path}): missing source_wiki")
    for field in ["ref", "evidence", "chronic_only", "notes"]:
        if field in rec and rec.get(field) not in (None, "", [], {}):
            if not has_refs(srefs.get(field)):
                errs.append(f"effects:{key} ({path}): missing source_refs.{field}")
    if rec.get("wet_reactive_class") is not None and not has_refs(srefs.get("wet_reactive_class")):
        errs.append(f"effects:{key} ({path}): missing source_refs.wet_reactive_class")
    effects = rec.get("effects", {})
    effect_refs = srefs.get("effects")
    if not isinstance(effect_refs, dict):
        errs.append(f"effects:{key} ({path}): missing source_refs.effects object")
    else:
        for metric, value in effects.items():
            if value not in (None, 0, 0.0) and not has_refs(effect_refs.get(metric)):
                errs.append(f"effects:{key} ({path}): missing source_refs.effects.{metric}")
    return errs


def physical_errors(key: str, rec: dict[str, Any], path: Path) -> list[str]:
    if not is_active(rec):
        return []
    errs: list[str] = []
    srefs = rec.get("source_refs")
    if not isinstance(srefs, dict):
        return [f"physical:{key} ({path}): missing source_refs object"]
    if not rec.get("source_wiki"):
        errs.append(f"physical:{key} ({path}): missing source_wiki")
    scalar_fields = [
        "formula",
        "molar_mass_g_per_mol",
        "osmotic_n",
        "solubility_g_per_100ml_25c",
        "density_kg_m3",
        "wet_reactive_class_hint",
        "note",
    ]
    for field in scalar_fields:
        if field in rec and rec.get(field) not in (None, "", [], {}):
            if not has_refs(srefs.get(field)):
                errs.append(f"physical:{key} ({path}): missing source_refs.{field}")
    if rec.get("pka") not in (None, [], {}):
        if not has_refs(srefs.get("pka")):
            errs.append(f"physical:{key} ({path}): missing source_refs.pka")
    ions = rec.get("ions_mmol_per_g")
    if isinstance(ions, dict) and ions:
        ion_refs = srefs.get("ions_mmol_per_g")
        if isinstance(ion_refs, dict):
            for ion, value in ions.items():
                if value not in (None, 0, 0.0) and not has_refs(ion_refs.get(ion)):
                    errs.append(f"physical:{key} ({path}): missing source_refs.ions_mmol_per_g.{ion}")
        elif not has_refs(ion_refs):
            errs.append(f"physical:{key} ({path}): missing source_refs.ions_mmol_per_g")
    return errs




def calculator_compat_keys() -> set[str]:
    """Compat keys explicitly required by the calculator mapping."""
    calc_path = SKILL_ROOT / "scripts" / "calculated_stats_card.py"
    try:
        tree = ast.parse(calc_path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "COMPAT_KEY_MAP" for t in node.targets):
                try:
                    mapping = ast.literal_eval(node.value)
                except Exception:
                    return set()
                if isinstance(mapping, dict):
                    return {str(v) for v in mapping.values() if v}
    return set()


def active_profile_compat_keys(effects: dict[str, tuple[dict[str, Any], Path]]) -> set[str]:
    keys: set[str] = set()
    for rec, _path in (item for item in effects.values()):
        if is_active(rec) and rec.get("solubility_key"):
            keys.add(str(rec["solubility_key"]))
    return keys

def compat_expected_keys(project_root: Path) -> set[str]:
    sys.path.insert(0, str(project_root))
    try:
        from compat import data as compat_data  # type: ignore
    except Exception:
        return set()
    return set(compat_data.SUBSTANCES) | set(compat_data.MOLAR_MASS_G_PER_MOL) | set(compat_data.OSMOTIC_N) | set(compat_data.ELECTROLYTE_IONS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    effect_roots = [SKILL_ROOT / "registry" / "effects", project_root / "substances" / "effects"]
    physical_roots = [SKILL_ROOT / "registry" / "physical", project_root / "substances" / "physical"]
    effects = load_json_files(effect_roots)
    physical = load_json_files(physical_roots)

    errors: list[str] = []
    for key, (rec, path) in sorted(effects.items()):
        errors.extend(effect_errors(key, rec, path))
    for key, (rec, path) in sorted(physical.items()):
        errors.extend(physical_errors(key, rec, path))

    expected = compat_expected_keys(project_root) | calculator_compat_keys() | active_profile_compat_keys(effects)
    physical_keys = set(physical) | {str(rec.get("compat_key")) for rec, _path in physical.values() if rec.get("compat_key")}
    missing_physical_records = sorted(k for k in expected if k not in physical_keys)
    for key in missing_physical_records:
        errors.append(f"physical:{key}: compat key has no physical registry record")

    report = {
        "effect_records": len(effects),
        "physical_records": len(physical),
        "compat_expected_physical_records": len(expected),
        "errors": errors,
        "ok": not errors,
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if errors:
            print("PROVENANCE AUDIT FAILED")
            for err in errors:
                print(f"- {err}")
        else:
            print(
                f"PROVENANCE AUDIT PASS: {len(effects)} effect records, "
                f"{len(physical)} physical records, {len(expected)} compat keys covered"
            )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
