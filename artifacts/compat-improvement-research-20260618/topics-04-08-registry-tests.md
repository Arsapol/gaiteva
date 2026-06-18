# Topics 4 + 8 — Physical registry cleanup + tests/golden fixtures

**Task owner:** worker-4  
**Date:** 2026-06-18  
**Scope:** Research/documentation only; no formula or calculator code changed.

## Executive recommendation

Make `substances/physical/*.json` the canonical physical-constants registry, demote `compat/data.py` hardcoded values to generated/backward-compatible defaults, and add a pytest/golden-fixture harness that locks known compatibility outputs before the calculator is refactored further.

Priority order:

1. **Registry contract + loader hardening:** define one schema for physical constants, source refs, review status, salt-as-weighed keys, ions, pKa, solubility, density, and osmotic screening values.
2. **Drift audit:** compare `compat/data.py` constants against `substances/physical/*.json` and fail on unreviewed drift.
3. **Golden outputs:** preserve known repo outputs: failing liquid drench `1542 mOsm/L -> BLOCK`, reformulated liquid ORS `274 mOsm/L -> PASS`, dry fight-day drink `291 mOsm/L -> PASS`, plus Na/K/Cl and solubility bottleneck counts.
4. **Fixture migration:** move demo formulas into machine-readable fixtures so `compat_calc.py`, `reformulate.py`, and `verify_dry_sku.py` render reports from the same inputs tests use.
5. **CI gate:** require registry audit + pytest before accepting future formula/scoring changes.

## Current repo state

### Calculator and constants

- `compat/data.py` contains hardcoded dictionaries for physical chemistry constants: `SUBSTANCES`, `MOLAR_MASS_G_PER_MOL`, `OSMOTIC_N`, `ELECTROLYTE_IONS`, and `DEGRADATION_EA_J_PER_MOL`.
- The same module also has `_load_external_physical_overlays()`, which mutates those module dictionaries at import time from `substances/physical/*.json` when the current working directory contains that path.
- `substances/physical/default-compat-physical.json` already mirrors many compat constants with richer fields: `compat_key`, `formula`, `molar_mass_g_per_mol`, `osmotic_n`, `solubility_g_per_100ml_25c`, `density_kg_m3`, `pka`, `ions_mmol_per_g`, `sources`, and field-level `source_refs`.
- Additional project overlays exist, including `substances/physical/taurine.json` and `substances/physical/magnesium_chloride_hexahydrate.json`.
- `compat/osmolality.py` depends on `SUBSTANCES`, `MOLAR_MASS_G_PER_MOL`, `OSMOTIC_N`, and `ELECTROLYTE_IONS` to calculate dissolved grams, mOsm/L, and Na/K/Cl load.
- `compat/solubility.py` depends on `SUBSTANCES` for solubility ceiling, dissolved solids, bottleneck, and supersaturation checks.
- `compat/ph_module.py` reads citric acid pKa from `SUBSTANCES["citric_acid"]["pka"]`.
- `compat/stokes.py` uses solubility and density for settling of undissolved fractions.
- There is no dedicated `tests/` directory, no pytest config, and no golden fixture folder in the repo root at task time.

### Existing validation evidence in scripts

The repo has three runnable scripts that already behave like informal golden tests:

| Script | Current evidence to preserve | Formula-design meaning |
|---|---:|---|
| `python3 compat_calc.py` | `1542 mOsm/L -> BLOCK`; no complete ORS; tyrosine + creatine bottlenecks | Original liquid drench is a no-go hydration solution before chemistry levers matter. |
| `python3 reformulate.py` | `274 mOsm/L -> PASS`; Na `74.1`, K `20.1`, Cl `64.6`; zero bottlenecks | Low-osmolarity liquid ORS design is plausible and complete. |
| `python3 verify_dry_sku.py` | fight-day drink `291 mOsm/L -> PASS`; Na `52.7`, K `14.8`, Cl `64.4`; zero bottlenecks | Dry-SKU split is validated; the reconstituted drink is close to the 300 mOsm/L cap, so the dextrose monohydrate spec is load-bearing. |

### Current drift / contract hazards

- **Dual source of truth:** constants live in both `compat/data.py` and `substances/physical/default-compat-physical.json`.
- **Import-time mutation:** `compat/data.py` loads overlays based on `Path.cwd() / "substances" / "physical"`; importing from another working directory may skip project overlays silently.
- **Silent failures:** malformed JSON or unexpected records are ignored by broad `except Exception: continue` paths.
- **Key ambiguity:** `compat_key` can differ from a file/object key (`magnesium_chloride_hexahydrate` maps to `magnesium_chloride`), which is useful but needs explicit salt-as-weighed semantics in tests.
- **Review-status ambiguity:** rejected/blocked records are skipped, but `draft` records can load unless status is rejected/blocked. That is flexible for exploration but risky for production scoring.
- **No golden tolerances:** future refactors could change mOsm/L, ion mmol/L, or bottleneck counts without a test explaining whether the change is intended.

## How the improvement works

### 1. Canonical registry model

Promote `substances/physical/*.json` to the canonical data source. Each active record should satisfy a documented schema:

```json
{
  "compat_key": "dextrose_monohydrate",
  "key": "dextrose_monohydrate",
  "name": "Dextrose monohydrate",
  "formula": "C6H12O6·H2O",
  "molar_mass_g_per_mol": 198.17,
  "osmotic_n": 1.0,
  "solubility_g_per_100ml_25c": 91.0,
  "density_kg_m3": 1560.0,
  "pka": [],
  "ions_mmol_per_g": {},
  "review_status": "verified",
  "sources": [],
  "source_refs": {}
}
```

Recommended status handling:

- `verified` and `reviewed`: allowed in production/default calculator reports.
- `draft`: allowed only when an explicit `allow_draft=True` or research mode is selected.
- `blocked` and `rejected`: never loaded.

Recommended data handling:

- The loader should return a new registry object rather than mutating module globals as a side effect.
- The project registry path should resolve relative to repo root or an explicit argument, not `Path.cwd()` only.
- Every loaded property should retain provenance (`source_refs`) so reports can audit why a score changed.
- Duplicate `compat_key` values should be an explicit override event with a warning/error unless the later record declares `overrides`.

### 2. Drift audit

Add a registry audit command that compares:

- `compat/data.py` hardcoded constants vs `substances/physical/default-compat-physical.json` during the transition.
- Required fields vs schema.
- `molar_mass_g_per_mol`, `osmotic_n`, and `ions_mmol_per_g` consistency.
- `ions_mmol_per_g` against formula/molar mass for simple salts where ion stoichiometry is known.
- `source_refs` presence for formula, molar mass, osmotic_n, solubility, density/pKa when present, ion fields, and note.

This can reuse the standards documented by the existing stats-card provenance upgrade page and the installed `gamefowl-formula-stats-card` audit pattern, but should produce compat-specific errors for fields the calculator actually consumes.

### 3. Golden fixture harness

Create test fixtures for the three current scenarios:

- `fixtures/compat/failing-liquid-drench.json`
- `fixtures/compat/reformulated-liquid-ors.json`
- `fixtures/compat/fight-day-drink-1l.json`

Each fixture should contain:

- `components`: list of `{key, grams}`.
- `water_ml`.
- `use_case`: e.g. `hydration_drink`, `dry_capsule`, `dry_premix`, `wet_concentrate`.
- Expected outputs with tolerances: total mOsm/L, verdict, Na/K/Cl, bottleneck count, salient blocker/warning strings.
- Registry mode: `verified_only` vs `research`.

Minimal pytest targets:

- `test_failing_liquid_drench_blocks_osmolality_and_ors()`
- `test_reformulated_liquid_ors_matches_golden_pass()`
- `test_fight_day_drink_matches_wiki_claim_and_margin()`
- `test_external_registry_overlay_loads_taurine_and_magnesium()`
- `test_rejected_or_blocked_registry_records_do_not_load()`
- `test_draft_records_do_not_load_in_verified_mode()`
- `test_registry_drift_report_has_no_unexplained_differences()`

### 4. Script/report unification

After fixtures are added, keep scripts as human-readable demos but have them consume fixture inputs and calculator APIs rather than owning separate lists. That prevents documentation examples from diverging from tests.

## Formula design decision impact

This improvement changes the calculator from an expert-demo script into an audit-controlled design gate:

- **Ingredient swaps become traceable.** If a supplier swaps dextrose monohydrate for anhydrous dextrose, tests should catch the fight-day drink crossing its narrow osmotic margin.
- **Hydration claims become safer.** Golden tests keep the blocking ORS/osmolality gate from being diluted by future scoring changes.
- **Wet vs dry split stays protected.** Tests preserve the key design decision that dry capsules/premix are not judged by standing-solution osmolality, while reconstituted drink is.
- **Registry confidence affects formula confidence.** A formula using `draft` or missing-provenance constants should be reported as lower-confidence even if the math passes.
- **Migration becomes safer.** Refactors toward a unified API or stats-card scoring can prove they preserve `1542 BLOCK`, `274 PASS`, and `291 PASS` before changing formulas.

## Risks and unknowns

- **Measured vs screening osmolality:** `osmotic_n` values are screening approximations; future lab osmolality may legitimately differ from computed mOsm/L.
- **Solubility in matrix:** single-solute ceilings do not fully model pH, ionic strength, cosolvents, temperature, and multi-solute salting effects.
- **Hydrate/salt identity:** salt-as-weighed basis must be explicit. Example: dextrose monohydrate and anhydrous dextrose have different MW and osmotic load per gram.
- **Registry overrides:** project overlays are useful but can mask defaults if duplicate keys are not audited.
- **Draft research velocity:** banning drafts everywhere may slow exploration; allow draft mode only outside production reports.
- **No current CI baseline:** adding pytest may reveal unrelated smoke-test fragility; start with pure calculator tests and fixture assertions.

## Validation and audit checklist

### Registry checklist

- [ ] Define `substances/physical` JSON schema and required fields.
- [ ] Add a loader that resolves from explicit repo root/path, not only CWD.
- [ ] Decide verified-only default for production calculator outputs.
- [ ] Fail on malformed active JSON records instead of silently ignoring them.
- [ ] Emit duplicate-key/override diagnostics.
- [ ] Require field-level `source_refs` for active records.
- [ ] Add drift report between legacy `compat/data.py` constants and registry values during migration.
- [ ] Add salt/hydrate identity notes for formula-critical specs.

### Golden fixture checklist

- [ ] Golden: original liquid drench remains `BLOCK`, approx `1542 mOsm/L`, complete ORS `False`.
- [ ] Golden: original liquid drench has two solubility bottlenecks: `l_tyrosine`, `creatine_monohydrate`.
- [ ] Golden: reformulated liquid ORS remains `PASS`, approx `274 mOsm/L`, Na/K/Cl approx `74.1/20.1/64.6`, zero bottlenecks.
- [ ] Golden: fight-day drink remains `PASS`, approx `291 mOsm/L`, Na/K/Cl approx `52.7/14.8/64.4`, zero bottlenecks.
- [ ] Golden: dry capsule/premix fixtures bypass standing-solution osmolality and use dry-product checks instead.
- [ ] Regression: changing dextrose monohydrate to anhydrous dextrose in the drink fixture must fail or warn on margin loss.
- [ ] Regression: blocked/rejected registry records do not affect outputs.

### Verification commands used for this research artifact

```bash
python3 compat_calc.py
python3 reformulate.py
python3 verify_dry_sku.py
python3 -m compileall compat compat_calc.py reformulate.py verify_dry_sku.py
```

## Affected files / proposed future files

### Existing files affected by a future implementation

- `compat/data.py` — registry loader, legacy constants, degradation pathway constants.
- `compat/osmolality.py` — consumes MW, osmotic_n, ion mmol/g, solubility-limited dissolved grams.
- `compat/solubility.py` — consumes solubility ceilings and miscibility convention.
- `compat/ph_module.py` — consumes citric acid pKa.
- `compat/stokes.py` — consumes solubility/density for undissolved particle settling.
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py` — should eventually read fixture inputs.
- `substances/physical/default-compat-physical.json`, `substances/physical/taurine.json`, `substances/physical/magnesium_chloride_hexahydrate.json` — current physical registry records.
- `calculated-stats-card-v3-upgraded.md`, `calculated-stats-card-v3-upgraded.json` — downstream score/readiness reports that should trust stable compat outputs.

### Proposed new files for implementation phase

- `compat/registry.py`
- `compat/report.py` or future unified API module owned by topic 1
- `tests/test_compat_registry.py`
- `tests/test_compat_golden_fixtures.py`
- `fixtures/compat/failing-liquid-drench.json`
- `fixtures/compat/reformulated-liquid-ors.json`
- `fixtures/compat/fight-day-drink-1l.json`
- `artifacts/compat-registry-drift/*.json` or similar generated audit output

## Evidence references

- Context snapshot: `/Users/arsapolm/Documents/my-projects/gaiteva/.omx/context/compat-stability-improvement-team-20260618T071451Z.md`.
- Task file: `/Users/arsapolm/.omx-runs/run-20260618070426-4bc2/.omx/state/team/research-improvement-44ddd92b/tasks/task-4.json`.
- Current constants and loader: `compat/data.py` (`SUBSTANCES`, `MOLAR_MASS_G_PER_MOL`, `OSMOTIC_N`, `ELECTROLYTE_IONS`, `_load_external_physical_overlays`).
- Solubility/TDS consumer: `compat/solubility.py`.
- Osmolality/electrolyte consumer: `compat/osmolality.py`.
- pH pKa consumer: `compat/ph_module.py`.
- Demo/golden scripts: `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py`.
- Registry records: `substances/physical/default-compat-physical.json`, `substances/physical/taurine.json`, `substances/physical/magnesium_chloride_hexahydrate.json`.
- Prior calculator KB: `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md`.
- Provenance registry precedent: `omx_wiki/stats-card-provenance-registry-upgrade-2026-06-17.md`.

## Coordination notes

- Boundary with worker-1/topics 1+10: registry/golden fixtures should feed the future unified API and scoring, but this artifact does not define the final score formula.
- Boundary with worker-2/topics 2+9: golden fixture assertions should include use-case-specific gates, but ORS thresholds and use-case routing belong to that topic.
- Boundary with worker-3/topics 3+5: registry schema should include reactive class hints and metal ppm fields later, but pairwise/redox rule design belongs to that topic.
- Boundary with worker-5/topics 6+7: pKa/buffer constants and Arrhenius pathway constants should be registry-auditable, but pH prediction and assay-driven shelf-life modeling belong to that topic.

Coordination protocol: coordinated - task list boundaries checked; this artifact keeps topic 4+8 to registry/test harness and calls out interfaces to workers 1, 2, 3, and 5.

## Subagent findings integrated

Subagents spawned: 3 read-only researcher probes (`current repo state`, `risk/edge-case review`, `documentation/migration slice review`) using the task-required gpt-5.4-mini researcher role.  
Serial searches before spawn: 1 task-file/inbox read sequence after claim.  
Findings integrated: pending child reports were not required to author the first pass; final task completion evidence will include completed child IDs and any additional integrated bullets, or note if no child completed before deadline.
