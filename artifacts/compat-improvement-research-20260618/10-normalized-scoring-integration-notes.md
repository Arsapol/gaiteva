# Topic 10 implementation notes — normalized scoring integration

Date: 2026-06-18  
Worker: worker-1  
Scope: minimal implementation for normalized compatibility/stability/commercial-readiness scoring.

## What changed

- Added `compat.scoring` as a schema-versioned scoring/report facade (`compat-eval-v0.1`).
- Exported `evaluate_formula`, `score_osmolality_report`, and `score_solubility_report` from `compat`.
- Kept focused chemistry modules (`compat.osmolality`, `compat.solubility`, etc.) as the source of raw calculations.
- Updated the stats-card script to consume normalized scoring helpers at the solubility/osmolality boundary and attach a `normalized_compat_report` without changing existing headline smoke scores.
- Added `tests/test_compat_scoring.py` covering hard-blocker visibility, hydration caps, solubility bottleneck scoring, dry-product applicability, and schema version output.

## Double-counting guardrail

The integration does **not** add normalized aggregate penalties on top of the existing stats-card GI/shelf ledger. Instead:

1. existing raw module reports are generated once;
2. `compat.scoring` maps those reports into normalized findings/scores/caps;
3. stats-card preserves the existing GI/shelf/hydration ledger behavior and records the normalized report as an auditable compatibility facade.

This keeps current Route A and V3 Hybrid score outputs stable while creating a reusable compatibility scoring contract for later migration.

## Formula-design impact

- Hard hydration blockers remain separate findings/caps, so a biologically attractive hypertonic product cannot pass by averaging high active scores.
- Dry capsules/premixes avoid standing-solution osmolality penalties unless a reconstituted hydration claim is explicit.
- Unknown physical constants become `INSUFFICIENT_DATA` findings instead of silent optimism.
- Commercial-readiness warnings remain distinct from acute biological potential, preserving the design choice between make-fresh, split-SKU, wet concentrate, and dry activator architectures.

## Verification snapshot

- `python3 -m unittest discover -s tests -p 'test_*.py' -v` — PASS, 4 tests.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q compat compat_calc.py reformulate.py verify_dry_sku.py concentrate.py prep_sheet.py tests .codex/skills/gamefowl-formula-stats-card/scripts/calculated_stats_card.py` — PASS.
- `mypy compat compat_calc.py reformulate.py verify_dry_sku.py --ignore-missing-imports` — PASS.
- Stats-card temp regeneration vs `calculated-stats-card-v3-upgraded.json` — headline `overall`, `biological_potential`, `formulation_feasibility`, `rollups`, and `scores` unchanged for Route A and V3 Hybrid; normalized report schema attached as `compat-eval-v0.1`.
