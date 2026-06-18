"""
ph_module.py — pH / buffer chemistry helpers for the gamefowl supplement compat calculator.

All functions are pure and immutable (return new dicts, never mutate inputs).
Target product pH window: 3.0 – 4.0.
"""

from __future__ import annotations

from math import isfinite

from compat.data import MOLAR_MASS_G_PER_MOL, SUBSTANCES

_CITRIC_PKA: list[float] = SUBSTANCES["citric_acid"]["pka"]  # [3.13, 4.76, 6.40]
_KW_25C = 1e-14
_LN10 = 2.302585092994046

# Minimal, explicit hydrate/form registry for citrate pH screening.  Keep this
# local until the physical-constants registry owns every hydrate variant.
_CITRATE_SPECIES: dict[str, dict[str, float | str]] = {
    "citric_acid": {
        "role": "acid",
        "mw_g_per_mol": MOLAR_MASS_G_PER_MOL["citric_acid"],
        "citrate_per_mol": 1.0,
        "strong_cation_mol_per_mol": 0.0,
    },
    "citric_acid_monohydrate": {
        "role": "acid",
        "mw_g_per_mol": 210.14,
        "citrate_per_mol": 1.0,
        "strong_cation_mol_per_mol": 0.0,
    },
    "trisodium_citrate": {
        "role": "base_salt",
        "mw_g_per_mol": MOLAR_MASS_G_PER_MOL["trisodium_citrate"],
        "citrate_per_mol": 1.0,
        "strong_cation_mol_per_mol": 3.0,
    },
    "trisodium_citrate_anhydrous": {
        "role": "base_salt",
        "mw_g_per_mol": 258.06,
        "citrate_per_mol": 1.0,
        "strong_cation_mol_per_mol": 3.0,
    },
}


def henderson_hasselbalch(pH: float, pKa: float) -> dict:
    """
    Return Henderson-Hasselbalch derived quantities for a single pKa.

    Parameters
    ----------
    pH  : solution pH
    pKa : acid dissociation constant

    Returns
    -------
    dict with keys:
        base_to_acid_ratio : float  — [A⁻] / [HA]  (10^(pH - pKa))
        fraction_ionized   : float  — mole fraction present as conjugate base
    """
    ratio = 10 ** (pH - pKa)
    fraction_ionized = ratio / (1.0 + ratio)
    return {
        "base_to_acid_ratio": ratio,
        "fraction_ionized": fraction_ionized,
    }


def citrate_alpha_fractions(pH: float, pka: list[float] | None = None) -> dict:
    """Return triprotic citrate alpha fractions at a pH.

    Fractions are for H3Cit, H2Cit-, HCit2-, and Cit3-.  This is still a
    screening model: activity coefficients, temperature, and the rest of the
    formula matrix are not solved here.
    """
    pka = list(_CITRIC_PKA if pka is None else pka)
    if len(pka) != 3:
        raise ValueError("citrate alpha calculation requires exactly three pKa values")
    h = 10 ** (-pH)
    ka1, ka2, ka3 = (10 ** (-x) for x in pka)
    denom = h**3 + ka1 * h**2 + ka1 * ka2 * h + ka1 * ka2 * ka3
    if denom <= 0 or not isfinite(denom):
        raise ValueError("invalid citrate alpha denominator")
    a0 = h**3 / denom
    a1 = ka1 * h**2 / denom
    a2 = ka1 * ka2 * h / denom
    a3 = ka1 * ka2 * ka3 / denom
    avg_charge = a1 + 2.0 * a2 + 3.0 * a3
    return {
        "H3Cit": a0,
        "H2Cit_minus": a1,
        "HCit_2minus": a2,
        "Cit_3minus": a3,
        "average_negative_charge": avg_charge,
    }


def citrate_buffer_ratio(target_pH: float) -> dict:
    """
    Report citric acid buffer speciation at target_pH using pKa values from data.py.

    Identifies the pKa closest to target_pH (greatest buffering capacity there)
    and computes the conjugate-base : acid mole ratio for that equilibrium.

    Parameters
    ----------
    target_pH : desired solution pH

    Returns
    -------
    dict with keys:
        dominant_pka         : float  — the pKa nearest target_pH
        dominant_pka_index   : int    — 1-based index (pKa1/pKa2/pKa3)
        base_to_acid_ratio   : float  — mole ratio citrate⁻ : citric acid at dominant pKa
        fraction_ionized     : float  — fraction deprotonated at dominant pKa
        all_pka              : list   — full pKa list for reference
    """
    pka_list = _CITRIC_PKA
    dominant_pka = min(pka_list, key=lambda k: abs(target_pH - k))
    dominant_index = pka_list.index(dominant_pka) + 1
    hh = henderson_hasselbalch(target_pH, dominant_pka)
    return {
        "dominant_pka": dominant_pka,
        "dominant_pka_index": dominant_index,
        "base_to_acid_ratio": hh["base_to_acid_ratio"],
        "fraction_ionized": hh["fraction_ionized"],
        "all_pka": list(pka_list),
    }


def _component_name_and_grams(component: tuple[str, float] | dict) -> tuple[str, float, str | None]:
    if isinstance(component, dict):
        name = str(component.get("name") or component.get("key"))
        grams = float(component.get("grams", component.get("g", component.get("amount_g", 0.0))))
        form = component.get("form") or component.get("hydrate")
        return name, grams, None if form is None else str(form)
    name, grams = component
    return str(name), float(grams), None


def _species_key(name: str, form: str | None = None) -> str | None:
    normalized = name.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in {"sodium_citrate", "trisodium_citrate_dihydrate"}:
        normalized = "trisodium_citrate"
    if normalized in {"citric_acid_anhydrous"}:
        normalized = "citric_acid"
    if form:
        f = form.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized == "citric_acid" and "monohydrate" in f:
            normalized = "citric_acid_monohydrate"
        if normalized == "trisodium_citrate" and "anhydrous" in f:
            normalized = "trisodium_citrate_anhydrous"
    return normalized if normalized in _CITRATE_SPECIES else None


def citrate_inventory(components: list[tuple[str, float]] | list[dict], water_ml: float) -> dict:
    """Summarize citrate acid/base moles and concentration for pH screening."""
    if water_ml <= 0:
        raise ValueError("water_ml must be positive")
    species_rows = []
    total_citrate_mol = 0.0
    strong_cation_mol = 0.0
    acid_mol = 0.0
    base_salt_mol = 0.0
    for component in components:
        name, grams, form = _component_name_and_grams(component)
        key = _species_key(name, form)
        if grams < 0:
            raise ValueError(f"negative component mass for {name}")
        if key is None or grams == 0:
            continue
        spec = _CITRATE_SPECIES[key]
        moles = grams / float(spec["mw_g_per_mol"])
        citrate_mol = moles * float(spec["citrate_per_mol"])
        cation_mol = moles * float(spec["strong_cation_mol_per_mol"])
        total_citrate_mol += citrate_mol
        strong_cation_mol += cation_mol
        if spec["role"] == "acid":
            acid_mol += citrate_mol
        else:
            base_salt_mol += citrate_mol
        species_rows.append({
            "name": name,
            "modeled_as": key,
            "role": spec["role"],
            "grams": grams,
            "mw_g_per_mol": spec["mw_g_per_mol"],
            "citrate_mmol": citrate_mol * 1000.0,
            "strong_cation_mmol": cation_mol * 1000.0,
        })
    volume_l = water_ml / 1000.0
    return {
        "water_ml": water_ml,
        "species": species_rows,
        "total_citrate_mmol": total_citrate_mol * 1000.0,
        "total_citrate_mmol_per_l": (total_citrate_mol / volume_l) * 1000.0,
        "strong_cation_mmol": strong_cation_mol * 1000.0,
        "strong_cation_mmol_per_l": (strong_cation_mol / volume_l) * 1000.0,
        "acid_citrate_mmol": acid_mol * 1000.0,
        "base_salt_citrate_mmol": base_salt_mol * 1000.0,
        "acid_to_base_citrate_ratio": None if base_salt_mol == 0 else acid_mol / base_salt_mol,
    }


def _charge_balance(pH: float, citrate_mol_l: float, strong_cation_mol_l: float) -> float:
    h = 10 ** (-pH)
    oh = _KW_25C / h
    alpha = citrate_alpha_fractions(pH)
    citrate_negative = citrate_mol_l * alpha["average_negative_charge"]
    return (h + strong_cation_mol_l) - (oh + citrate_negative)


def _solve_citrate_ph(citrate_mol_l: float, strong_cation_mol_l: float) -> tuple[float | None, str]:
    if citrate_mol_l <= 0:
        return None, "no citrate acid/base species were present; pH not predicted"
    low, high = 0.0, 14.0
    f_low = _charge_balance(low, citrate_mol_l, strong_cation_mol_l)
    f_high = _charge_balance(high, citrate_mol_l, strong_cation_mol_l)
    if f_low == 0:
        return low, "charge-balance root at lower bound"
    if f_high == 0:
        return high, "charge-balance root at upper bound"
    if f_low * f_high > 0:
        return None, "no physical pH root found in pH 0-14 for citrate-only charge balance"
    for _ in range(80):
        mid = (low + high) / 2.0
        f_mid = _charge_balance(mid, citrate_mol_l, strong_cation_mol_l)
        if abs(f_mid) < 1e-12:
            return mid, "charge-balance root solved"
        if f_low * f_mid <= 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return (low + high) / 2.0, "charge-balance root solved (iteration limit)"


def _required_strong_cation_mol_l(pH: float, citrate_mol_l: float) -> float:
    h = 10 ** (-pH)
    oh = _KW_25C / h
    alpha = citrate_alpha_fractions(pH)
    return oh + citrate_mol_l * alpha["average_negative_charge"] - h


def _buffer_shift_report(predicted_pH: float, citrate_mol_l: float, strong_cation_mol_l: float) -> dict:
    shifts = {}
    for delta in (0.1, 0.5):
        down = max(0.0, predicted_pH - delta)
        up = min(14.0, predicted_pH + delta)
        acid_needed = max(0.0, strong_cation_mol_l - _required_strong_cation_mol_l(down, citrate_mol_l))
        base_needed = max(0.0, _required_strong_cation_mol_l(up, citrate_mol_l) - strong_cation_mol_l)
        shifts[f"minus_{delta:g}_pH_acid_mmol_per_l"] = acid_needed * 1000.0
        shifts[f"plus_{delta:g}_pH_base_mmol_per_l"] = base_needed * 1000.0
    beta = None
    try:
        c = citrate_mol_l
        alpha = citrate_alpha_fractions(predicted_pH)
        beta_water = _LN10 * ((10 ** (-predicted_pH)) + (_KW_25C / (10 ** (-predicted_pH))))
        # Numerical local slope of bound base equivalents, robust for triprotic acid.
        eps = 0.001
        a_minus = citrate_alpha_fractions(predicted_pH - eps)["average_negative_charge"]
        a_plus = citrate_alpha_fractions(predicted_pH + eps)["average_negative_charge"]
        beta = (c * (a_plus - a_minus) / (2.0 * eps) + beta_water) * 1000.0
    except Exception:
        beta = None
    return {
        "beta_mmol_per_l_per_pH": beta,
        "shift_reserve": shifts,
        "interpretation": (
            "screening buffer reserve only: mmol/L strong acid/base equivalents to move pH; "
            "confirm final products with calibrated pH meter in the real matrix"
        ),
    }


def preservative_active_fraction(pH: float, preservative: str = "sorbic_acid", pka: float | None = None) -> dict:
    """Return undissociated weak-acid preservative fraction at pH.

    Default pKa is sorbic acid/potassium sorbate (~4.76). Benzoic acid can be
    requested with preservative="benzoic_acid".
    """
    pka_by_name = {"sorbic_acid": 4.76, "potassium_sorbate": 4.76, "benzoic_acid": 4.20, "sodium_benzoate": 4.20}
    use_pka = float(pka if pka is not None else pka_by_name.get(preservative, 4.76))
    fraction = 1.0 / (1.0 + 10 ** (pH - use_pka))
    if fraction >= 0.85:
        verdict = "strong active-fraction support"
    elif fraction >= 0.5:
        verdict = "moderate active fraction; verify preservative system"
    else:
        verdict = "low active fraction; pH likely undermines weak-acid preservative efficacy"
    return {"preservative": preservative, "pka": use_pka, "undissociated_fraction": fraction, "verdict": verdict}


def citrate_ph_report(
    components: list[tuple[str, float]] | list[dict],
    water_ml: float,
    *,
    dilution_water_ml: float | None = None,
    measured_pH: float | None = None,
    use_case: str = "screening",
) -> dict:
    """Predict citrate-driven pH, buffer reserve, and optional dilution drift.

    This is deliberately conservative: only registered citrate acid/base species
    drive the pH root, and caveats are always returned because real formula
    matrices can shift pH by several tenths.
    """
    inventory = citrate_inventory(components, water_ml)
    citrate_mol_l = inventory["total_citrate_mmol_per_l"] / 1000.0
    cation_mol_l = inventory["strong_cation_mmol_per_l"] / 1000.0
    predicted_pH, solver_status = _solve_citrate_ph(citrate_mol_l, cation_mol_l)
    effective_pH = measured_pH if measured_pH is not None else predicted_pH
    caveats = [
        "screening-grade citrate-only pH estimate; validate with calibrated meter at use temperature",
        "activity coefficients, amino acids, minerals, sugars, CO2 uptake, and preservatives are not fully modeled",
        "hydrate/form assumptions are explicit only for citric acid and trisodium citrate variants",
    ]
    if not inventory["species"]:
        caveats.append("no citrate acid/base components detected")
    prediction_error = None
    if measured_pH is not None and predicted_pH is not None:
        prediction_error = measured_pH - predicted_pH
    buffer_capacity = None
    window = None
    degradation = None
    preservative = None
    alpha = None
    if effective_pH is not None:
        alpha = citrate_alpha_fractions(effective_pH)
        window = ph_window_check(effective_pH)
        degradation = degradation_vs_ph(effective_pH)
        preservative = preservative_active_fraction(effective_pH)
        if predicted_pH is not None:
            buffer_capacity = _buffer_shift_report(predicted_pH, citrate_mol_l, cation_mol_l)
    dilution = None
    if dilution_water_ml is not None:
        if dilution_water_ml <= water_ml:
            caveats.append("dilution_water_ml must exceed water_ml to model dilution; skipped dilution branch")
        else:
            diluted = citrate_ph_report(
                components,
                dilution_water_ml,
                measured_pH=None,
                use_case=f"{use_case}_diluted",
            )
            dilution = {
                "from_water_ml": water_ml,
                "to_water_ml": dilution_water_ml,
                "dilution_factor": dilution_water_ml / water_ml,
                "predicted_pH": diluted["predicted_pH"],
                "total_citrate_mmol_per_l": diluted["inventory"]["total_citrate_mmol_per_l"],
                "buffer_capacity": diluted["buffer_capacity"],
                "window": diluted["window"],
                "preservative_active_fraction": diluted["preservative_active_fraction"],
            }
    return {
        "use_case": use_case,
        "predicted_pH": predicted_pH,
        "effective_pH": effective_pH,
        "measured_pH": measured_pH,
        "prediction_error_pH": prediction_error,
        "solver_status": solver_status,
        "inventory": inventory,
        "alpha_fractions_at_effective_pH": alpha,
        "buffer_capacity": buffer_capacity,
        "window": window,
        "degradation": degradation,
        "preservative_active_fraction": preservative,
        "dilution": dilution,
        "confidence": "low_to_moderate_screening" if predicted_pH is not None else "not_predicted",
        "caveats": caveats,
    }


def ph_window_check(
    target_pH: float,
    low: float = 3.0,
    high: float = 4.0,
) -> dict:
    """
    Check whether target_pH falls inside the product's target window [low, high].

    Parameters
    ----------
    target_pH : pH to evaluate
    low       : lower bound (default 3.0)
    high      : upper bound (default 4.0)

    Returns
    -------
    dict with keys:
        in_window  : bool
        target_pH  : float
        low        : float
        high       : float
        reason     : str  — human-readable explanation
    """
    in_window = low <= target_pH <= high
    if in_window:
        reason = (
            f"pH {target_pH} is within the target window [{low}, {high}]. "
            "Citric acid buffers effectively here; ascorbate and Maillard stability are optimised."
        )
    elif target_pH < low:
        reason = (
            f"pH {target_pH} is below the lower bound {low}. "
            "Acidity may impair palatability and accelerate metal corrosion in equipment."
        )
    else:
        reason = (
            f"pH {target_pH} is above the upper bound {high}. "
            "Ascorbate oxidation and Maillard browning risks rise above pH 4.0."
        )
    return {
        "in_window": in_window,
        "target_pH": target_pH,
        "low": low,
        "high": high,
        "reason": reason,
    }


def degradation_vs_ph(target_pH: float) -> dict:
    """
    Qualitative degradation guidance at target_pH for key stability concerns.

    Covers:
    - Ascorbate (vitamin C) oxidation: pKa1 ≈ 4.17; most stable at pH 2.5–3.0,
      oxidation rate peaks near pH 4 and above.
    - Maillard browning: negligible below pH 4, rises significantly above pH 5.
    - Combined recommendation for this product's pH 3.0–4.0 target window.

    Parameters
    ----------
    target_pH : pH to evaluate

    Returns
    -------
    dict with keys:
        ascorbate_oxidation    : str  — qualitative rate description
        maillard_browning      : str  — qualitative risk description
        combined_recommendation: str  — overall stability guidance
    """
    # Ascorbate guidance
    if target_pH < 3.0:
        ascorbate = (
            "Very low — below pH 3.0 ascorbate is predominantly in its protonated "
            "ascorbic acid form (pKa1 ≈ 4.17), which is the most oxidatively stable species."
        )
    elif 3.0 <= target_pH <= 4.0:
        ascorbate = (
            "Low to moderate — pH 3.0–4.0 keeps most ascorbate as ascorbic acid "
            "(pKa1 ≈ 4.17 not yet crossed). Oxidation is slower than at neutral pH "
            "but increases toward the upper end of this range."
        )
    elif 4.0 < target_pH <= 5.0:
        ascorbate = (
            "Moderate to high — approaching and crossing pKa1 ≈ 4.17 means more "
            "ascorbate anion is present, which oxidises significantly faster than "
            "the protonated form."
        )
    else:
        ascorbate = (
            "High — above pH 5.0 ascorbate is mostly deprotonated and highly "
            "susceptible to oxidative degradation; metal catalysis is also enhanced."
        )

    # Maillard guidance
    if target_pH < 4.0:
        maillard = (
            "Negligible — Maillard browning requires pH ≥ 4 for meaningful reaction "
            "rates; acidic conditions protonate amino groups and suppress the reaction."
        )
    elif 4.0 <= target_pH < 5.0:
        maillard = (
            "Low — Maillard browning begins to become possible near pH 4; still "
            "suppressed relative to neutral pH but worth monitoring."
        )
    else:
        maillard = (
            "Rising — above pH 5.0 Maillard browning accelerates substantially, "
            "especially with reducing sugars present."
        )

    # Combined
    if 3.0 <= target_pH <= 4.0:
        combined = (
            "pH 3.0–4.0 is the optimal stability window for this formula. "
            "Ascorbate is predominantly in its stable protonated form, and "
            "Maillard browning is negligible. Citric acid provides robust "
            "buffering across pKa1 (3.13) and toward pKa2 (4.76)."
        )
    elif target_pH < 3.0:
        combined = (
            f"pH {target_pH} is below the recommended window. Ascorbate stability "
            "is excellent but formula acidity may cause palatability and "
            "packaging-compatibility concerns."
        )
    else:
        combined = (
            f"pH {target_pH} is above the recommended window. Both ascorbate "
            "oxidation risk and potential Maillard browning are elevated; "
            "consider increasing citric acid to bring pH into 3.0–4.0."
        )

    return {
        "ascorbate_oxidation": ascorbate,
        "maillard_browning": maillard,
        "combined_recommendation": combined,
    }


if __name__ == "__main__":
    import json

    TARGET = 3.5

    print(f"=== ph_module smoke test  (target_pH={TARGET}) ===\n")

    print("1. henderson_hasselbalch(pH=3.5, pKa=3.13):")
    print(json.dumps(henderson_hasselbalch(TARGET, 3.13), indent=2))

    print("\n2. citrate_buffer_ratio(3.5):")
    print(json.dumps(citrate_buffer_ratio(TARGET), indent=2))

    print("\n3. ph_window_check(3.5):")
    print(json.dumps(ph_window_check(TARGET), indent=2))

    print("\n4. degradation_vs_ph(3.5):")
    print(json.dumps(degradation_vs_ph(TARGET), indent=2))

    print("\n5. citrate_ph_report(dry stick in 1 L):")
    print(json.dumps(citrate_ph_report([
        ("citric_acid", 0.7),
        ("trisodium_citrate", 0.3),
    ], water_ml=1000.0), indent=2))
