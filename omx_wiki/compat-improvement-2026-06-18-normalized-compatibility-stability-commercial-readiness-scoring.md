---
title: "Compat improvement 10: Normalized compatibility/stability/commercial-readiness scoring integrated with stats card"
tags: ["compat-calculator", "stability", "research-improvement", "task-3", "gamefowl"]
created: 2026-06-18T07:20:00Z
updated: 2026-06-18T07:20:00Z
category: reference
confidence: medium
schemaVersion: 1
---

# Compat improvement 10: Normalized compatibility/stability/commercial-readiness scoring integrated with stats card

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

Medium-high — needed for ranking candidates, but only after gates are trustworthy.

## Current repo state

`calculated-stats-card-v3-upgraded.md/json` already includes physical chemistry gate outcomes, hydration caps, GI/emulsion penalties, shelf/commercial-readiness notes, and confidence labels. However, the score logic is not a general compat report and may drift from `compat/` scripts. Physical chemistry is partly a hard gate (e.g., hypertonic hydration block) and partly a weighted readiness score (e.g., emulsion validation, preservative challenge), but this distinction is not normalized across product profiles.

## How the improvement works

Define a scoring layer that consumes the unified report rather than recalculating chemistry. Normalize three dimensions: compatibility feasibility, stability/shelf readiness, and commercial validation readiness. Each score should carry caps, penalties, confidence, and missing evidence. Blocking gates should cap relevant biological metrics (hydration) while advisory gaps reduce readiness and confidence. The stats card should display both raw biological potential and physically deliverable score.

## How it affects formula design decisions

Candidate ranking becomes more honest. A biologically attractive wet formula with 1309-2450 mOsm/L should not outrank a lower-glamour ORS that can actually hydrate. Conversely, a dry preload can retain biological score while carrying packaging/dose-uniformity validation requirements instead of wet-shelf penalties.

## Risks / unknowns

Scoring can hide a block if the display averages too much. The report must keep hard NO-GO gates visually separate from numeric readiness. Weighting may need calibration against field outcomes and lab results; early scores should be decision support, not a safety certificate.

## Validation checklist

- [ ] Stats-card reads normalized compat report fields rather than duplicating calculations.
- [ ] Hydration metric is capped when ORS gate blocks, with reason preserved.
- [ ] Shelf/commercial readiness remains low confidence without assay/challenge evidence.
- [ ] Hard blocks cannot be averaged away by strong biological actives.
- [ ] Report compares biological potential vs deliverable score for each candidate.

## Affected files / future touchpoints

- `calculated-stats-card-v3-upgraded.md`
- `calculated-stats-card-v3-upgraded.json`
- `compat/*.py`
- future: compat/scoring.py, stats-card integration point

## Evidence references

- `calculated-stats-card-v3-upgraded.md:52-71` shows solubility/TDS, osmolality block, shelf penalties, and hydration cap.
- `calculated-stats-card-v3-upgraded.md:124-156` shows V3 hybrid physical gate and hydration cap.
- Context snapshot topic 10 requests normalized scoring integrated with stats card.
