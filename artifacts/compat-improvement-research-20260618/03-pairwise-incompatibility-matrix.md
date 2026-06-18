# Compat improvement 3: Machine-readable pairwise incompatibility matrix

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

High — closes the gap between human safety notes and automated formula screening.

## Current repo state

Pairwise incompatibility knowledge exists mostly in prose dossiers and formula-safety workflow guidance, while `compat/gibbs.py` is explicitly only a backup thermodynamic screen. `compat/redox.py` handles ascorbate redox risk and can infer a default metal proxy, but it does not express a general matrix for NAC + metals, reducing sugar + amine, ribose + ascorbate, citrate + minerals, preservative pH limits, oil-phase incompatibilities, or dry-separation mitigations. The current docs correctly warn that Gibbs spontaneity is not a rate or practical danger signal.

## How the improvement works

Create a versioned matrix such as `substances/compatibility/pairwise-rules.json`. Each rule should identify `a`, `b`, optional phase/use-case constraints, mechanism, severity, confidence, required mitigation, and citations/provenance. The evaluator then expands a formula into relevant pairs and returns a normalized rule ledger. Rules should support classes (`reducing_sugar`, `primary_amine`, `transition_metal`, `thiol`) so new substances inherit known incompatibilities without duplicating every pair.

## How it affects formula design decisions

Formula design can automatically justify split architectures: dry activator for tyrosine/ascorbate/taurine, make-fresh liquids for ribose/electrolytes, and separation of redox-active trace metals from wet antioxidants. The matrix would make commercial readiness penalties auditable rather than ad hoc prose in each stats card.

## Risks / unknowns

A sparse matrix can miss hazards and a broad class rule can over-block benign pairings. Rule confidence and applicability windows are essential: a dry capsule pair may be acceptable while the same pair in a wet stored SKU is a block. Pairwise rules also miss three-way effects such as O2 + metal + ascorbate.

## Validation checklist

- [ ] At least one golden formula triggers sugar+primary-amine Maillard advisory only in wet/stored contexts.
- [ ] Ascorbate+metal/O2/light rules reproduce current `redox.py` conclusions.
- [ ] Dry-separated pairs downgrade severity with explicit mitigation evidence.
- [ ] Rules can be traced back to substance dossier/wiki references.
- [ ] Unknown class membership is reported as an unknown, not a pass.

## Affected files / future touchpoints

- `compat/gibbs.py`
- `compat/redox.py`
- `omx_wiki/substance-*.md`
- `.codex/skills/formula-safety-check/SKILL.md`
- future: substances/compatibility/pairwise-rules.json, compat/pairwise.py

## Evidence references

- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md:21-31` labels Gibbs as backup and Arrhenius/reactivity as primary.
- `compat/gibbs.py` caveat says dG<0 does not mean fast or dangerous.
- `calculated-stats-card-v3-upgraded.md:66-71` shows Maillard/redox/TDS penalties already influence shelf and hydration caps.
