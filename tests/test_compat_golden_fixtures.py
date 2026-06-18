from compat.osmolality import osmolality_report
from compat.solubility import additive_report

FAILING_LIQUID = [
    ("l_tyrosine", 0.5),
    ("creatine_monohydrate", 5.0),
    ("dextrose", 12.0),
    ("ascorbic_acid", 2.0),
    ("citric_acid", 1.5),
    ("beta_alanine", 2.0),
    ("glycerin", 10.0),
]

REFORMULATED_ORS = [
    ("dextrose", 14.0),
    ("sodium_chloride", 2.6),
    ("potassium_chloride", 1.5),
    ("trisodium_citrate", 2.9),
    ("ascorbic_acid", 0.5),
    ("beta_alanine", 1.0),
    ("d_ribose", 2.0),
]

FIGHT_DAY_DRINK = [
    ("dextrose_monohydrate", 22.0),
    ("d_ribose", 5.0),
    ("sodium_chloride", 2.9),
    ("potassium_chloride", 1.1),
    ("l_citrulline", 1.15),
    ("citric_acid", 0.7),
    ("dmg", 0.4),
    ("trisodium_citrate", 0.3),
]


def approx(value, expected, tolerance):
    assert abs(value - expected) <= tolerance, f"{value} != {expected} ± {tolerance}"


def test_failing_liquid_drench_blocks_osmolality_and_ors():
    report = osmolality_report(FAILING_LIQUID, water_ml=150.0)
    sol = additive_report(FAILING_LIQUID, water_ml=150.0)
    approx(report["ors_gate"]["total_mosm_per_l"], 1542, 1.0)
    assert report["ors_gate"]["verdict"] == "BLOCK"
    assert report["electrolyte_balance"]["complete_ors"] is False
    assert len(sol["bottlenecks"]) == 2
    assert {b.split(":", 1)[0] for b in sol["bottlenecks"]} == {"l_tyrosine", "creatine_monohydrate"}


def test_reformulated_liquid_ors_matches_golden_pass():
    report = osmolality_report(REFORMULATED_ORS, water_ml=1000.0)
    sol = additive_report(REFORMULATED_ORS, water_ml=1000.0)
    electro = report["electrolyte_balance"]
    approx(report["ors_gate"]["total_mosm_per_l"], 274, 1.0)
    assert report["ors_gate"]["verdict"] == "PASS"
    assert report["blocking"] is False
    approx(electro["na_mmol"], 74.1, 0.1)
    approx(electro["k_mmol"], 20.1, 0.1)
    approx(electro["cl_mmol"], 64.6, 0.1)
    assert sol["bottlenecks"] == []


def test_fight_day_drink_matches_wiki_claim_and_margin():
    report = osmolality_report(FIGHT_DAY_DRINK, water_ml=1000.0)
    sol = additive_report(FIGHT_DAY_DRINK, water_ml=1000.0)
    electro = report["electrolyte_balance"]
    approx(report["ors_gate"]["total_mosm_per_l"], 291, 1.0)
    assert report["ors_gate"]["verdict"] == "PASS"
    assert report["blocking"] is False
    approx(electro["na_mmol"], 52.7, 0.1)
    approx(electro["k_mmol"], 14.8, 0.1)
    approx(electro["cl_mmol"], 64.4, 0.1)
    assert sol["bottlenecks"] == []


def test_dextrose_monohydrate_identity_is_load_bearing():
    monohydrate = osmolality_report(FIGHT_DAY_DRINK, water_ml=1000.0)["ors_gate"]["total_mosm_per_l"]
    anhydrous_formula = [("dextrose", grams) if name == "dextrose_monohydrate" else (name, grams) for name, grams in FIGHT_DAY_DRINK]
    anhydrous = osmolality_report(anhydrous_formula, water_ml=1000.0)["ors_gate"]["total_mosm_per_l"]
    assert anhydrous - monohydrate > 11.0
    assert anhydrous > 300.0
