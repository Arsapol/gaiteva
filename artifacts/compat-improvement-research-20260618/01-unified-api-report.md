# Compat improvement 1: Unified API and report for full formula evaluation

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

High — enables every other improvement to be consumed consistently.

## Current repo state

The calculator is a set of pure modules plus scripts rather than a single evaluator. `compat_calc.py` manually calls `osmolality_report`, `additive_report`, `ph_window_check`, `all_pathways`, `settling_report`, and `screen_pair`; `reformulate.py` and `verify_dry_sku.py` are separate fixtures. `calculated-stats-card-v3-upgraded.*` already carries physical gates, but those gates are embedded in stats-card generation rather than emitted by `compat/` as a stable report contract. The prior `.omc` wiki page says Tier 0 is enough for GO/NO-GO formulation decisions, yet there is no importable `evaluate_formula(...)` API that returns the entire Tier-0 decision ledger.

## How the improvement works

Add a thin orchestration layer such as `compat/report.py` with an `evaluate_formula(formula, use_case, volume_ml=None, storage=None, packaging=None, assumptions=None)` function. It should call existing modules, normalize all outputs into a versioned JSON schema, and emit a Markdown renderer for audit. The schema should separate `blocking_gates`, `advisory_flags`, `scores`, `assumptions`, `unknowns`, `provenance`, and `next_validation`. Do not hide module detail: each gate should include the raw module output plus a normalized severity (`pass`, `marginal`, `block`, `unknown`) and confidence.

## How it affects formula design decisions

Formula design moves from scattered script interpretation to a single decision packet. A designer can compare wet-core, dry-stick, capsule, and make-fresh concepts without re-implementing the same chemistry checks. It also prevents stats-card scoring from diverging from command-line calculator behavior; hydration caps, shelf penalties, and solubility factors would all come from the same report.

## Risks / unknowns

The main risk is false authority: a polished report may look like lab validation. The API must label screening assumptions and require bench assays for shelf-life claims. Another risk is overfitting the API to the current hydration-drink examples; the schema should tolerate dry products, oil emulsions, and partial formulas without forcing irrelevant gates.

## Validation checklist

- [ ] Golden JSON report for current `compat_calc.py` failing drench: ~1542 mOsm/L BLOCK, no Na/K/Cl, two solubility bottlenecks.
- [ ] `reformulate.py` report remains ~274 mOsm/L PASS and complete ORS.
- [ ] `verify_dry_sku.py` report marks dry products exempt from standing-solution osmolality while the 1 L drink is ~291 mOsm/L PASS.
- [ ] Schema version, assumptions, unknown molar masses, and provenance are always present.
- [ ] Markdown renderer round-trips the JSON without hand-edited conclusions.

## Affected files / future touchpoints

- `compat_calc.py`
- `reformulate.py`
- `verify_dry_sku.py`
- `compat/*.py`
- `calculated-stats-card-v3-upgraded.*`
- future: compat/report.py, compat/schema.py

## Evidence references

- `compat_calc.py:92-236` orchestrates checks manually.
- `compat/osmolality.py:158-170` already returns a full blocking gate object.
- `calculated-stats-card-v3-upgraded.md:50-85` and `:124-156` prove physical gate output affects formula scores.
