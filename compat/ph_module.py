"""
ph_module.py — pH / buffer chemistry helpers for the gamefowl supplement compat calculator.

All functions are pure and immutable (return new dicts, never mutate inputs).
Target product pH window: 3.0 – 4.0.
"""

from __future__ import annotations

from compat.data import SUBSTANCES

_CITRIC_PKA: list[float] = SUBSTANCES["citric_acid"]["pka"]  # [3.13, 4.76, 6.40]


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
