# Leader synthesis — Compatibility/Stability calculator improvement research

Date: 2026-06-18
Team: `research-improvement-44ddd92b`
Scope: research/documentation only; no calculator/formula code implementation in this run.

## Team execution evidence

- Team launched with 5 researcher workers.
- Terminal team status before shutdown: 5 tasks total, 5 completed, 0 failed, 0 in progress.
- Team shutdown completed cleanly.
- Worker artifacts were integrated into leader branch; final team HEAD after shutdown: `35fe7bb`.
- Pre-team dirty wiki/log changes were stashed for OMX worktree preflight and restored after shutdown.

## Research KB outputs

Primary lane artifacts:

1. `topics-01-10-unified-api-scoring.md` — unified API/report + normalized scoring.
2. `topics-02-09-ors-usecase-gates.md` — volume-aware ORS gate + use-case gates.
3. `topics-03-05-pairwise-redox.md` — pairwise incompatibility matrix + redox upgrade.
4. `topics-04-08-registry-tests.md` — physical registry cleanup + tests/golden fixtures.
5. `topics-06-07-ph-arrhenius.md` — pH/buffer prediction + assay-driven Arrhenius.

Expanded KB set:

- `README.md` and `compat-stability-decision-tree.md` under `artifacts/compat-improvement-research-20260618/`.
- 10 per-topic artifacts: `01-...` through `10-...`.
- Wiki pages under `omx_wiki/compat-improvement-2026-06-18-*.md`.
- Five lane-specific wiki pages under `omx_wiki/research-compat-improvement-*.md`.
- Roadmap page: `omx_wiki/compat-stability-calculator-improvement-roadmap-2026-06-18.md`.
- Decision-tree page: `omx_wiki/compat-stability-decision-tree.md`.

## Executive synthesis

The current `compat/` calculator is scientifically useful as a Tier-0 screening toolkit, but it is still script/module driven. The biggest improvement is not adding one more equation. It is creating an auditable evaluator that applies the right gates to the right product class and exposes a consistent report object for stats-card scoring, wiki review, and formula design.

Recommended implementation order:

1. **Tests/golden fixtures first.** Lock current known outputs before refactor: `compat_calc.py` ~1542 mOsm/L BLOCK, `reformulate.py` ~274 PASS, `verify_dry_sku.py` ~291 PASS.
2. **Physical registry hardening.** Make `substances/physical/*.json` the source of truth; eliminate drift vs hardcoded constants; fail closed on missing MW/ions for hydration calculations.
3. **Unified `compat.evaluate_formula(...)` API.** Return one schema with product type, route, volume, storage state, gates, findings, blockers/warnings, confidence, validation checklist, and score deltas.
4. **Use-case profiles.** Hydration drink, acute sublingual/oral-mucosal, dry capsule, dry premix, wet concentrate, and wet-core-plus-dry-activator need different blocking/advisory logic.
5. **Volume-aware ORS/electrolyte gate.** Report Na/K/Cl mmol/L, glucose mmol/L, glucose:Na, hydrate/salt forms, and final delivered volume. Current sodium-only `complete_ors` is too weak for future certification.
6. **Pairwise matrix + upgraded redox.** Convert prose incompatibilities into machine-readable rules with phase/use-state context; expand redox from qualitative strings to mole/ppm/packaging/oxygen/light-aware findings.
7. **pH/buffer and assay-backed stability.** Predict pH from citric acid/citrate amounts and dilution; use real stress/real-time assay data for Arrhenius projections while keeping label shelf-life claims bounded.
8. **Normalized scoring integration.** Only after gates/schema are stable, feed compatibility/stability/commercial-readiness scores into the stats-card without double-counting penalties.

## Formula-design impact

- **Hydration formulas:** must pass delivered-volume osmolality and real ORS completeness before biological actives matter. This protects against hypertonic drinks being mislabeled as hydration support.
- **Dry capsules/preloads:** should not be penalized by standing-solution osmolality. Their gates are moisture, caking, segregation, dose uniformity, packaging, and dry-state compatibility.
- **Acute sublingual/oral-mucosal products:** high osmolality can be route-conditionally acceptable, but this must not be confused with swallowed hydration suitability.
- **Wet concentrates:** need two checks: bottle-state stability/solubility/aw/redox/preservative/emulsion, and final-dilution osmolality/pH/ORS suitability.
- **Split-SKU designs:** remain the most robust architecture because dry separation avoids many wet Maillard/redox/microbial conflicts while make-fresh drink can carry hydration.
- **Commercial readiness:** cannot come from calculator math alone. Wet shelf claims require assay, challenge testing, packaging evidence, and real-time/accelerated stability data.

## Key risks to fix

- Current `complete_ors` can pass with any sodium >0; future gate must require meaningful Na/K/Cl and glucose:Na ranges.
- `compat/data.py` and `substances/physical/*.json` can drift; overlay loading is currently CWD-sensitive.
- Unknown molar mass/ion stoichiometry can undercount osmoles and over-credit formulas.
- Redox is qualitative; metal ppm, chelator molar ratios, O2/headspace, light, and packaging are not yet quantified.
- pH module checks a target pH but does not predict pH/buffer reserve from ingredients or dilution.
- Arrhenius module has useful priors but cannot prove product shelf life without product-specific assays and real-time confirmation.

## Minimal implementation backlog

1. Add `tests/test_compat_golden_fixtures.py` with current three script examples.
2. Add `compat/registry.py` with explicit repo-root registry loading and schema validation.
3. Add fixture JSON files for failing liquid drench, reformulated ORS, fight-day drink, dry capsule, acute sublingual, and wet concentrate.
4. Add `compat/profiles.py` defining use-case applicability gates.
5. Add `compat/report.py` or `compat.evaluate_formula(...)` facade.
6. Add `compat/pairwise.py` and `substances/compatibility/pairwise-rules.json`.
7. Upgrade `compat/redox.py` to accept formula masses, CoA metal ppm, chelator moles, oxygen/light/packaging context.
8. Add citrate pH solver and buffer capacity report.
9. Add assay input schema for Arrhenius projections and require confidence labels.
10. Migrate stats-card physical gate logic to consume the unified report.

## Audit notes

- The team intentionally wrote documentation/KB only. Future implementation should be a separate coding pass.
- Keep the roadmap page as canonical entry point: `omx_wiki/compat-stability-calculator-improvement-roadmap-2026-06-18.md`.
- Keep the decision tree close to formula-design work: `omx_wiki/compat-stability-decision-tree.md`.
