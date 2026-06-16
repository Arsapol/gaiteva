"""
stokes.py — Stokes settling velocity calculator for gamefowl supplement suspensions.

Physical model
--------------
Stokes' law (creeping-flow regime, Re << 1):

    v = 2 r² (ρ_p − ρ_f) g / (9 η)

where
    r      particle radius [m]
    ρ_p    particle (crystal) density [kg/m³]
    ρ_f    fluid density [kg/m³]  — default 1000 (water-like)
    η      dynamic viscosity [Pa·s]
    g      9.81 m/s²

v > 0 → particle settles (sinks)
v < 0 → particle creams (floats)

Amino-acid crystal density assumption
--------------------------------------
When a substance entry in SUBSTANCES has density_kg_m3 = None, a default
of 1400 kg/m³ is used (midpoint of the 1300–1500 kg/m³ range typical of
amino-acid crystals; documented here and in each call site via the
``rho_p`` argument).

All functions are pure and return new objects — no mutation.
"""

from __future__ import annotations

import math
from typing import Final

from compat.data import SUBSTANCES

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
_G: Final[float] = 9.81          # m/s²
_RHO_FLUID_DEFAULT: Final[float] = 1000.0   # kg/m³  (water at 25 °C)
_RHO_CRYSTAL_DEFAULT: Final[float] = 1400.0  # kg/m³  (mid amino-acid crystal range)


# ---------------------------------------------------------------------------
# Core Stokes functions
# ---------------------------------------------------------------------------

def stokes_velocity(
    r_m: float,
    rho_p: float,
    rho_f: float,
    eta: float,
) -> float:
    """Return Stokes terminal velocity [m/s].

    Parameters
    ----------
    r_m   : particle radius [m]
    rho_p : particle density [kg/m³]
    rho_f : fluid density [kg/m³]
    eta   : dynamic viscosity [Pa·s]

    Returns
    -------
    v [m/s]; positive → settling, negative → creaming, zero → neutrally buoyant.

    Raises
    ------
    ValueError if r_m < 0, eta <= 0.
    """
    if r_m < 0:
        raise ValueError(f"r_m must be >= 0, got {r_m}")
    if eta <= 0:
        raise ValueError(f"eta must be > 0, got {eta}")
    return (2.0 * r_m**2 * (rho_p - rho_f) * _G) / (9.0 * eta)


def settle_time(v_m_s: float, height_m: float) -> float:
    """Return time [s] for a particle to traverse height_m at velocity v_m_s.

    Parameters
    ----------
    v_m_s    : Stokes velocity [m/s] (positive for settling, negative for creaming)
    height_m : column height [m]

    Returns
    -------
    Seconds to traverse the column; math.inf if v_m_s == 0.

    Raises
    ------
    ValueError if height_m < 0.
    """
    if height_m < 0:
        raise ValueError(f"height_m must be >= 0, got {height_m}")
    if v_m_s == 0.0:
        return math.inf
    return abs(height_m / v_m_s)


# ---------------------------------------------------------------------------
# Solubility gate helpers
# ---------------------------------------------------------------------------

def undissolved_grams(name: str, dose_g: float, water_ml: float) -> float:
    """Return the undissolved fraction [g] of *name* given dose_g in water_ml.

    Uses the solubility ceiling from SUBSTANCES[name]['solubility_g_per_100ml_25c'].
    If solubility is None, returns 0.0 (assume fully dissolved — conservative).

    Parameters
    ----------
    name     : substance key as in SUBSTANCES (e.g. "tyrosine")
    dose_g   : total grams added
    water_ml : volume of water [mL]

    Returns
    -------
    Grams that remain undissolved (>= 0).
    """
    entry = SUBSTANCES.get(name)
    if entry is None:
        raise KeyError(f"'{name}' not found in SUBSTANCES")

    sol = entry.get("solubility_g_per_100ml_25c")
    if sol is None:
        return 0.0  # unknown ceiling → assume dissolved (conservative)

    ceiling_g = sol * (water_ml / 100.0)
    excess = dose_g - ceiling_g
    return max(0.0, excess)


# ---------------------------------------------------------------------------
# High-level settling report
# ---------------------------------------------------------------------------

def settling_report(
    name: str,
    dose_g: float,
    water_ml: float,
    particle_radius_m: float,
    eta_pa_s: float,
    bottle_height_m: float = 0.1,
) -> dict:
    """Return a settling analysis dict for one supplement in solution.

    Gate: if the dose is fully within solubility, particles do not exist
    and Stokes analysis is not applicable.

    Parameters
    ----------
    name              : substance key in SUBSTANCES (e.g. "tyrosine")
    dose_g            : grams of substance added
    water_ml          : water volume [mL]
    particle_radius_m : assumed undissolved particle radius [m]
    eta_pa_s          : dynamic viscosity of the suspension [Pa·s]
                        (pure water ≈ 0.001; glycerin addition raises this)
    bottle_height_m   : liquid column height to compute settle_time [m]

    Returns
    -------
    dict with keys:
        applicable (bool)
        reason (str)
        undissolved_g (float)
        v (float)                     — Stokes velocity [m/s]; 0 if not applicable
        settle_time_s (float | None)  — seconds; inf if v==0; None if not applicable
        reduce_radius_effect (str)    — qualitative note (always present)
        raise_viscosity_effect (str)  — qualitative note (always present)
    """
    entry = SUBSTANCES.get(name)
    if entry is None:
        raise KeyError(f"'{name}' not found in SUBSTANCES")

    undissolved = undissolved_grams(name, dose_g, water_ml)

    _radius_note = (
        "Halving particle radius (e.g. via fine grinding) reduces settling "
        "velocity by 4× (v ∝ r²)."
    )
    _viscosity_note = (
        "Doubling viscosity (e.g. adding glycerin) halves settling velocity "
        "(v ∝ 1/η). Glycerin at 5–10 % v/v is a practical strategy."
    )

    if undissolved == 0.0:
        return {
            "applicable": False,
            "reason": "fully in solution; no particles to settle",
            "undissolved_g": 0.0,
            "v": 0.0,
            "settle_time_s": None,
            "reduce_radius_effect": _radius_note,
            "raise_viscosity_effect": _viscosity_note,
        }

    # Particle density: use substance value or amino-acid crystal default
    rho_p: float = entry.get("density_kg_m3") or _RHO_CRYSTAL_DEFAULT

    v = stokes_velocity(
        r_m=particle_radius_m,
        rho_p=rho_p,
        rho_f=_RHO_FLUID_DEFAULT,
        eta=eta_pa_s,
    )
    t = settle_time(v_m_s=v, height_m=bottle_height_m)

    return {
        "applicable": True,
        "reason": f"{undissolved:.4f} g undissolved (above solubility ceiling)",
        "undissolved_g": undissolved,
        "v": v,
        "settle_time_s": t,
        "reduce_radius_effect": _radius_note,
        "raise_viscosity_effect": _viscosity_note,
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pprint

    print("=== Example 1: L-Tyrosine OVER ceiling (0.5 g in 50 mL) ===")
    report_over = settling_report(
        name="l_tyrosine",
        dose_g=0.5,
        water_ml=50.0,
        particle_radius_m=50e-6,   # 50 µm crystal
        eta_pa_s=0.001,            # pure water
        bottle_height_m=0.10,
    )
    pprint.pprint(report_over)

    print()
    print("=== Example 2: Ascorbic acid FULLY dissolved (0.5 g in 50 mL) ===")
    report_dissolved = settling_report(
        name="ascorbic_acid",
        dose_g=0.5,
        water_ml=50.0,
        particle_radius_m=50e-6,
        eta_pa_s=0.001,
        bottle_height_m=0.10,
    )
    pprint.pprint(report_dissolved)
