from pathlib import Path

from compat.registry import load_physical_registry


def test_non_strict_registry_keeps_valid_records_when_one_active_record_is_bad(tmp_path: Path):
    (tmp_path / "mixed.json").write_text(
        '''{
          "good": {
            "compat_key": "good", "key": "good", "name": "Good",
            "molar_mass_g_per_mol": 100.0, "osmotic_n": 1.0,
            "solubility_g_per_100ml_25c": 10.0, "review_status": "verified",
            "sources": ["fixture"],
            "source_refs": {
              "molar_mass_g_per_mol": ["fixture"],
              "osmotic_n": ["fixture"],
              "solubility_g_per_100ml_25c": ["fixture"]
            }
          },
          "bad": {"compat_key": "bad", "review_status": "verified"}
        }''',
        encoding="utf-8",
    )
    registry = load_physical_registry(tmp_path, strict=False)
    assert "good" in registry.records
    assert registry.active_errors()
