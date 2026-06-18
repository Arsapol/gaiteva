---
title: "Compat/Stability Calculator Improvement Roadmap — 2026-06-18"
tags: ["compat-calculator", "stability", "research-improvement", "task-3", "roadmap", "gamefowl"]
created: 2026-06-18T07:20:00Z
updated: 2026-06-18T07:20:00Z
category: reference
confidence: medium
schemaVersion: 1
---

# Compat/stability calculator improvement research — Task 3 synthesis

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

## Executive synthesis

The repo already has a credible Tier-0 compatibility/stability calculator for water-based gamefowl formula screening: osmolality/electrolyte blocking, solubility/TDS, pH window, Arrhenius pathway projections, ascorbate redox, activity, water activity, Stokes settling for undissolved solids, and Gibbs as a non-primary backup screen. The main improvement opportunity is not another isolated equation; it is making the existing pieces auditable, use-case aware, and test-backed so formula design decisions cannot drift between scripts, wiki prose, and stats-card scoring.

Recommended order:

1. Add tests/golden fixtures first. This protects the known 1542 BLOCK / 274 PASS / 291 PASS behavior before refactors.
2. Add a unified report API and use-case profiles. This makes dry, wet, concentrate, and hydration products comparable without false gates.
3. Harden ORS/glucose:Na and constants registry because they directly decide hydration claims and manufacturing specs.
4. Add pairwise matrix, redox expansion, pH/buffer dilution, and assay-driven Arrhenius as incremental scientific depth.
5. Integrate normalized scoring with stats-card only after gates and report schema are stable.

## Topic artifacts

| # | Topic | Priority | Artifact | Wiki-ready page |
|---:|---|---|---|---|
| 1 | Unified API and report for full formula evaluation | High | [`01-unified-api-report.md`](01-unified-api-report.md) | [`omx_wiki/compat-improvement-2026-06-18-unified-api-report.md`](compat-improvement-2026-06-18-unified-api-report.md) |
| 2 | Volume-aware electrolyte/ORS gate and glucose:Na ratio | High | [`02-volume-aware-ors-glucose-na-gate.md`](02-volume-aware-ors-glucose-na-gate.md) | [`omx_wiki/compat-improvement-2026-06-18-volume-aware-ors-glucose-na-gate.md`](compat-improvement-2026-06-18-volume-aware-ors-glucose-na-gate.md) |
| 3 | Machine-readable pairwise incompatibility matrix | High | [`03-pairwise-incompatibility-matrix.md`](03-pairwise-incompatibility-matrix.md) | [`omx_wiki/compat-improvement-2026-06-18-pairwise-incompatibility-matrix.md`](compat-improvement-2026-06-18-pairwise-incompatibility-matrix.md) |
| 4 | Physical constants registry and drift cleanup | High | [`04-physical-constants-registry-drift-cleanup.md`](04-physical-constants-registry-drift-cleanup.md) | [`omx_wiki/compat-improvement-2026-06-18-physical-constants-registry-drift-cleanup.md`](compat-improvement-2026-06-18-physical-constants-registry-drift-cleanup.md) |
| 5 | Redox calculation upgrade | Medium-high | [`05-redox-calculation-upgrade.md`](05-redox-calculation-upgrade.md) | [`omx_wiki/compat-improvement-2026-06-18-redox-calculation-upgrade.md`](compat-improvement-2026-06-18-redox-calculation-upgrade.md) |
| 6 | pH, buffer-capacity, and dilution prediction | Medium-high | [`06-ph-buffer-dilution-prediction.md`](06-ph-buffer-dilution-prediction.md) | [`omx_wiki/compat-improvement-2026-06-18-ph-buffer-dilution-prediction.md`](compat-improvement-2026-06-18-ph-buffer-dilution-prediction.md) |
| 7 | Data-driven Arrhenius shelf-life projection from stress assays | Medium | [`07-data-driven-arrhenius-stress-assay-shelf-life.md`](07-data-driven-arrhenius-stress-assay-shelf-life.md) | [`omx_wiki/compat-improvement-2026-06-18-data-driven-arrhenius-stress-assay-shelf-life.md`](compat-improvement-2026-06-18-data-driven-arrhenius-stress-assay-shelf-life.md) |
| 8 | Tests, golden fixtures, and validation harness | High | [`08-tests-golden-fixtures-validation-harness.md`](08-tests-golden-fixtures-validation-harness.md) | [`omx_wiki/compat-improvement-2026-06-18-tests-golden-fixtures-validation-harness.md`](compat-improvement-2026-06-18-tests-golden-fixtures-validation-harness.md) |
| 9 | Separate gates by product/use-case: hydration drink, acute sublingual, dry capsule, wet concentrate | High | [`09-separate-gates-by-product-use-case.md`](09-separate-gates-by-product-use-case.md) | [`omx_wiki/compat-improvement-2026-06-18-separate-gates-by-product-use-case.md`](compat-improvement-2026-06-18-separate-gates-by-product-use-case.md) |
| 10 | Normalized compatibility/stability/commercial-readiness scoring integrated with stats card | Medium-high | [`10-normalized-compatibility-stability-commercial-readiness-scoring.md`](10-normalized-compatibility-stability-commercial-readiness-scoring.md) | [`omx_wiki/compat-improvement-2026-06-18-normalized-compatibility-stability-commercial-readiness-scoring.md`](compat-improvement-2026-06-18-normalized-compatibility-stability-commercial-readiness-scoring.md) |

## Current command evidence captured by worker-3

- `python3 compat_calc.py`: failing liquid drench is **1542 mOsm/L -> BLOCK**, no added Na/K/Cl, tyrosine and creatine bottlenecks; final verdict is NO-GO as hydration drench.
- `python3 reformulate.py`: reformulated ORS is **274 mOsm/L -> PASS**, Na 74.1 / K 20.1 / Cl 64.6 mmol/L, zero bottlenecks; advisory flags include moderate ascorbate redox and high water activity requiring preservative/challenge testing for wet shelf claims.
- `python3 verify_dry_sku.py`: dry Products 1/2 are exempt from standing-solution osmolality; Product 3 drink is **291 mOsm/L -> PASS**, Na 52.7 / K 14.8 / Cl 64.4 mmol/L, high-aw make-fresh/discard-same-day warning.
- Test discovery: no `test*.py`, `pytest.ini`, `pyproject.toml`, or package test suite was found in this worktree; current checks are script smoke runs and module `__main__` blocks.

## Boundary / coordination notes

- Coordination protocol: coordinated - task state, leader inbox instructions, resolved context snapshot path, artifact/wiki output boundaries, and no-code-edit constraint checked.
- No shared formula/calculator code was edited. All writes are documentation under `artifacts/compat-improvement-research-20260618/` and `omx_wiki/`.
- Integration risk for leader: this worker created multiple wiki-ready pages. If the leader prefers a single canonical page, retain `omx_wiki/compat-stability-calculator-improvement-roadmap-2026-06-18.md` as the entry point and merge topic pages later.
