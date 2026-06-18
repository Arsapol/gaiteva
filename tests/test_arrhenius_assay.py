import math

from compat.arrhenius import (
    arrhenius_k,
    assay_projection_report,
    assay_shelf_life_projection,
)


def _synthetic_first_order_points(*, ea_j=80_000.0, a_per_day=3.0e10):
    rows = []
    for temp_c, days in [(25.0, 45.0), (40.0, 14.0), (50.0, 6.0)]:
        k = arrhenius_k(a_per_day, ea_j, temp_c + 273.15)
        remaining = 100.0 * math.exp(-k * days)
        rows.append({"temperature_C": temp_c, "time_days": days, "measured_value": remaining})
    return rows


def test_synthetic_assay_fixture_recovers_known_ea():
    projection = assay_shelf_life_projection(
        "maillard_browning",
        _synthetic_first_order_points(),
        analyte_or_marker="browning_A420_inverse",
        acceptance_limit=90.0,
    )

    assert projection["arrhenius_fit"]["fit_status"] == "fitted"
    assert projection["projection_basis"] == "assay_fitted"
    assert projection["Ea_J_per_mol_used"] == pytest_approx(80_000.0, rel=0.01)
    assert projection["label_claim_supported"] is False
    assert projection["ich_real_time_status"] in {
        "screen_only",
        "accelerated_supported_real_time_pending",
    }


def test_single_stress_temperature_is_prior_constrained_not_claim():
    projection = assay_shelf_life_projection(
        "ascorbate_oxidation",
        [{"temperature_C": 40.0, "time_days": 28.0, "measured_value": 92.0}],
        analyte_or_marker="ascorbate_potency",
        acceptance_limit=90.0,
    )

    assert projection["projection_basis"] == "prior_constrained"
    assert projection["ich_real_time_status"] == "screen_only"
    assert projection["label_claim_supported"] is False
    assert "Low-Ea" in projection["low_ea_warning"]


def test_report_keeps_screening_separate_from_label_claim():
    projection = assay_shelf_life_projection(
        "creatine_cyclization",
        [{"temperature_C": 50.0, "time_days": 10.0, "measured_value": 95.0}],
        analyte_or_marker="creatine_potency",
        acceptance_limit=90.0,
    )
    report = assay_projection_report(projection)

    assert "ICH/real-time status: screen_only" in report
    assert "Label shelf-life claim supported: NO" in report
    assert "50 °C" in report


def pytest_approx(expected, *, rel):
    # Keep this file runnable under unittest/plain Python if pytest is absent.
    class Approx:
        def __eq__(self, actual):
            return abs(actual - expected) <= abs(expected) * rel
    return Approx()


def test_missing_assay_data_does_not_fabricate_shelf_life():
    projection = assay_shelf_life_projection(
        "maillard_browning",
        [],
        analyte_or_marker="browning_A420",
        acceptance_limit=90.0,
    )

    assert projection["ich_real_time_status"] == "insufficient_data"
    assert projection["projected_shelf_life_days"] is None
    assert projection["label_claim_supported"] is False
