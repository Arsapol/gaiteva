"""
Gamefowl supplement compatibility calculator — physical-chemistry constants.

Provenance
----------
SUBSTANCES values are extracted directly from the substance-*.md dossiers in
.omc/wiki/ (as of 2026-06-16).  Where a dossier explicitly quotes a numeric
value from a cited source, that source is reproduced in the 'note' field.
Where a dossier gives only qualitative guidance (e.g. "very soluble") or the
property is not discussed, well-known literature values are used and the note
is tagged "literature" to distinguish them from dossier-sourced figures.
None of the values in this module are inferred or guessed silently.

Keys
----
Each entry in SUBSTANCES has:
    solubility_g_per_100ml_25c : float | None
        Water solubility at 25 °C in g / 100 mL.
        None  → not found in dossier or literature.
    density_kg_m3 : float | None
        Bulk/solid density in kg/m³.
        None  → not found.
    pka : list[float]
        Acid dissociation constants (thermodynamic, 25 °C).
        Empty list [] → not applicable (e.g. non-electrolyte, no ionisable
        group in the formula pH range, or not found).
    note : str
        One-line provenance string.  "dossier" = extracted from wiki;
        "literature" = well-known reference value not in dossier.

Immutability
------------
Both module-level dicts are defined as plain dict literals. Callers MUST
NOT mutate them in place; treat as read-only constants.  If a mutable copy
is needed, use dict.copy() or copy.deepcopy().
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# SUBSTANCES
# ---------------------------------------------------------------------------
# Key: lowercase common name used throughout the codebase.
# Solubility is in g/100 mL (= g per 100 mL of water at 25 °C).
# pKa values are the macroscopic/thermodynamic values at 25 °C.
# ---------------------------------------------------------------------------

SUBSTANCES: dict[str, dict] = {

    "ascorbic_acid": {
        # Dossier: "~330 g/L" (R1 section) → 33 g/100 mL
        "solubility_g_per_100ml_25c": 33.0,
        "density_kg_m3": None,  # not in dossier
        "pka": [4.17, 11.57],   # literature; classic enol-diol pKa values
        "note": (
            "solubility dossier ~330 g/L; pKa literature (enol-diol 4.17/11.57)"
        ),
    },

    "beta_alanine": {
        # Dossier: "~550+ g/L" → >55 g/100 mL; use 55 as conservative floor
        "solubility_g_per_100ml_25c": 55.0,
        "density_kg_m3": None,
        "pka": [3.55, 10.24],   # literature (alpha-COOH / alpha-NH3+)
        "note": (
            "solubility dossier '>550 g/L' (floor 55 g/100 mL used); "
            "pKa literature"
        ),
    },

    "betaine_anhydrous": {
        # Dossier (verifier-confirmed): "~1600 g/L" → 160 g/100 mL
        "solubility_g_per_100ml_25c": 160.0,
        "density_kg_m3": None,
        "pka": [],              # quaternary-ammonium zwitterion, no ionisable proton in range
        "note": (
            "solubility dossier ~1600 g/L (ChemicalBook/ScienceDirect, Tier 2)"
        ),
    },

    "citric_acid": {
        # Dossier: "~59.2% w/w @20C (~1450 mg/mL)" → ~145 g/100 mL @20C;
        # literature @25C ~147 g/100 mL (Lange's Handbook)
        "solubility_g_per_100ml_25c": 147.0,
        "density_kg_m3": 1665.0,  # anhydrous, literature (USP/Sigma ~1.665 g/cm³)
        "pka": [3.13, 4.76, 6.40],  # dossier (Wikipedia/buffer refs, Tier 2)
        "note": (
            "solubility literature ~147 g/100 mL @25C; density literature; "
            "pKa dossier (pKa1 3.13 / pKa2 4.76 / pKa3 6.40)"
        ),
    },

    "copper_tbcc": {
        # TBCC = tribasic copper chloride Cu₂(OH)₃Cl; sparingly soluble powder
        # Dossier: "sparingly water-soluble as a powder; dissolves in gastric acid"
        # No numeric aqueous solubility given in dossier; literature ~0.0017 g/100 mL
        "solubility_g_per_100ml_25c": 0.0017,
        "density_kg_m3": 3760.0,  # literature (mineral atacamite-type, ~3.76 g/cm³)
        "pka": [],
        "note": (
            "TBCC; solubility literature (sparingly soluble; dossier gives no number); "
            "density literature"
        ),
    },

    "creatine_monohydrate": {
        # Dossier: "~13–17 g/L water (~25°C)" → 1.3–1.7 g/100 mL; midpoint 1.4
        "solubility_g_per_100ml_25c": 1.4,
        "density_kg_m3": 1330.0,  # literature (Sigma ~1.33 g/cm³)
        "pka": [2.63, 14.3],    # literature (COOH ~2.63; guanidinium >14)
        "note": (
            "solubility dossier 13–17 g/L @25C (midpoint 1.4 g/100 mL used); "
            "density literature; pKa literature"
        ),
    },

    "d_ribose": {
        # Dossier: "very soluble (~1000+ g/L)" → >100 g/100 mL
        "solubility_g_per_100ml_25c": 100.0,  # conservative floor
        "density_kg_m3": 1720.0,  # literature (~1.72 g/cm³)
        "pka": [],               # reducing sugar, no titratable pKa in range
        "note": (
            "solubility dossier '>1000 g/L' (floor 100 g/100 mL used); "
            "density literature"
        ),
    },

    "dextrose": {
        # Dossier: "~900 g/L (~91 g/100mL, 25°C)" — NIST cited
        "solubility_g_per_100ml_25c": 91.0,
        "density_kg_m3": 1560.0,  # literature anhydrous D-glucose (~1.56 g/cm³)
        "pka": [],
        "note": (
            "solubility dossier ~900 g/L = 91 g/100 mL @25C (NIST, Tier 1)"
        ),
    },

    "dmg": {
        # DMG (N,N-dimethylglycine). Dossier: "~50 mg/mL" = 5 g/100 mL
        "solubility_g_per_100ml_25c": 5.0,
        "density_kg_m3": 1069.0,  # dossier: "density 1.069" (ChemicalBook, Tier 2)
        "pka": [2.0, 9.9],       # dossier: "pKa COOH ~2.0, N-H+ ~9.9" (ChEBI)
        "note": (
            "solubility dossier ~50 mg/mL = 5 g/100 mL (Sigma-Aldrich D1156, Tier 2); "
            "density dossier 1.069 g/cm³; pKa dossier (ChEBI:58251)"
        ),
    },

    "glycerin": {
        # Dossier: "fully MISCIBLE with water in ALL proportions" → coded as None
        # with a very large effective value; use None and document in note.
        "solubility_g_per_100ml_25c": None,  # miscible in all proportions
        "density_kg_m3": 1261.0,  # dossier: "specific gravity ~1.261 (20C)" (USP)
        "pka": [],                # triol, no ionisable proton in formulation range
        "note": (
            "solubility: miscible with water in all proportions (USP monograph, Tier 1); "
            "density dossier ~1.261 g/cm³ @20C"
        ),
    },

    "gaa": {
        # Guanidinoacetic acid. Dossier (verifier-corrected): "~3.6 g/L" → 0.36 g/100 mL
        "solubility_g_per_100ml_25c": 0.36,
        "density_kg_m3": None,
        "pka": [2.82, 13.1],   # literature (COOH / guanidinium)
        "note": (
            "solubility dossier ~3.6 g/L @15C (corrected per verifier from 2.5 g/L; "
            "ChemicalBook, Tier 2); pKa literature"
        ),
    },

    "l_arginine": {
        # Dossier (free base): "~148.7 g/L = 14.87 g/100 mL @20C" (CRC Handbook, Tier 2)
        "solubility_g_per_100ml_25c": 14.87,
        "density_kg_m3": 1100.0,  # literature (~1.1 g/cm³)
        "pka": [2.17, 9.04, 12.48],  # dossier (CRC / Fitch 2015 canonical)
        "note": (
            "solubility dossier ~14.87 g/100 mL @20C (Wikipedia/CRC, Tier 2); "
            "density literature; pKa dossier (CRC textbook values)"
        ),
    },

    "l_carnitine_l_tartrate": {
        # LCLT. Dossier: ">1 g/mL = >100 g/100 mL" (ChemicalBook, Tier 2)
        "solubility_g_per_100ml_25c": 100.0,  # lower-bound (actual >> this)
        "density_kg_m3": None,
        "pka": [3.36, 4.09],   # literature: tartrate pKa1 2.89, pKa2 3.96;
                                 # carnitine carboxyl ~3.36; use dossier hint
                                 # "tartaric acid pKa1 2.89 vs carnitine carboxyl pKa 4.09"
        "note": (
            "solubility dossier '>1 g/mL' @20C = lower-bound 100 g/100 mL "
            "(ChemicalBook CB5141230, Tier 2); "
            "pKa from dossier (tartrate 2.89 / carnitine carboxyl 4.09)"
        ),
    },

    "l_glutamine": {
        # Dossier: "~36 mg/mL (~250 mM) neutral pH ~25C" = 3.6 g/100 mL
        "solubility_g_per_100ml_25c": 3.6,
        "density_kg_m3": None,
        "pka": [2.17, 9.13],   # literature (COOH / alpha-NH3+)
        "note": (
            "solubility dossier ~36 mg/mL @25C (Sigma/ChemicalBook, Tier 2); "
            "pKa literature"
        ),
    },

    "l_phenylalanine": {
        # Dossier (Tier 1): "~27.7 g/L @25C" (J. Chem. Eng. Japan 43(9):2010)
        "solubility_g_per_100ml_25c": 2.77,
        "density_kg_m3": 1290.0,  # literature (~1.29 g/cm³)
        "pka": [1.83, 9.13],   # dossier (alpha-COOH ~1.83, alpha-NH3+ ~9.13)
        "note": (
            "solubility dossier ~27.7 g/L @25C = 2.77 g/100 mL "
            "(J. Chem. Eng. Japan 43(9) DOI 10.1252/jcej.10we013, Tier 1); "
            "pKa dossier (Chegg/Vaia textbook set)"
        ),
    },

    "l_tyrosine": {
        # Dossier (Tier 2 Merck/Wikipedia): "~0.45 g/L = 0.045 g/100 mL @25C"
        "solubility_g_per_100ml_25c": 0.045,
        "density_kg_m3": 1456.0,  # literature (~1.456 g/cm³)
        "pka": [2.2, 9.1, 10.1],  # dossier (alpha-COOH / alpha-NH3+ / phenolic-OH)
        "note": (
            "solubility dossier ~0.45 g/L = 0.045 g/100 mL @25C "
            "(Merck Index / Wikipedia, Tier 2; pI ~5.6 = solubility minimum); "
            "density literature; pKa dossier"
        ),
    },

    # --- Electrolyte salts (ORS premix) — literature values -----------------
    "sodium_chloride": {
        "solubility_g_per_100ml_25c": 36.0,   # literature ~360 g/L
        "density_kg_m3": 2170.0,
        "pka": [],
        "note": "literature; ORS Na+/Cl- source",
    },
    "potassium_chloride": {
        "solubility_g_per_100ml_25c": 34.0,   # literature ~340 g/L
        "density_kg_m3": 1980.0,
        "pka": [],
        "note": "literature; ORS K+/Cl- source",
    },
    "trisodium_citrate": {
        # trisodium citrate dihydrate Na3C6H5O7·2H2O
        "solubility_g_per_100ml_25c": 42.0,   # very soluble (conservative)
        "density_kg_m3": 1700.0,
        "pka": [],                            # conjugate base; buffers with citric acid
        "note": "literature; ORS Na+ source + citrate buffer/base (dihydrate MW 294.1)",
    },

}

# ---------------------------------------------------------------------------
# DEGRADATION_EA_J_PER_MOL
# ---------------------------------------------------------------------------
# Activation energies for the three degradation pathways used by arrhenius.py.
# Tuples are (low_Ea, typical_Ea, high_Ea) in J/mol.
# Sources: physical-organic chemistry literature compiled during team research
# (2026-06-16).  The ranges reflect pH-dependence, ionic-strength variation,
# and source-to-source scatter.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# MOLAR_MASS_G_PER_MOL  +  OSMOTIC_N
# ---------------------------------------------------------------------------
# Needed to convert a dissolved mass (g/L) into an osmolarity contribution:
#     mOsm/L = (dissolved_g / L) / molar_mass * osmotic_n * 1000
# OSMOTIC_N = number of osmotically active particles released per molecule
# when DISSOLVED at the formulation pH (~3.0-4.0).
#   - Sugars, polyols, neutral/zwitterionic amino acids, weak acids that stay
#     largely undissociated at low pH  -> n = 1 (one particle per molecule).
#   - Salts that dissociate into a cation + an anion  -> n >= 2.
# These are screening approximations; partial dissociation of citric acid and
# the exact stoichiometry of LCLT shift the true value slightly. Marked in
# the note where non-obvious.  Values are literature molar masses.
# ---------------------------------------------------------------------------

MOLAR_MASS_G_PER_MOL: dict[str, float] = {
    "ascorbic_acid": 176.12,            # C6H8O6
    "beta_alanine": 89.09,
    "betaine_anhydrous": 117.15,
    "citric_acid": 192.12,              # anhydrous
    "copper_tbcc": 213.56,              # Cu2(OH)3Cl; negligible dissolved anyway
    "creatine_monohydrate": 149.15,
    "d_ribose": 150.13,
    "dextrose": 180.16,
    "dmg": 103.12,
    "glycerin": 92.09,
    "gaa": 117.11,
    "l_arginine": 174.20,               # free base
    "l_carnitine_l_tartrate": 314.33,   # 1:1 carnitine:tartrate basis
    "l_glutamine": 146.14,
    "l_phenylalanine": 165.19,
    "l_tyrosine": 181.19,
    "sodium_chloride": 58.44,
    "potassium_chloride": 74.55,
    "trisodium_citrate": 294.10,        # dihydrate
}

OSMOTIC_N: dict[str, float] = {
    "ascorbic_acid": 1.0,               # weak acid, largely undissociated at pH 3-4
    "beta_alanine": 1.0,                # zwitterion
    "betaine_anhydrous": 1.0,           # zwitterion
    "citric_acid": 1.0,                 # screening value; partial 1st dissociation underestimated
    "copper_tbcc": 2.0,                 # if any dissolves; negligible at 0.0017 g/100mL
    "creatine_monohydrate": 1.0,
    "d_ribose": 1.0,
    "dextrose": 1.0,
    "dmg": 1.0,
    "glycerin": 1.0,                    # an osmole even though a cosolvent
    "gaa": 1.0,
    "l_arginine": 1.0,                  # free base; if HCl salt used -> 2.0
    "l_carnitine_l_tartrate": 2.0,      # dissociates carnitine+ / tartrate2- (approx)
    "l_glutamine": 1.0,
    "l_phenylalanine": 1.0,
    "l_tyrosine": 1.0,
    "sodium_chloride": 2.0,             # Na+ + Cl-
    "potassium_chloride": 2.0,          # K+ + Cl-
    "trisodium_citrate": 4.0,           # 3 Na+ + citrate3-
}

# Electrolyte ions tracked for ORS / Na-K-Cl balance.
#   mmol of ion released per gram of salt = (1000 / MW) * ions_of_that_type
ELECTROLYTE_IONS: dict[str, dict] = {
    # name -> {"na_mmol_per_g": float, "k_mmol_per_g": float, "cl_mmol_per_g": float}
    "sodium_chloride": {
        "na_mmol_per_g": 1000.0 / 58.44,        # 17.11
        "cl_mmol_per_g": 1000.0 / 58.44,        # 17.11
    },
    "potassium_chloride": {
        "k_mmol_per_g": 1000.0 / 74.55,         # 13.41
        "cl_mmol_per_g": 1000.0 / 74.55,        # 13.41
    },
    "trisodium_citrate": {
        "na_mmol_per_g": 3.0 * 1000.0 / 294.10,  # 10.20 (dihydrate)
    },
}


DEGRADATION_EA_J_PER_MOL: dict[str, tuple[int, int, int]] = {

    # Ascorbate oxidation in aqueous solution.
    # LOW Ea because the rate-limiting step is electron transfer to dissolved O₂,
    # catalysed by trace Cu/Fe; the low Ea means this pathway is NOT dramatically
    # slowed by refrigeration — confirmed by the dossier "make-fresh < 1 h" guidance.
    # pH-dependent: fastest near neutral, slower in acid (but never negligible).
    # Refs: Buettner et al. 2021 Sci Rep DOI:10.1038/s41598-021-86477-8;
    #        Ahmad & Bittenbender review of ascorbate oxidation kinetics.
    "ascorbate_oxidation": (15_000, 40_000, 67_000),

    # Maillard / Amadori browning (reducing sugar + amine).
    # HIGH Ea because the condensation step (nucleophilic attack of amine on
    # carbonyl, Schiff-base formation, Amadori rearrangement) requires significant
    # activation; refrigeration dramatically slows browning, explaining why
    # sugar+amino-acid wet products can have months of shelf-life at 4 °C but
    # days at 35 °C.
    # Refs: van Boekel 2001 Food Chem 78:35-45 (Ea ≈ 50-160 kJ/mol);
    #        Laroque et al. 2008 (fructose-amino-acid Maillard Ea ≈ 90-160 kJ/mol).
    "maillard_browning": (65_000, 100_000, 160_000),

    # Creatine → creatinine cyclisation.
    # Intramolecular dehydration/cyclisation; activation energy is relatively
    # tight (narrow range) because the mechanism is a simple intramolecular
    # proton-catalysed ring-closure with a well-characterised transition state.
    # pH-dependent: fastest at pH < 4 (acid catalysis); substantially slower
    # at pH 5.8–6.2, justifying dry storage as a mitigation.
    # Refs: Greenhaff et al. review; Deldicque et al. 2008 (Ea ≈ 90-100 kJ/mol).
    "creatine_cyclization": (90_000, 97_000, 105_000),

}
