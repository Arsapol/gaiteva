# Compat improvement 4: Physical constants registry and drift cleanup

**Task/source context.** Worker-3 Task 3 research artifact generated 2026-06-18 from local evidence only. Required snapshot resolved at `/Users/arsapolm/Documents/my-projects/gaiteva/.omx/context/compat-stability-improvement-team-20260618T071451Z.md` because `.omx/context/` is not present inside this worker worktree. Scope is documentation/research only; no formula or calculator code changes are proposed here.

**Current evidence anchors used across this set.**
- `compat/osmolality.py:1-24`, `:86-170` — dissolved-fraction osmolality, ORS classification, and absolute Na/K/Cl completeness flag.
- `compat/solubility.py:49-200` — per-substance solubility, TDS, bottlenecks, and supersaturation warnings.
- `compat/data.py:368-406` plus `substances/physical/*.json` — external physical-constant overlays.
- `compat/redox.py:121-331` — ascorbate-focused redox screen with O2/light/metal/chelation drivers.
- `compat/ph_module.py:1-226` — Henderson-Hasselbalch helpers, pH-window check, degradation-vs-pH text.
- `compat/arrhenius.py:31-180` — Arrhenius `k`, Q10, acceleration factor, and per-pathway projections.
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py` — executable demos/fixtures.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md:46-87` — prior calculator reference page; no equivalent `omx_wiki/` page existed before this task.
- `calculated-stats-card-v3-upgraded.md:50-85`, `:124-156` — physical gate penalties already affect stats-card outputs but are not driven by a unified compat API.

## Priority / recommendation

High — bad constants silently invalidate every downstream gate.

## Current repo state

`compat/data.py` contains built-in constants for solubility, density, pKa, molecular weight, osmotic particle count, electrolyte ions, and degradation activation energies. It also loads JSON overlays from `substances/physical/*.json`, with provenance fields in `default-compat-physical.json`, `taurine.json`, and `magnesium_chloride_hexahydrate.json`. This is a good start, but constants are split between Python and JSON, units are implicit in some dictionaries, and there is no CI check that JSON overlays match schema, units, or expected drift from Python defaults.

## How the improvement works

Move toward a single registry contract: one schema for physical constants with explicit units, temperature, hydration state, pH/speciation assumptions, source tier, and last-reviewed date. Python defaults can remain as bootstrapping data, but the loader should validate overlays and emit drift warnings when a key changes a score-critical value. Add a generated registry report that lists constants by confidence and missing fields.

## How it affects formula design decisions

Design decisions become manufacturing-control decisions. The current dry-stick drink has only +9 mOsm/L margin to a 300 cap, so dextrose monohydrate vs anhydrous MW is not a trivia field; it can flip a design from pass to marginal. Solubility ceilings for tyrosine and creatine decide whether an active belongs in a wet liquid or dry SKU.

## Risks / unknowns

Over-centralizing constants can slow iteration if every exploratory value needs a formal source. Conversely, allowing unvalidated overlays creates silent drift. Some values are context-dependent (temperature, pH, ionic strength, polymorph), so the registry must represent ranges and screening assumptions rather than a fake single truth.

## Validation checklist

- [ ] JSON schema validates all `substances/physical/*.json` records.
- [ ] Registry report flags missing MW, osmotic_n, solubility, temperature, hydration state, or provenance.
- [ ] Changing dextrose monohydrate MW to anhydrous changes osmolality fixture as expected and fails a spec test.
- [ ] Overlay load order is deterministic and logged in report provenance.
- [ ] Every constant used in score-critical gates has a source tier or explicit assumption.

## Affected files / future touchpoints

- `compat/data.py`
- `substances/physical/default-compat-physical.json`
- `substances/physical/taurine.json`
- `substances/physical/magnesium_chloride_hexahydrate.json`
- future: substances/physical/schema.json, compat/registry.py

## Evidence references

- `compat/data.py:368-406` loads external overlays into `SUBSTANCES`, `MOLAR_MASS_G_PER_MOL`, `OSMOTIC_N`, and electrolyte dictionaries.
- `substances/physical/default-compat-physical.json` includes provenance and notes that osmotic_n is a screening count.
- `.omc/wiki/...:73` notes the dextrose-monohydrate spec is load-bearing for the 291 mOsm/L drink.
