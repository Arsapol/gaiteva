# Compat improvement 8: Tests, golden fixtures, and validation harness

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

High — lowest-risk way to harden the calculator before implementation changes.

## Current repo state

The repo has module `__main__` smoke tests and executable scripts, but no discovered `pytest`/unit-test files in this worktree. Current expected values are known from script runs: `compat_calc.py` failing drench ~1542 mOsm/L BLOCK, `reformulate.py` passing ORS ~274 mOsm/L, and `verify_dry_sku.py` fight-day drink ~291 mOsm/L PASS with high-aw make-fresh warning. Without golden fixtures, changes to constants, units, or gate thresholds can silently alter conclusions.

## How the improvement works

Add a `tests/` suite with small golden fixtures and schema assertions. Tests should directly call pure module functions rather than parse console output, while keeping a smoke test that runs the three scripts. Include fixtures for edge cases: unknown molar mass, zero/negative water volume, solubility-capped osmoles, dry-use-case osmolality exemption, high-aw liquid warning, and redox packaging mitigation.

## How it affects formula design decisions

Designers and reviewers can trust that future refactors do not accidentally greenlight hypertonic products or block dry products. Golden tests also make future research auditable: if a constant changes, the diff explains whether the design decision changed or the data improved.

## Risks / unknowns

Goldens can freeze early screening assumptions too tightly. Tests should allow tolerances and distinguish scientific thresholds from implementation details. Some current functions may need input validation decisions before tests can assert behavior.

## Validation checklist

- [ ] `pytest` passes with fixture values for 1542, 274, and 291 mOsm/L within tolerance.
- [ ] Tests cover both blocking and advisory gates.
- [ ] Tests assert JSON schema/provenance fields once unified report exists.
- [ ] CLI smoke tests capture regressions in user-visible demos.
- [ ] Validation harness exports a short markdown/JSON evidence bundle for leader audit.

## Affected files / future touchpoints

- `compat/*.py`
- `compat_calc.py`
- `reformulate.py`
- `verify_dry_sku.py`
- future: tests/test_compat_*.py, tests/fixtures/*.json

## Evidence references

- Command evidence in this task: no test files found by `find` for `test*.py`, `pytest.ini`, or `pyproject.toml`.
- `compat/solubility.py:207-227` and `compat/osmolality.py:173-196` have smoke-test blocks but not a CI harness.
- Current script outputs captured under `/tmp/worker3-*.out` during this research pass.
