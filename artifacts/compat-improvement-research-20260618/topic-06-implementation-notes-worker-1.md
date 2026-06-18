# Topic 06 implementation notes — worker-1

Implemented a minimal citrate-only pH/buffer/dilution screening upgrade.

## Added surface

- `compat.ph_module.citrate_alpha_fractions(pH)` reports triprotic citrate alpha fractions.
- `compat.ph_module.citrate_inventory(components, water_ml)` reports citrate acid/salt inventory and explicit hydrate assumptions.
- `compat.ph_module.citrate_ph_report(...)` predicts screening-grade citrate-driven pH, buffer reserve, optional dilution-to-use pH, sorbate active fraction, measured-pH override, prediction error, confidence, and caveats.
- Existing helpers `henderson_hasselbalch`, `citrate_buffer_ratio`, `ph_window_check`, and `degradation_vs_ph` remain additive/backward-compatible.

## Scope and caveats

This is not a full matrix pH solver. It solves citrate-only charge balance from citric acid and trisodium citrate forms, then labels the result as screening-grade. Reports explicitly warn that activity coefficients, amino acids, minerals, sugars, CO2 uptake, preservatives, temperature, and the real water matrix require calibrated meter confirmation.

Supported first-slice hydrate/form assumptions:

- `citric_acid`: anhydrous, MW 192.12 g/mol.
- `citric_acid_monohydrate`: MW 210.14 g/mol.
- `trisodium_citrate`: dihydrate, MW 294.10 g/mol.
- `trisodium_citrate_anhydrous`: MW 258.06 g/mol.

## Intentional smoke-output change

`compat_calc.py` now includes an additive subsection under LEVER 2:

- citrate pH/buffer screening estimate,
- total citrate pool,
- screening buffer beta,
- 1 L dilution pH/citrate concentration,
- sorbate active fraction,
- meter-confirmation caveat.

Existing osmolality, solubility, target-pH window, degradation, Arrhenius, Stokes, Gibbs, and overall verdict lines are preserved.

## Regression coverage

Added `tests/test_ph_module.py` covering:

- alpha-fraction normalization at pH 3.13, 4.76, and 6.40,
- documented 0.7 g/L citric acid + 0.3 g/L trisodium citrate ORS fixture,
- dilution lowering buffer capacity,
- measured-pH override retaining prediction error,
- sorbate active fraction decreasing at higher pH.
