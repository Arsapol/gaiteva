# Topic 07 implementation notes — assay-driven Arrhenius shelf-life

Implemented a minimal assay-driven layer in `compat.arrhenius`:

- `assay_rates_by_temperature(...)` fits first-order or zero-order assay rates from rows with `temperature_C`, `time_days`, and `measured_value`.
- `fit_arrhenius_ea_from_rates(...)` fits Ea only when at least two positive-rate temperatures exist.
- `assay_shelf_life_projection(...)` projects a target-temperature endpoint while returning an ICH/real-time status and `label_claim_supported` guardrail.
- `assay_projection_report(...)` renders a compact report that explicitly separates screening projections from label shelf-life claims.

Guardrails:

- Single-temperature stress data are `prior_constrained` and `screen_only`.
- 50 °C or hotter observations are stress-screen only because degradation mechanisms may change.
- Low-Ea/ascorbate pathways always carry a real-time-data warning.
- Label shelf-life support remains false unless target-temperature real-time observations cover the projected endpoint.

Smoke output preservation:

- Existing `compat_calc.py` output was not changed. The new API/report functions are callable but not added to the demo smoke path.
