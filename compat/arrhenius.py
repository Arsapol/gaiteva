"""
Gamefowl supplement shelf-life calculator — Arrhenius kinetics.

All functions are pure and immutable (no side effects, no mutation).
Temperature inputs in Celsius are converted internally to Kelvin (+273.15).

Functions
---------
arrhenius_k   : rate constant k = A * exp(-Ea / RT)
q10           : rate multiplier per +10 K above reference
accel_factor  : ICH-style acceleration factor between two temperatures
pathway_projection : Q10/AF/stress-week summary for one degradation pathway
all_pathways  : run pathway_projection for every registered pathway
assay_shelf_life_projection : fit assay points and project screening shelf life
assay_projection_report : human-readable assay projection report lines

Assay-driven guardrail
----------------------
The assay-driven helpers intentionally return screening projections plus an
ICH/real-time status. They do not make label shelf-life claims from stress data
alone; ``label_claim_supported`` is only true when real-time target-temperature
observations cover the projected endpoint.
"""

from __future__ import annotations

import math
from collections import defaultdict
import json
from typing import Any, Iterable, TypedDict

from compat.data import DEGRADATION_EA_J_PER_MOL

# Universal gas constant (J / mol / K)
_R: float = 8.314


class AssayPoint(TypedDict, total=False):
    """Data model for one stability-assay observation row.

    Runtime validation requires ``temperature_C``, ``time_days``, and
    ``measured_value``. The optional fields record the tested matrix and
    storage scope so a projection cannot be detached from its evidence.
    """

    temperature_C: float
    time_days: float
    measured_value: float
    unit: str
    replicate_id: str
    endpoint: str
    formulation_id: str
    lot_id: str
    pH: float
    water_activity: float
    packaging: str
    headspace: str
    light: str
    oxygen: str
    metal_ppb: float


class AssayProjection(TypedDict, total=False):
    """Data model returned by ``assay_shelf_life_projection``."""

    pathway: str
    analyte_or_marker: str
    model_type: str
    initial_value: float
    acceptance_limit: float
    target_temperature_C: float
    rates_by_temperature: dict[float, dict[str, Any]]
    arrhenius_fit: dict[str, Any]
    projection_basis: str
    projected_rate_per_day: float | None
    projected_shelf_life_days: float | None
    projected_shelf_life_months: float | None
    Ea_J_per_mol_used: float | None
    A_per_day_used: float | None
    ich_real_time_status: str
    label_claim_supported: bool
    guardrail_note: str
    low_ea_warning: str
    storage_scope_fields: list[str]


# ---------------------------------------------------------------------------
# Core Arrhenius functions
# ---------------------------------------------------------------------------

def arrhenius_k(A: float, Ea_J: float, T_K: float) -> float:
    """Return the rate constant k = A * exp(-Ea / RT).

    Parameters
    ----------
    A    : pre-exponential factor (same units as k; arbitrary positive float)
    Ea_J : activation energy in J/mol
    T_K  : absolute temperature in Kelvin
    """
    return A * math.exp(-Ea_J / (_R * T_K))


def q10(Ea_J: float, T_K: float = 298.15) -> float:
    """Return the Q10 rate multiplier — how much faster the reaction is per +10 K.

    Q10 = exp(Ea / R * 10 / T^2)   (Van't Hoff / Arrhenius approximation)

    Parameters
    ----------
    Ea_J : activation energy in J/mol
    T_K  : reference temperature in Kelvin (default 298.15 K = 25 °C)
    """
    return math.exp(Ea_J * 10.0 / (_R * T_K ** 2))


def accel_factor(Ea_J: float, T_stress_K: float, T_store_K: float) -> float:
    """Return the ICH-style acceleration factor AF.

    AF = exp(Ea/R * (1/T_store - 1/T_stress))

    A product that degrades by a given fraction in *t* days at T_stress will
    take AF * t days to reach the same endpoint at T_store.

    Parameters
    ----------
    Ea_J      : activation energy in J/mol
    T_stress_K : stress (elevated) temperature in Kelvin
    T_store_K  : storage (target) temperature in Kelvin
    """
    return math.exp(Ea_J / _R * (1.0 / T_store_K - 1.0 / T_stress_K))


# ---------------------------------------------------------------------------
# Pathway-level summaries
# ---------------------------------------------------------------------------

def pathway_projection(
    pathway_key: str,
    T_stress_C: float = 40.0,
    T_store_C: float = 25.0,
) -> dict[str, Any]:
    """Return a shelf-life projection dict for one degradation pathway.

    Parameters
    ----------
    pathway_key : key in DEGRADATION_EA_J_PER_MOL
                  ('ascorbate_oxidation', 'maillard_browning', 'creatine_cyclization')
    T_stress_C  : accelerated-aging stress temperature in °C (default 40 °C)
    T_store_C   : target storage temperature in °C (default 25 °C)

    Returns
    -------
    dict with keys:
        pathway                   : str, the pathway key
        Q10_range                 : (low, typical, high) Q10 at T_store
        AF_range                  : (low, typical, high) acceleration factors
        weeks_stress_for_24mo_typical : float, weeks at T_stress equivalent to 24 mo storage
        ich_warning               : str, regulatory caution text (non-empty when Ea is low)
    """
    ea_low, ea_typ, ea_high = DEGRADATION_EA_J_PER_MOL[pathway_key]

    T_stress_K = T_stress_C + 273.15
    T_store_K = T_store_C + 273.15

    q10_low = q10(ea_low, T_store_K)
    q10_typ = q10(ea_typ, T_store_K)
    q10_high = q10(ea_high, T_store_K)

    af_low = accel_factor(ea_low, T_stress_K, T_store_K)
    af_typ = accel_factor(ea_typ, T_stress_K, T_store_K)
    af_high = accel_factor(ea_high, T_stress_K, T_store_K)

    # 24 months real-time ÷ AF_typical → weeks of stress needed
    real_time_weeks = 24.0 * (365.25 / 7.0 / 12.0)  # 24 calendar months in weeks
    weeks_stress = real_time_weeks / af_typ

    # ICH Q1A(R2) warning: when Ea is low, AF is small (~2–3×) so accelerated
    # aging at 40 °C cannot adequately compress 24 months into a short study;
    # real-time 25 °C data remain mandatory.
    if ea_typ <= 50_000:
        ich_warning = (
            f"LOW Ea ({ea_typ/1000:.0f} kJ/mol): AF(typical) = {af_typ:.1f}x only. "
            "ICH Q1A(R2) requires real-time 25 °C data for this pathway — "
            "accelerated aging alone cannot establish shelf life when Ea < ~50 kJ/mol."
        )
    else:
        ich_warning = (
            f"HIGH Ea ({ea_typ/1000:.0f} kJ/mol): AF(typical) = {af_typ:.1f}x. "
            "Accelerated aging at 40 °C is predictive; real-time confirmation still "
            "recommended but AF compression is meaningful."
        )

    return {
        "pathway": pathway_key,
        "Q10_range": (round(q10_low, 2), round(q10_typ, 2), round(q10_high, 2)),
        "AF_range": (round(af_low, 1), round(af_typ, 1), round(af_high, 1)),
        "weeks_stress_for_24mo_typical": round(weeks_stress, 1),
        "ich_warning": ich_warning,
    }


def all_pathways(
    T_stress_C: float = 40.0,
    T_store_C: float = 25.0,
) -> dict[str, dict[str, Any]]:
    """Run pathway_projection for every registered pathway.

    Returns
    -------
    dict keyed by pathway name, values are pathway_projection dicts.
    """
    return {
        key: pathway_projection(key, T_stress_C, T_store_C)
        for key in DEGRADATION_EA_J_PER_MOL
    }


# ---------------------------------------------------------------------------
# Assay-driven shelf-life layer
# ---------------------------------------------------------------------------

_ASSAY_REQUIRED_FIELDS = ("temperature_C", "time_days", "measured_value")
_SUPPORTED_MODELS = {"first_order", "zero_order"}

ASSAY_TARGET_TEMP_TOLERANCE_C = 0.6
STRESS_SCREEN_ONLY_TEMP_C = 50.0
LOW_EA_WARNING_THRESHOLD_J_PER_MOL = 50_000
LOW_EA_WARNING_PATHWAYS = {"ascorbate_oxidation"}
STORAGE_SCOPE_FIELDS = (
    "formulation_id", "lot_id", "pH", "water_activity", "packaging",
    "headspace", "light", "oxygen", "metal_ppb",
)


def _as_float(row: AssayPoint, key: str) -> float:
    value = row[key]
    if value is None:
        raise ValueError(f"assay point field {key!r} cannot be None")
    return float(value)


def _validate_assay_point(row: AssayPoint) -> None:
    missing = [key for key in _ASSAY_REQUIRED_FIELDS if key not in row]
    if missing:
        raise ValueError(f"assay point missing required field(s): {', '.join(missing)}")
    if _as_float(row, "time_days") < 0:
        raise ValueError("assay point time_days must be >= 0")
    if _as_float(row, "measured_value") < 0:
        raise ValueError("assay point measured_value must be >= 0")


def assay_rates_by_temperature(
    assay_points: Iterable[AssayPoint],
    *,
    initial_value: float = 100.0,
    model_type: str = "first_order",
) -> dict[float, dict[str, Any]]:
    """Estimate degradation rates from assay rows grouped by temperature.

    ``assay_points`` rows require ``temperature_C``, ``time_days``, and
    ``measured_value``. Optional metadata such as ``replicate_id``, ``endpoint``,
    ``lot_id``, ``pH``, ``packaging``, ``headspace``, ``light``, and
    ``oxygen`` is passed through only by callers; the rate fit uses the numeric
    fields.

    ``model_type='first_order'`` treats ``measured_value`` as remaining potency
    or marker fraction relative to ``initial_value`` and returns k in 1/day.
    ``model_type='zero_order'`` treats loss as linear value units/day.
    """
    if model_type not in _SUPPORTED_MODELS:
        raise ValueError(f"model_type must be one of {sorted(_SUPPORTED_MODELS)}")
    if initial_value <= 0:
        raise ValueError("initial_value must be positive")

    rates: dict[float, list[float]] = defaultdict(list)
    source_rows: dict[float, int] = defaultdict(int)

    for row in assay_points:
        _validate_assay_point(row)
        temp_C = _as_float(row, "temperature_C")
        time_days = _as_float(row, "time_days")
        measured_value = _as_float(row, "measured_value")
        source_rows[temp_C] += 1

        # Baseline observations are useful evidence for elapsed real-time
        # coverage, but they do not estimate a degradation rate by themselves.
        if time_days == 0:
            continue

        if model_type == "first_order":
            if measured_value <= 0:
                raise ValueError("first_order assay measured_value must be > 0")
            fraction_remaining = measured_value / initial_value
            if not 0 < fraction_remaining <= 1:
                raise ValueError("first_order assay measured_value cannot exceed initial_value")
            rates[temp_C].append(-math.log(fraction_remaining) / time_days)
        else:
            loss = initial_value - measured_value
            if loss < 0:
                raise ValueError("zero_order assay measured_value cannot exceed initial_value")
            rates[temp_C].append(loss / time_days)

    fit: dict[float, dict[str, Any]] = {}
    for temp_C, values in rates.items():
        if not values:
            continue
        fit[temp_C] = {
            "temperature_C": temp_C,
            "rate_per_day": sum(values) / len(values),
            "n_rate_points": len(values),
            "n_source_rows": source_rows[temp_C],
            "model_type": model_type,
        }
    return dict(sorted(fit.items()))


def fit_arrhenius_ea_from_rates(rates_by_temperature: dict[float, dict[str, Any]]) -> dict[str, Any]:
    """Fit Ea from ``ln(k)`` vs ``1/T`` when at least two temperatures exist."""
    pairs = [
        (1.0 / (temp_C + 273.15), math.log(row["rate_per_day"]))
        for temp_C, row in rates_by_temperature.items()
        if row["rate_per_day"] > 0
    ]
    if len(pairs) < 2:
        return {
            "fit_status": "insufficient_temperatures",
            "temperature_count": len(pairs),
            "Ea_J_per_mol": None,
            "A_per_day": None,
        }

    mean_x = sum(x for x, _ in pairs) / len(pairs)
    mean_y = sum(y for _, y in pairs) / len(pairs)
    denom = sum((x - mean_x) ** 2 for x, _ in pairs)
    if denom == 0:
        return {
            "fit_status": "insufficient_temperature_span",
            "temperature_count": len(pairs),
            "Ea_J_per_mol": None,
            "A_per_day": None,
        }

    slope = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / denom
    intercept = mean_y - slope * mean_x
    ea_J = -slope * _R
    if ea_J <= 0:
        return {
            "fit_status": "nonphysical_ea",
            "temperature_count": len(pairs),
            "Ea_J_per_mol": ea_J,
            "A_per_day": math.exp(intercept),
        }

    return {
        "fit_status": "fitted",
        "temperature_count": len(pairs),
        "Ea_J_per_mol": ea_J,
        "A_per_day": math.exp(intercept),
    }


def _project_rate_from_ea(
    *,
    observed_rate_per_day: float,
    observed_temperature_C: float,
    Ea_J: float,
    target_temperature_C: float,
) -> float:
    observed_K = observed_temperature_C + 273.15
    target_K = target_temperature_C + 273.15
    return observed_rate_per_day / accel_factor(Ea_J, observed_K, target_K)


def _endpoint_days(
    *,
    initial_value: float,
    acceptance_limit: float,
    rate_per_day: float,
    model_type: str,
) -> float | None:
    if rate_per_day <= 0:
        return None
    if model_type == "first_order":
        if not 0 < acceptance_limit < initial_value:
            raise ValueError("first_order acceptance_limit must be between 0 and initial_value")
        return -math.log(acceptance_limit / initial_value) / rate_per_day
    if acceptance_limit >= initial_value:
        raise ValueError("zero_order acceptance_limit must be below initial_value")
    return (initial_value - acceptance_limit) / rate_per_day


def _max_observed_days_at_temperature(
    assay_points: Iterable[AssayPoint], target_temperature_C: float) -> float:
    max_days = 0.0
    for row in assay_points:
        _validate_assay_point(row)
        if abs(_as_float(row, "temperature_C") - target_temperature_C) <= ASSAY_TARGET_TEMP_TOLERANCE_C:
            max_days = max(max_days, _as_float(row, "time_days"))
    return max_days


def _ich_status(
    *,
    assay_points: list[AssayPoint],
    target_temperature_C: float,
    max_assay_temperature_C: float | None,
    temperature_count: int,
    projected_days: float | None,
) -> tuple[str, bool, str]:
    if projected_days is None or temperature_count == 0:
        return (
            "insufficient_data",
            False,
            "No positive assay-derived rate was available; do not infer shelf life.",
        )

    real_time_days = _max_observed_days_at_temperature(assay_points, target_temperature_C)
    if real_time_days >= projected_days:
        return (
            "real_time_confirmed",
            True,
            "Target-temperature observations cover the projected endpoint; label claim still remains limited to the tested matrix/packaging.",
        )

    if max_assay_temperature_C is not None and max_assay_temperature_C >= STRESS_SCREEN_ONLY_TEMP_C:
        return (
            "screen_only",
            False,
            "50 °C or hotter data are stress-screen evidence only because mechanisms can change; reject-risk signal, not a label shelf-life claim.",
        )

    if temperature_count >= 2:
        return (
            "accelerated_supported_real_time_pending",
            False,
            "Multi-temperature accelerated data support a screening projection, but ICH real-time target-temperature confirmation is still pending.",
        )

    return (
        "screen_only",
        False,
        "Single-temperature stress data are prior-constrained screening evidence only; real-time confirmation is required.",
    )


def _storage_scope_metadata(rows: list[AssayPoint]) -> dict[str, Any]:
    scope: dict[str, Any] = {}
    for field in STORAGE_SCOPE_FIELDS:
        values = []
        for row in rows:
            if field in row and row[field] is not None:
                value = row[field]
                marker = json.dumps(value, sort_keys=True, default=str) if isinstance(value, (dict, list)) else str(value)
                if marker not in [m for m, _ in values]:
                    values.append((marker, value))
        if len(values) > 1:
            raise ValueError(f"assay projection scope field {field!r} contains mixed values; split projections by storage scope")
        if len(values) == 1:
            scope[field] = values[0][1]
    return scope


def assay_shelf_life_projection(
    pathway_key: str,
    assay_points: Iterable[AssayPoint],
    *,
    analyte_or_marker: str,
    acceptance_limit: float,
    initial_value: float = 100.0,
    target_temperature_C: float = 25.0,
    model_type: str = "first_order",
) -> AssayProjection:
    """Project shelf-life from actual assay observations plus guardrails.

    The function fits per-temperature degradation rates from assay rows and fits
    Arrhenius Ea only when two or more positive-rate temperatures exist. With a
    single stress temperature, it uses the pathway's typical Ea prior and marks
    the result as ``prior_constrained`` / ``screen_only``.

    Returned shelf-life values are screening projections. They are safe for
    ranking and go/no-go decisions, not label claims unless
    ``label_claim_supported`` is true.
    """
    if pathway_key not in DEGRADATION_EA_J_PER_MOL:
        raise KeyError(f"unknown pathway_key {pathway_key!r}")
    rows = [dict(row) for row in assay_points]
    for row in rows:
        _validate_assay_point(row)
    storage_scope = _storage_scope_metadata(rows)

    rates = assay_rates_by_temperature(rows, initial_value=initial_value, model_type=model_type)
    fit = fit_arrhenius_ea_from_rates(rates)
    max_temp = max((_as_float(row, "temperature_C") for row in rows), default=None)

    projection_basis = "assay_fitted" if fit["fit_status"] == "fitted" else "prior_constrained"
    if fit["fit_status"] == "fitted":
        ea_J = float(fit["Ea_J_per_mol"])
        A_per_day = float(fit["A_per_day"])
        projected_rate = arrhenius_k(A_per_day, ea_J, target_temperature_C + 273.15)
    elif rates:
        _ea_low, ea_typ, _ea_high = DEGRADATION_EA_J_PER_MOL[pathway_key]
        nearest_temp = min(rates, key=lambda t: abs(t - target_temperature_C))
        projected_rate = _project_rate_from_ea(
            observed_rate_per_day=rates[nearest_temp]["rate_per_day"],
            observed_temperature_C=nearest_temp,
            Ea_J=ea_typ,
            target_temperature_C=target_temperature_C,
        )
        ea_J = float(ea_typ)
        A_per_day = None
    else:
        ea_J = None
        A_per_day = None
        projected_rate = None

    projected_days = None
    if projected_rate is not None:
        projected_days = _endpoint_days(
            initial_value=initial_value,
            acceptance_limit=acceptance_limit,
            rate_per_day=projected_rate,
            model_type=model_type,
        )

    ich_status, label_supported, guardrail_note = _ich_status(
        assay_points=rows,
        target_temperature_C=target_temperature_C,
        max_assay_temperature_C=max_temp,
        temperature_count=len(rates),
        projected_days=projected_days,
    )

    low_ea_warning = ""
    if pathway_key in LOW_EA_WARNING_PATHWAYS or (ea_J is not None and ea_J <= LOW_EA_WARNING_THRESHOLD_J_PER_MOL):
        low_ea_warning = (
            "Low-Ea/ascorbate-sensitive pathway: accelerated data compress poorly and O2/light/metal/pH controls may dominate; require real-time assays."
        )

    return {
        "pathway": pathway_key,
        "analyte_or_marker": analyte_or_marker,
        "model_type": model_type,
        "initial_value": initial_value,
        "acceptance_limit": acceptance_limit,
        "target_temperature_C": target_temperature_C,
        "rates_by_temperature": rates,
        "arrhenius_fit": fit,
        "projection_basis": projection_basis,
        "projected_rate_per_day": None if projected_rate is None else round(projected_rate, 8),
        "projected_shelf_life_days": None if projected_days is None else round(projected_days, 1),
        "projected_shelf_life_months": None if projected_days is None else round(projected_days / 30.4375, 2),
        "Ea_J_per_mol_used": None if ea_J is None else round(ea_J, 1),
        "A_per_day_used": A_per_day,
        "ich_real_time_status": ich_status,
        "label_claim_supported": label_supported,
        "guardrail_note": guardrail_note,
        "low_ea_warning": low_ea_warning,
        "storage_scope_fields": list(STORAGE_SCOPE_FIELDS),
        "storage_scope": storage_scope,
    }


def assay_projection_report(projection: AssayProjection) -> str:
    """Render a compact, human-readable assay projection report."""
    shelf_days = projection["projected_shelf_life_days"]
    shelf = "not projected" if shelf_days is None else f"{shelf_days:.1f} days ({projection['projected_shelf_life_months']:.2f} months)"
    ea = projection["Ea_J_per_mol_used"]
    ea_text = "not estimated" if ea is None else f"{ea/1000:.1f} kJ/mol"
    lines = [
        f"Assay projection: {projection['pathway']} / {projection['analyte_or_marker']}",
        f"  model: {projection['model_type']} ({projection['projection_basis']})",
        f"  target: {projection['target_temperature_C']:.1f} °C; endpoint: {projection['acceptance_limit']} from initial {projection['initial_value']}",
        f"  Ea used: {ea_text}; projected endpoint: {shelf}",
        f"  ICH/real-time status: {projection['ich_real_time_status']}",
        f"  Label shelf-life claim supported: {'YES' if projection['label_claim_supported'] else 'NO'}",
        f"  Guardrail: {projection['guardrail_note']}",
    ]
    if projection["low_ea_warning"]:
        lines.append(f"  Warning: {projection['low_ea_warning']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pprint

    print("=== Arrhenius smoke test  (stress=40°C, store=25°C) ===\n")

    # Spot-check core functions
    k = arrhenius_k(A=1.0, Ea_J=97_000, T_K=298.15)
    print(f"arrhenius_k(A=1, Ea=97 kJ/mol, T=25°C) = {k:.4e}")

    q = q10(Ea_J=97_000, T_K=298.15)
    print(f"q10(Ea=97 kJ/mol, T=25°C)               = {q:.3f}")

    af = accel_factor(Ea_J=97_000, T_stress_K=313.15, T_store_K=298.15)
    print(f"accel_factor(97 kJ/mol, 40°C→25°C)      = {af:.2f}x\n")

    print("=== all_pathways() ===\n")
    pprint.pprint(all_pathways(), sort_dicts=False)
