"""
Water activity (aw) screening estimator for aqueous gamefowl ORS supplements.

SCIENCE NOTES
-------------
Raoult's Law (default, dilute-solution screening):
    aw ≈ x_water = n_water / (n_water + Σ n_solute_particles)
where n_solute_particles counts dissociated species via OSMOTIC_N.
Assumption: full dissociation of all solutes; ideal solution behaviour.
This OVERESTIMATES aw relative to true values (lower bound of depression).

Norrish correction (optional refinement for dominant non-electrolyte):
    ln(aw) = ln(x_water) - K * x_solute²
K factors (Norrish 1966): sucrose ~2.6, glucose ~1.0, glycerol ~1.16.
More accurate for concentrated sugar/polyol solutions; negligible at <5% w/v.

FDA / food-micro aw thresholds (screening only):
    aw > 0.95  → supports most bacteria incl. many pathogens
    aw ≤ 0.95  → restricts some pathogens (e.g. C. botulinum non-proteolytic)
    aw ≤ 0.91  → limits most bacteria
    aw ≤ 0.85  → regulatory control threshold (21 CFR part 114)
    aw ≤ 0.60  → no microbial growth

A dilute ORS (aw ~0.98-0.99) requires a validated preservative system,
micro spec, and challenge test regardless of pH. aw alone does NOT confer
shelf stability.
"""

from __future__ import annotations

import math
from typing import NamedTuple

from compat.data import MOLAR_MASS_G_PER_MOL, OSMOTIC_N

_WATER_MW: float = 18.015  # g/mol

# Norrish K constants for common non-electrolytes
NORRISH_K: dict[str, float] = {
    "sucrose": 2.6,
    "dextrose": 1.0,      # glucose screening value
    "d_ribose": 1.0,      # pentose, use glucose proxy
    "glycerin": 1.16,
    "glycerol": 1.16,
}


class MoleFractionResult(NamedTuple):
    x_water: float
    n_water_mol: float
    n_solute_particles_mol: float
    unknown_mw: list[str]


def mole_fraction_water(
    components: list[tuple[str, float]],
    water_ml: float,
) -> MoleFractionResult:
    """Return mole-fraction of water and particle counts for an aqueous solution.

    Parameters
    ----------
    components:
        List of (substance_name, mass_g) pairs. Names must match
        MOLAR_MASS_G_PER_MOL / OSMOTIC_N keys (lowercase).
    water_ml:
        Volume of water in mL (assumed density 1.0 g/mL → mass = water_ml g).

    Returns
    -------
    MoleFractionResult with fields:
        x_water                  – mole fraction of water (Raoult aw)
        n_water_mol              – moles of water
        n_solute_particles_mol   – total osmotically-active moles of solute
        unknown_mw               – substance names missing from MOLAR_MASS lookup

    Assumptions
    -----------
    - Full dissociation of all solutes (OSMOTIC_N at face value).
    - Water density = 1.000 g/mL; solute volume neglected.
    - Ideal solution (Raoult); no activity coefficients.
    """
    n_water = water_ml / _WATER_MW  # g / (g/mol)

    total_solute_particles: float = 0.0
    unknown: list[str] = []

    for name, mass_g in components:
        mw = MOLAR_MASS_G_PER_MOL.get(name)
        n_osmotic = OSMOTIC_N.get(name, 1.0)
        if mw is None:
            unknown.append(name)
            continue
        n_mol = mass_g / mw
        total_solute_particles += n_mol * n_osmotic

    total_mol = n_water + total_solute_particles
    x_water = n_water / total_mol if total_mol > 0 else 1.0

    return MoleFractionResult(
        x_water=x_water,
        n_water_mol=n_water,
        n_solute_particles_mol=total_solute_particles,
        unknown_mw=unknown,
    )


def raoult_aw(
    components: list[tuple[str, float]],
    water_ml: float,
) -> float:
    """Return Raoult-law screening estimate of water activity (= x_water).

    This is a dilute-ideal approximation. It OVERESTIMATES aw for concentrated
    solutions (underestimates aw depression). Labelled 'screening'.
    """
    result = mole_fraction_water(components, water_ml)
    return result.x_water


def norrish_aw(x_water: float, x_solute: float, K: float) -> float:
    """Return Norrish-corrected aw for a single dominant non-electrolyte.

    ln(aw) = ln(x_water) - K * x_solute²

    Parameters
    ----------
    x_water:
        Mole fraction of water (from mole_fraction_water).
    x_solute:
        Mole fraction of the target non-electrolyte solute.
    K:
        Norrish constant for that solute (see NORRISH_K).

    Returns
    -------
    float – corrected aw. Refinement only; single-solute approximation.
    """
    ln_aw = math.log(x_water) - K * x_solute**2
    return math.exp(ln_aw)


def _microbial_class(aw: float) -> tuple[str, str]:
    """Map aw to FDA/food-micro microbial class and threshold note."""
    if aw > 0.95:
        cls = "HIGH_RISK"
        note = (
            "aw > 0.95: supports most bacteria incl. many pathogens. "
            "Requires preservative system, micro spec, and challenge test."
        )
    elif aw > 0.91:
        cls = "MODERATE_RISK"
        note = (
            "0.91 < aw ≤ 0.95: restricts some pathogens; "
            "many spoilage and pathogenic bacteria can still grow."
        )
    elif aw > 0.85:
        cls = "CONTROLLED"
        note = (
            "0.85 < aw ≤ 0.91: most bacteria inhibited; "
            "mould/yeast still possible. Monitor for xerophiles."
        )
    elif aw > 0.60:
        cls = "REGULATORY_THRESHOLD"
        note = (
            "aw ≤ 0.85: FDA 21 CFR §114 intermediate-acid food threshold. "
            "Most pathogens inhibited; xerophilic moulds still possible."
        )
    else:
        cls = "SHELF_STABLE_AW"
        note = "aw ≤ 0.60: no microbial growth expected by aw alone."
    return cls, note


def aw_report(
    components: list[tuple[str, float]],
    water_ml: float,
) -> dict:
    """Return a screening aw report dict for an aqueous ORS formulation.

    Keys
    ----
    aw_raoult         – Raoult screening estimate (float)
    microbial_class   – FDA/food-micro risk tier string
    threshold_note    – human-readable note on the risk tier
    preservation_flag – mandatory advisory for high-aw aqueous products
    unknown_mw        – substances skipped due to missing molar mass (list)

    The Raoult path is a dilute-ideal screening approximation. For dominant
    sugars/polyols, use norrish_aw() as an optional refinement.
    """
    result = mole_fraction_water(components, water_ml)
    aw = result.x_water
    cls, note = _microbial_class(aw)

    preservation_flag = (
        "REQUIRED: This is a high-aw aqueous product. "
        "A validated preservative system (antimicrobial agent or hurdle combination), "
        "microbiological specification, and challenge test per FDA/ICH guidelines "
        "are MANDATORY regardless of pH. aw screening does NOT confer shelf stability."
    )

    return {
        "aw_raoult": round(aw, 6),
        "microbial_class": cls,
        "threshold_note": note,
        "preservation_flag": preservation_flag,
        "unknown_mw": result.unknown_mw,
    }


if __name__ == "__main__":
    # Smoke test — reformulated gamefowl ORS per 1000 mL water
    ORS_COMPONENTS: list[tuple[str, float]] = [
        ("dextrose", 14.0),
        ("sodium_chloride", 2.6),
        ("potassium_chloride", 1.5),
        ("trisodium_citrate", 2.9),
        ("ascorbic_acid", 0.5),
        ("beta_alanine", 1.0),
        ("d_ribose", 2.0),
    ]
    WATER_ML = 1000.0

    mfr = mole_fraction_water(ORS_COMPONENTS, WATER_ML)
    report = aw_report(ORS_COMPONENTS, WATER_ML)

    print("=== Water Activity Screening Report ===")
    print(f"  n_water_mol              : {mfr.n_water_mol:.4f} mol")
    print(f"  n_solute_particles_mol   : {mfr.n_solute_particles_mol:.4f} mol")
    print(f"  aw (Raoult screening)    : {report['aw_raoult']:.6f}")
    print(f"  microbial_class          : {report['microbial_class']}")
    print(f"  threshold_note           : {report['threshold_note']}")
    print(f"  preservation_flag        : {report['preservation_flag']}")
    if report["unknown_mw"]:
        print(f"  unknown_mw (skipped)     : {report['unknown_mw']}")

    # Optional Norrish refinement for dextrose (dominant sugar)
    dextrose_mol = 14.0 / MOLAR_MASS_G_PER_MOL["dextrose"]
    x_dextrose = dextrose_mol / (mfr.n_water_mol + mfr.n_solute_particles_mol)
    aw_norrish = norrish_aw(mfr.x_water, x_dextrose, NORRISH_K["dextrose"])
    print(f"\n  Norrish refinement (dextrose, K=1.0): aw = {aw_norrish:.6f}")
    print("  (negligible correction at this dilution — Raoult sufficient)")
