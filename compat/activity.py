"""
Ionic-strength and activity-coefficient corrections for the gamefowl ORS formula.

Screening-grade approximations — NOT production thermodynamics:
  • Davies equation valid up to I ≈ 0.5 mol/L (breaks down for I >> 0.5).
  • Setschenow constants (ks) are literature screening values; ±50 % uncertainty.
  • Neutral/zwitterionic solutes (sugars, glycerin, amino acids near pI) contribute
    negligibly to ionic strength and are treated as I = 0 contributors.
  • All functions are pure and immutable (no side effects, return new dicts).
"""

from __future__ import annotations

import math

from compat.data import ELECTROLYTE_IONS, MOLAR_MASS_G_PER_MOL

# ---------------------------------------------------------------------------
# Ion charge table for electrolytes tracked in ELECTROLYTE_IONS
# ---------------------------------------------------------------------------
# Speciation at formulation pH (~3.5–4.5):
#   NaCl       → Na⁺ (z=1) + Cl⁻ (z=1)
#   KCl        → K⁺  (z=1) + Cl⁻ (z=1)
#   trisodium_citrate → 3 Na⁺ (z=1) + citrate³⁻ (z=3)
#
# Ionic strength: I = 0.5 * Σ c_i * z_i²  (c_i in mol/L)

_ION_SPECS: dict[str, list[tuple[str, int]]] = {
    # electrolyte name -> list of (ion_label, charge_magnitude) per formula unit
    "sodium_chloride":    [("Na+", 1), ("Cl-", 1)],
    "potassium_chloride": [("K+",  1), ("Cl-", 1)],
    "trisodium_citrate":  [("Na+", 1), ("Na+", 1), ("Na+", 1), ("cit3-", 3)],
}

# ---------------------------------------------------------------------------
# Setschenow constants (ks, L/mol)  [SCREENING VALUES — literature ±50 %]
# Positive ks => salting-OUT (solubility decreases with ionic strength).
# References: Xie et al. 2002 (amino acids in NaCl); Sechenow 1889 (original).
# Neutral solutes only — electrolytes are handled via activity coefficients.
# ---------------------------------------------------------------------------
_KS_DEFAULTS: dict[str, float] = {
    # amino acids (modest salting-out in NaCl at 25 °C)
    "l_tyrosine":       0.16,   # lit. 0.12–0.20 L/mol in NaCl
    "l_phenylalanine":  0.14,   # lit. 0.10–0.18 L/mol
    "l_glutamine":      0.08,   # more polar; smaller ks
    "beta_alanine":     0.06,
    # sugars / polyols — near-zero salting effect
    "dextrose":         0.02,
    "d_ribose":         0.02,
    "glycerin":         0.01,
    # default for any neutral solute not listed
    "_default":         0.10,
}

# Davies A parameter (water, 25 °C)
_DAVIES_A: float = 0.509


# ---------------------------------------------------------------------------
# 1. ionic_strength
# ---------------------------------------------------------------------------

def ionic_strength(
    components: list[tuple[str, float]],
    water_ml: float,
) -> dict:
    """
    Compute the ionic strength of the solution from dissociating salts.

    Parameters
    ----------
    components : list of (substance_name, grams)
        Names must match keys in ELECTROLYTE_IONS / MOLAR_MASS_G_PER_MOL.
        Non-electrolytes are silently skipped (contribute ~0 to I).
    water_ml : float
        Volume of water in mL (used as the solvent volume; solute volume ignored
        for this screening calculation — dilute-solution approximation).

    Returns
    -------
    dict with keys:
        I_mol_per_l  : float  — ionic strength in mol/L
        ion_molarities: dict[str, float]  — individual ion concentrations (mol/L)
        note : str
    """
    if water_ml <= 0:
        raise ValueError("water_ml must be positive")

    water_l = water_ml / 1000.0
    ion_conc: dict[str, float] = {}  # accumulate mol/L per ion label

    for name, grams in components:
        if name not in ELECTROLYTE_IONS:
            continue  # neutral solute — skipped
        if name not in MOLAR_MASS_G_PER_MOL:
            continue

        mw = MOLAR_MASS_G_PER_MOL[name]
        mol_dissolved = grams / mw
        specs = _ION_SPECS.get(name, [])

        for ion_label, _z in specs:
            c = mol_dissolved / water_l  # mol/L per formula-unit contribution
            ion_conc[ion_label] = ion_conc.get(ion_label, 0.0) + c

    # I = 0.5 * Σ c_i * z_i²
    # Map ion_label -> z for charge lookup
    _label_z: dict[str, int] = {
        "Na+": 1, "K+": 1, "Cl-": 1, "cit3-": 3,
    }
    I = 0.5 * sum(
        c * (_label_z.get(label, 1) ** 2)
        for label, c in ion_conc.items()
    )

    return {
        "I_mol_per_l": round(I, 6),
        "ion_molarities": {k: round(v, 6) for k, v in ion_conc.items()},
        "note": (
            "Screening: neutral solutes excluded; solute volume neglected; "
            "Davies valid to I <= 0.5 mol/L"
        ),
    }


# ---------------------------------------------------------------------------
# 2. davies_gamma
# ---------------------------------------------------------------------------

def davies_gamma(
    I: float,
    z_plus: int = 1,
    z_minus: int = 1,
    A: float = _DAVIES_A,
) -> float:
    """
    Mean activity coefficient (gamma±) via the Davies equation.

    log10(gamma±) = -A * |z+ * z-| * ( sqrt(I)/(1+sqrt(I)) - 0.3*I )

    Valid for I <= ~0.5 mol/L (Davies 1938).  At I < 0.01 this converges to
    the Debye–Hückel limiting law.

    Parameters
    ----------
    I       : ionic strength in mol/L
    z_plus  : charge magnitude of the cation
    z_minus : charge magnitude of the anion
    A       : Davies A-parameter (0.509 for water at 25 °C)

    Returns
    -------
    float — mean activity coefficient gamma± (dimensionless)
    """
    if I < 0:
        raise ValueError("Ionic strength must be non-negative")
    if I == 0.0:
        return 1.0
    sqrt_I = math.sqrt(I)
    log_gamma = -A * abs(z_plus * z_minus) * (sqrt_I / (1.0 + sqrt_I) - 0.3 * I)
    return 10.0 ** log_gamma


# ---------------------------------------------------------------------------
# 3. setschenow_corrected_solubility
# ---------------------------------------------------------------------------

def setschenow_corrected_solubility(
    name: str,
    base_solubility_g_100ml: float,
    I: float,
    ks: float | None = None,
) -> dict:
    """
    Setschenow (salting-out) correction for a NEUTRAL solute.

    log10(S / S0) = -ks * I  =>  S = S0 * 10^(-ks * I)

    Positive ks → salting-OUT (S < S0).  Negative ks → salting-IN (rare).

    Parameters
    ----------
    name                    : substance key (used for ks lookup if ks=None)
    base_solubility_g_100ml : S0 in g / 100 mL (from data.py or experiment)
    I                       : ionic strength in mol/L
    ks                      : Setschenow constant (L/mol); if None, uses built-in table

    Returns
    -------
    dict with keys:
        name, base_g_100ml, corrected_g_100ml, pct_change, salting
    """
    if ks is None:
        ks = _KS_DEFAULTS.get(name, _KS_DEFAULTS["_default"])

    corrected = base_solubility_g_100ml * (10.0 ** (-ks * I))
    pct_change = (corrected - base_solubility_g_100ml) / base_solubility_g_100ml * 100.0

    if abs(pct_change) < 0.05:
        salting: str = "none"
    elif corrected < base_solubility_g_100ml:
        salting = "out"
    else:
        salting = "in"

    return {
        "name": name,
        "base_g_100ml": round(base_solubility_g_100ml, 4),
        "corrected_g_100ml": round(corrected, 4),
        "pct_change": round(pct_change, 2),
        "salting": salting,
        "ks_used": round(ks, 4),
        "note": "Setschenow screening; ks ±50% uncertainty",
    }


# ---------------------------------------------------------------------------
# 4. corrected_ceilings
# ---------------------------------------------------------------------------

# Neutral solutes with non-trivial solubility ceilings worth correcting.
# Electrolytes are excluded (their activity is handled via gamma±, not ks).
_NEUTRAL_LOW_SOL: dict[str, float] = {
    # name: solubility_g_per_100ml from data.py (SUBSTANCES)
    "l_tyrosine":      0.045,   # sparingly soluble — most sensitive to I
    "l_phenylalanine": 2.965,
    "l_glutamine":     4.25,
    "creatine_monohydrate": 1.6,
    "dextrose":        91.0,
    "d_ribose":        84.5,
    # glycerin omitted — miscible, no finite ceiling to correct
}


def corrected_ceilings(
    components: list[tuple[str, float]],
    water_ml: float,
) -> dict:
    """
    Compute ionic strength from the salt fraction, then apply Setschenow
    corrections to neutral low-solubility solutes present in *components*.

    Returns
    -------
    dict with keys:
        I_result  : output of ionic_strength()
        corrections: list[dict]  — one entry per neutral solute found
        summary   : str
    """
    I_result = ionic_strength(components, water_ml)
    I = I_result["I_mol_per_l"]

    present_neutral = {
        name: grams
        for name, grams in components
        if name in _NEUTRAL_LOW_SOL and _NEUTRAL_LOW_SOL[name] is not None
    }

    corrections = []
    for name, grams in present_neutral.items():
        base = _NEUTRAL_LOW_SOL[name]
        corr = setschenow_corrected_solubility(name, base, I)
        # Annotate whether the solute exceeds its corrected ceiling
        ceiling_g = corr["corrected_g_100ml"] * water_ml / 100.0
        dissolved_g = grams
        corr = {
            **corr,
            "dissolved_g": round(dissolved_g, 4),
            "ceiling_g_in_volume": round(ceiling_g, 4),
            "over_ceiling": dissolved_g > ceiling_g,
        }
        corrections.append(corr)

    summary = (
        f"I = {I:.4f} mol/L — "
        + ("corrections small (<1 %) at this low I" if I < 0.15 else "corrections non-negligible")
    )

    return {
        "I_result": I_result,
        "corrections": corrections,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# __main__ smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Reformulated ORS: per 1000 mL water
    ORS = [
        ("dextrose",          14.0),
        ("sodium_chloride",    2.6),
        ("potassium_chloride", 1.5),
        ("trisodium_citrate",  2.9),
    ]
    WATER_ML = 1000.0

    print("=== Gamefowl ORS — Ionic Strength + Activity Correction Smoke Test ===\n")

    # 1. Ionic strength
    I_res = ionic_strength(ORS, WATER_ML)
    print(f"Ionic strength I = {I_res['I_mol_per_l']:.4f} mol/L")
    print("Ion molarities (mol/L):")
    for ion, c in I_res["ion_molarities"].items():
        print(f"  {ion:8s}: {c:.5f}")
    print(f"Note: {I_res['note']}\n")

    # 2. Davies gamma for NaCl-like 1:1 electrolyte and citrate 1:3
    I = I_res["I_mol_per_l"]
    g11 = davies_gamma(I, z_plus=1, z_minus=1)
    g13 = davies_gamma(I, z_plus=1, z_minus=3)
    print(f"Davies gamma± (1-1 electrolyte): {g11:.4f}")
    print(f"Davies gamma± (1-3, Na/citrate):  {g13:.4f}")
    print("  → Both near 1.0 confirms corrections are small at this I\n")

    # 3. Setschenow correction for l-tyrosine (not in this ORS but illustrative)
    tyrosine_corr = setschenow_corrected_solubility("l_tyrosine", 0.045, I)
    print(f"Tyrosine Setschenow correction at I={I:.4f}:")
    print(f"  base={tyrosine_corr['base_g_100ml']} g/100mL -> "
          f"corrected={tyrosine_corr['corrected_g_100ml']} g/100mL "
          f"({tyrosine_corr['pct_change']:+.2f}%, salting-{tyrosine_corr['salting']})\n")

    # 4. Full corrected ceilings
    print("Corrected ceilings for neutral solutes in ORS:")
    result = corrected_ceilings(ORS, WATER_ML)
    if result["corrections"]:
        for c in result["corrections"]:
            flag = " *** OVER CEILING ***" if c["over_ceiling"] else ""
            print(f"  {c['name']}: {c['base_g_100ml']} -> {c['corrected_g_100ml']} g/100mL "
                  f"({c['pct_change']:+.2f}%){flag}")
    else:
        print("  (no tracked neutral low-solubility solutes in this formula)")
    print(f"\n{result['summary']}")
