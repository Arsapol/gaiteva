# Formulation compatibility — redox mechanism ledger

Implemented in `compat/redox.py` as a Tier-0 qualitative screen, not a shelf-life model.

## What changed

- Preserves the existing ascorbate `flag_from_components(...)` output used by `reformulate.py`.
- Adds `redox_mechanism_ledger(...)` for auditable mechanisms: ascorbate oxidation, NAC/thiol oxidation, oil peroxide risk, ribose + ascorbate co-loss, and transition-metal catalysis.
- Reports threshold assumptions, factor scores, detected drivers, mitigations, packaging/hold-time assumptions, and validation assays.

## Validation boundary

A high or severe wet-stored redox hit blocks 6-12 month shelf claims until product-specific assays exist. Useful assays include HPLC ascorbate/DHAA, NAC/disulfide or free-thiol assay, peroxide value for oils, colorimetry/browning, supplier CoA metal ppm limits, and real-time/stress stability in final packaging.

## Regression anchors

- Reformulated ORS with ascorbate + headspace O2 + clear packaging remains `MODERATE`.
- Wet NAC + copper/O2 flags thiol oxidation and blocks wet shelf claims pending assays.
- Dry-separated NAC is not treated as a wet-shelf redox block; humidity/packaging remains a separate dry-SKU control.

## Smoke-output preservation note

`reformulate.py` and `verify_dry_sku.py` were intentionally left API-compatible: the reformulated ORS still reports `Ascorbate redox risk : MODERATE` from headspace oxygen and clear packaging, and the dry-SKU drink still reports redox as N/A when no ascorbate is present. `python3 -m compat.redox` now intentionally prints the expanded structured ledger fields so the new thresholds, scores, assay list, and NAC wet/dry regression case are visible during smoke validation.
