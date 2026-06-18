import importlib
import os
import tempfile
from pathlib import Path

from compat.registry import default_registry_dir, load_physical_registry


def test_physical_registry_validates_and_reports_load_order():
    registry = load_physical_registry(strict=True)
    assert not registry.active_errors()
    assert "dextrose_monohydrate" in registry.records
    assert "taurine" in registry.records
    assert "magnesium_chloride" in registry.records
    assert list(registry.load_order) == sorted(registry.load_order)
    report = registry.report()
    assert report["record_count"] >= 23
    assert report["missing_source_refs"] == {}


def test_data_overlay_is_independent_of_process_cwd():
    before = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            import compat.data as data
            reloaded = importlib.reload(data)
        finally:
            os.chdir(before)
    assert reloaded.MOLAR_MASS_G_PER_MOL["magnesium_chloride"] == 203.3
    assert reloaded.OSMOTIC_N["magnesium_chloride"] == 3.0
    assert reloaded.ELECTROLYTE_IONS["magnesium_chloride"]["cl_mmol_per_g"] == 9.8396
    assert "taurine" in reloaded.SUBSTANCES


def test_blocked_and_draft_records_are_not_loaded_by_default(tmp_path: Path):
    (tmp_path / "records.json").write_text(
        """
        {
          "draft_one": {
            "compat_key": "draft_one", "key": "draft_one", "name": "Draft One",
            "molar_mass_g_per_mol": 100.0, "osmotic_n": 1.0,
            "review_status": "draft", "sources": [], "source_refs": {}
          },
          "blocked_one": {
            "compat_key": "blocked_one", "key": "blocked_one", "name": "Blocked One",
            "molar_mass_g_per_mol": 100.0, "osmotic_n": 1.0,
            "review_status": "blocked", "sources": [], "source_refs": {}
          }
        }
        """,
        encoding="utf-8",
    )
    registry = load_physical_registry(tmp_path)
    assert registry.records == {}
    assert {d.level for d in registry.diagnostics} == {"info"}
    research = load_physical_registry(tmp_path, allow_draft=True)
    assert "draft_one" in research.records
    assert "blocked_one" not in research.records


def test_malformed_active_record_fails_strict(tmp_path: Path):
    (tmp_path / "bad.json").write_text(
        '{"bad": {"compat_key": "bad", "review_status": "verified"}}',
        encoding="utf-8",
    )
    try:
        load_physical_registry(tmp_path, strict=True)
    except ValueError as exc:
        assert "physical registry validation failed" in str(exc)
        assert "missing required field" in str(exc)
    else:
        raise AssertionError("strict malformed active registry did not fail")


def test_schema_file_is_present_next_to_registry():
    assert (default_registry_dir() / "schema.json").exists()
