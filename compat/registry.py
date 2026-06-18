"""Validated physical-constants registry loader for compat calculators.

The compatibility package still exposes legacy module-level dictionaries from
``compat.data`` for backward compatibility.  This module is the transition
point toward a canonical ``substances/physical/*.json`` registry: it resolves
registry files independent of process CWD, validates the subset of schema the
current calculators consume, and returns explicit diagnostics instead of
silently swallowing malformed active records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable

ACTIVE_STATUSES = frozenset({"verified", "reviewed"})
DRAFT_STATUSES = frozenset({"draft"})
BLOCKED_STATUSES = frozenset({"blocked", "rejected"})
_REQUIRED_FIELDS = (
    "compat_key",
    "key",
    "name",
    "molar_mass_g_per_mol",
    "osmotic_n",
    "review_status",
    "sources",
    "source_refs",
)
_SOURCE_REF_FIELDS = (
    "formula",
    "molar_mass_g_per_mol",
    "osmotic_n",
    "solubility_g_per_100ml_25c",
    "note",
)


@dataclass(frozen=True)
class RegistryDiagnostic:
    """One loader/schema/drift diagnostic."""

    level: str
    path: str
    key: str
    message: str


@dataclass(frozen=True)
class RegistryRecord:
    """Validated physical registry record used by current compat gates."""

    key: str
    source_key: str
    path: Path
    data: dict[str, Any]
    override_of: str | None = None


@dataclass(frozen=True)
class PhysicalRegistry:
    """Loaded registry plus validation diagnostics and load-order provenance."""

    records: dict[str, RegistryRecord]
    diagnostics: tuple[RegistryDiagnostic, ...] = field(default_factory=tuple)
    load_order: tuple[str, ...] = field(default_factory=tuple)

    def active_errors(self) -> list[RegistryDiagnostic]:
        return [d for d in self.diagnostics if d.level == "error"]

    def report(self) -> dict[str, Any]:
        """Return a JSON-serialisable provenance/schema summary."""
        missing_fields: dict[str, list[str]] = {}
        for key, record in self.records.items():
            refs = record.data.get("source_refs") or {}
            missing = [name for name in _SOURCE_REF_FIELDS if _missing_source_ref(refs.get(name))]
            if missing:
                missing_fields[key] = missing
        return {
            "record_count": len(self.records),
            "records": sorted(self.records),
            "load_order": list(self.load_order),
            "diagnostics": [d.__dict__ for d in self.diagnostics],
            "missing_source_refs": missing_fields,
        }


def project_root() -> Path:
    """Resolve the repository root relative to this module, not process CWD."""
    return Path(__file__).resolve().parents[1]


def default_registry_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / "substances" / "physical"


def load_physical_registry(
    registry_dir: str | Path | None = None,
    *,
    allow_draft: bool = False,
    strict: bool = False,
) -> PhysicalRegistry:
    """Load and validate ``substances/physical/*.json`` records.

    Parameters
    ----------
    registry_dir:
        Explicit registry directory.  Defaults to the repo-local
        ``substances/physical`` regardless of the caller's current directory.
    allow_draft:
        Include ``review_status=draft`` records for research mode.  Production
        default is verified/reviewed only.
    strict:
        Raise ``ValueError`` if active records have schema errors.
    """
    root = Path(registry_dir) if registry_dir is not None else default_registry_dir()
    diagnostics: list[RegistryDiagnostic] = []
    records: dict[str, RegistryRecord] = {}
    load_order: list[str] = []

    if not root.exists():
        msg = f"physical registry directory not found: {root}"
        diagnostics.append(RegistryDiagnostic("error", str(root), "", msg))
        if strict:
            raise ValueError(msg)
        return PhysicalRegistry({}, tuple(diagnostics), ())

    for path in sorted(root.glob("*.json")):
        if path.name == "schema.json":
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            diagnostics.append(RegistryDiagnostic("error", str(path), "", f"invalid JSON: {exc}"))
            continue
        except OSError as exc:
            diagnostics.append(RegistryDiagnostic("error", str(path), "", f"cannot read: {exc}"))
            continue

        for source_key, rec in _iter_records(raw):
            if not isinstance(rec, dict):
                diagnostics.append(RegistryDiagnostic("error", str(path), str(source_key), "record is not an object"))
                continue
            status = str(rec.get("review_status", "draft")).lower()
            if status in BLOCKED_STATUSES:
                diagnostics.append(RegistryDiagnostic("info", str(path), str(source_key), f"skipped {status} record"))
                continue
            if status in DRAFT_STATUSES and not allow_draft:
                diagnostics.append(RegistryDiagnostic("info", str(path), str(source_key), "skipped draft record in verified-only mode"))
                continue
            key = str(rec.get("compat_key") or rec.get("key") or "").strip()
            if not key:
                diagnostics.append(RegistryDiagnostic("error", str(path), str(source_key), "missing compat_key/key"))
                continue
            rec_errors = _validate_record(rec, path, key, require_source_refs=status in ACTIVE_STATUSES)
            diagnostics.extend(rec_errors)
            if rec_errors:
                continue
            override_of = None
            if key in records:
                override_of = records[key].source_key
                if not rec.get("overrides"):
                    diagnostics.append(
                        RegistryDiagnostic(
                            "warning",
                            str(path),
                            key,
                            f"duplicate compat_key overrides {override_of} without explicit overrides metadata",
                        )
                    )
            records[key] = RegistryRecord(key=key, source_key=str(source_key), path=path, data=rec, override_of=override_of)
            load_order.append(f"{path.name}:{source_key}->{key}")

    registry = PhysicalRegistry(records, tuple(diagnostics), tuple(load_order))
    errors = registry.active_errors()
    if strict and errors:
        detail = "; ".join(f"{e.path}:{e.key}: {e.message}" for e in errors)
        raise ValueError(f"physical registry validation failed: {detail}")
    return registry


def apply_registry_to_legacy_maps(
    registry: PhysicalRegistry,
    substances: dict[str, dict[str, Any]],
    molar_mass_g_per_mol: dict[str, float],
    osmotic_n: dict[str, float],
    electrolyte_ions: dict[str, dict[str, float]],
) -> None:
    """Overlay validated registry values onto legacy compat.data dictionaries."""
    for key, record in registry.records.items():
        rec = record.data
        if "solubility_g_per_100ml_25c" in rec:
            entry = substances.setdefault(key, {})
            entry["solubility_g_per_100ml_25c"] = rec.get("solubility_g_per_100ml_25c")
            entry["density_kg_m3"] = rec.get("density_kg_m3")
            entry["pka"] = rec.get("pka", [])
            note = rec.get("note") or f"physical registry overlay from {record.path.name}"
            entry["note"] = f"{note} [registry:{record.path.name}]"
        if rec.get("molar_mass_g_per_mol") is not None:
            molar_mass_g_per_mol[key] = float(rec["molar_mass_g_per_mol"])
        if rec.get("osmotic_n") is not None:
            osmotic_n[key] = float(rec["osmotic_n"])
        ions = rec.get("ions_mmol_per_g")
        if isinstance(ions, dict) and ions:
            electrolyte_ions[key] = {f"{ion}_mmol_per_g": float(value) for ion, value in ions.items()}


def _iter_records(raw: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(raw, dict) and "compat_key" in raw:
        yield str(raw.get("key") or raw.get("compat_key") or "<record>"), raw
    elif isinstance(raw, dict):
        yield from raw.items()
    else:
        yield "<root>", raw


def _validate_record(rec: dict[str, Any], path: Path, key: str, *, require_source_refs: bool) -> list[RegistryDiagnostic]:
    diagnostics: list[RegistryDiagnostic] = []
    for field_name in _REQUIRED_FIELDS:
        if field_name not in rec:
            diagnostics.append(RegistryDiagnostic("error", str(path), key, f"missing required field {field_name}"))
    for numeric in ("molar_mass_g_per_mol", "osmotic_n", "solubility_g_per_100ml_25c", "density_kg_m3"):
        if numeric in rec and rec[numeric] is not None and not isinstance(rec[numeric], (int, float)):
            diagnostics.append(RegistryDiagnostic("error", str(path), key, f"{numeric} must be numeric or null"))
    if "pka" in rec and not isinstance(rec.get("pka"), list):
        diagnostics.append(RegistryDiagnostic("error", str(path), key, "pka must be a list"))
    if "ions_mmol_per_g" in rec and not isinstance(rec.get("ions_mmol_per_g"), dict):
        diagnostics.append(RegistryDiagnostic("error", str(path), key, "ions_mmol_per_g must be an object"))
    if not isinstance(rec.get("sources", []), list):
        diagnostics.append(RegistryDiagnostic("error", str(path), key, "sources must be a list"))
    refs = rec.get("source_refs")
    if refs is not None and not isinstance(refs, dict):
        diagnostics.append(RegistryDiagnostic("error", str(path), key, "source_refs must be an object"))
    elif require_source_refs:
        refs = refs or {}
        for field_name in _SOURCE_REF_FIELDS:
            if field_name in rec and rec[field_name] is not None and _missing_source_ref(refs.get(field_name)):
                diagnostics.append(RegistryDiagnostic("error", str(path), key, f"missing source_refs.{field_name}"))
        ions = rec.get("ions_mmol_per_g")
        if isinstance(ions, dict) and ions:
            ion_refs = refs.get("ions_mmol_per_g")
            if not isinstance(ion_refs, dict):
                diagnostics.append(RegistryDiagnostic("error", str(path), key, "missing source_refs.ions_mmol_per_g"))
            else:
                for ion in ions:
                    if _missing_source_ref(ion_refs.get(ion)):
                        diagnostics.append(RegistryDiagnostic("error", str(path), key, f"missing source_refs.ions_mmol_per_g.{ion}"))
    return diagnostics


def _missing_source_ref(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, list):
        return not value
    if isinstance(value, dict):
        return not value
    return False
