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
"""

from __future__ import annotations

import math
from typing import Any

from compat.data import DEGRADATION_EA_J_PER_MOL

# Universal gas constant (J / mol / K)
_R: float = 8.314


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
