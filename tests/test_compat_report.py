from compat import evaluate_formula, render_markdown
from compat_calc import COMPONENTS as FAILING_DRENCH, WATER_ML as FAILING_WATER_ML
from reformulate import LIQUID_ORS, WATER_ML as ORS_WATER_ML
from verify_dry_sku import FIGHT_DAY_DRINK, WATER_ML as DRINK_WATER_ML


def finding_ids(report):
    return {finding["id"] for finding in report["findings"]}


def test_failing_drench_report_blocks_with_schema_and_raw_gates():
    report = evaluate_formula(
        FAILING_DRENCH,
        product_type="hydration_drink",
        water_ml=FAILING_WATER_ML,
        target_ph=3.5,
    )
    assert report["schema_version"] == "compat-eval-v0.1"
    assert report["overall"]["verdict"] == "BLOCK"
    assert report["overall"]["blocking"] is True
    assert round(report["gates"]["osmolality"]["ors_gate"]["total_mosm_per_l"]) == 1542
    assert report["gates"]["osmolality"]["electrolyte_balance"]["complete_ors"] is False
    assert len(report["gates"]["solubility"]["bottlenecks"]) == 2
    ids = finding_ids(report)
    assert "osmolality.ors_gate" in ids
    assert "osmolality.electrolytes_incomplete" in ids
    assert any(f["severity"] == "BLOCKER" for f in report["findings"])
    assert report["assumptions"]
    assert report["provenance"]


def test_reformulated_ors_passes_with_complete_ors():
    report = evaluate_formula(LIQUID_ORS, product_type="hydration_drink", water_ml=ORS_WATER_ML)
    assert report["overall"]["blocking"] is False
    assert report["overall"]["verdict"] in {"PASS", "MARGINAL"}  # high-aw shelf warning may make it marginal
    assert round(report["gates"]["osmolality"]["ors_gate"]["total_mosm_per_l"]) == 274
    assert report["gates"]["osmolality"]["electrolyte_balance"]["complete_ors"] is True
    assert report["gates"]["solubility"]["bottlenecks"] == []
    assert report["scores"]["hydration_cap"] == 10.0


def test_dry_capsule_bypasses_standing_solution_gate():
    report = evaluate_formula([("l_tyrosine", 0.13)], product_type="dry_capsule")
    assert report["applicability"]["dry_ingestion"] is True
    assert report["gates"]["osmolality"]["applicable"] is False
    assert "osmolality.not_applicable" in finding_ids(report)
    assert report["overall"]["blocking"] is False


def test_reconstituted_dry_stick_drink_passes_current_fixture():
    report = evaluate_formula(FIGHT_DAY_DRINK, product_type="reconstituted_drink", water_ml=DRINK_WATER_ML)
    assert report["overall"]["blocking"] is False
    assert round(report["gates"]["osmolality"]["ors_gate"]["total_mosm_per_l"]) == 291
    assert report["gates"]["osmolality"]["electrolyte_balance"]["complete_ors"] is True
    assert report["gates"]["solubility"]["bottlenecks"] == []


def test_markdown_renderer_uses_same_json_conclusions():
    report = evaluate_formula(LIQUID_ORS, product_type="hydration_drink", water_ml=ORS_WATER_ML)
    md = render_markdown(report)
    assert report["schema_version"] in md
    assert report["overall"]["verdict"] in md
    assert "osmolality.ors_gate" in md
