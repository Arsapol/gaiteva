import json
from pathlib import Path

from compat.osmolality import osmolality_report
from compat.solubility import additive_report

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "compat"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def components(fixture: dict) -> list[tuple[str, float]]:
    return [(row["key"], float(row["grams"])) for row in fixture["components"]]


def approx(value, expected, tolerance):
    assert abs(value - expected) <= tolerance, f"{value} != {expected} ± {tolerance}"


def assert_fixture_matches(fixture_name: str) -> tuple[dict, dict, dict]:
    fixture = load_fixture(fixture_name)
    expected = fixture["expected"]
    report = osmolality_report(components(fixture), water_ml=fixture["water_ml"])
    sol = additive_report(components(fixture), water_ml=fixture["water_ml"])
    electro = report["electrolyte_balance"]
    approx(
        report["ors_gate"]["total_mosm_per_l"],
        expected["osmolarity_mosm_per_l"],
        expected["osmolarity_tolerance"],
    )
    assert report["ors_gate"]["verdict"] == expected["verdict"]
    assert electro["complete_ors"] is expected["complete_ors"]
    assert len(sol["bottlenecks"]) == expected["bottleneck_count"]
    for ion_key in ("na_mmol", "k_mmol", "cl_mmol"):
        if ion_key in expected:
            approx(electro[ion_key], expected[ion_key], expected["ion_tolerance"])
    return fixture, report, sol


def test_failing_liquid_drench_blocks_osmolality_and_ors():
    fixture, _report, sol = assert_fixture_matches("failing-liquid-drench.json")
    expected = fixture["expected"]
    assert {b.split(":", 1)[0] for b in sol["bottlenecks"]} == set(expected["bottleneck_keys"])


def test_reformulated_liquid_ors_matches_golden_pass():
    _fixture, report, sol = assert_fixture_matches("reformulated-liquid-ors.json")
    assert report["blocking"] is False
    assert sol["bottlenecks"] == []


def test_fight_day_drink_matches_wiki_claim_and_margin():
    _fixture, report, sol = assert_fixture_matches("fight-day-drink-1l.json")
    assert report["blocking"] is False
    assert sol["bottlenecks"] == []


def test_dextrose_monohydrate_identity_is_load_bearing():
    fixture = load_fixture("fight-day-drink-1l.json")
    expected = fixture["expected"]
    monohydrate = osmolality_report(components(fixture), water_ml=fixture["water_ml"])["ors_gate"]["total_mosm_per_l"]
    anhydrous_formula = [("dextrose", grams) if name == "dextrose_monohydrate" else (name, grams) for name, grams in components(fixture)]
    anhydrous = osmolality_report(anhydrous_formula, water_ml=fixture["water_ml"])["ors_gate"]["total_mosm_per_l"]
    assert anhydrous - monohydrate > expected["anhydrous_dextrose_min_delta_mosm_per_l"]
    assert anhydrous > expected["anhydrous_dextrose_min_total_mosm_per_l"]
