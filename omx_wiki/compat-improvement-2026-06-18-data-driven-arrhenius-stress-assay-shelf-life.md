---
title: "Compat improvement 7: Data-driven Arrhenius shelf-life projection from stress assays"
tags: ["compat-calculator", "stability", "research-improvement", "task-3", "gamefowl"]
created: 2026-06-18T07:20:00Z
updated: 2026-06-18T07:20:00Z
category: reference
confidence: medium
schemaVersion: 1
---

# Compat improvement 7: Data-driven Arrhenius shelf-life projection from stress assays

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

Medium — useful after prototypes exist; not a substitute for real-time data.

## Current repo state

`compat/arrhenius.py` implements generic Arrhenius, Q10, acceleration factor, and per-pathway projections from literature/assumed activation-energy ranges in `compat/data.py`. It already warns that low-Ea pathways such as ascorbate oxidation need real-time data because accelerated aging can under-predict ambient loss. There is no input format for observed assay data, no fitting of k/Ea from 25/30/40/50°C studies, and no confidence interval or endpoint model.

## How the improvement works

Add an assay-driven layer that accepts time/temperature/potency rows for a named pathway and fits first-order or pathway-specific degradation curves. It should estimate k at each temperature, fit Ea where justified, project shelf at target storage temperature, and compare against real-time data when available. The report should mark 50°C as stress-screen only when mechanisms can change and should keep ICH real-time requirements explicit.

## How it affects formula design decisions

Formulas stop claiming shelf-life from priors. A wet ribose/ascorbate/emulsion candidate can be screened early, but commercial readiness only improves when real matrix assays show potency, color, microbial, and physical stability. Dry or make-fresh designs can be favored when wet data are absent.

## Risks / unknowns

Arrhenius fits can be mathematically clean and chemically wrong if the degradation mechanism changes with temperature, oxygen, water activity, pH, or phase separation. Small data sets can produce misleading Ea. The module should prefer conservative bounds and require real-time confirmation before label shelf-life.

## Validation checklist

- [ ] Synthetic assay fixture recovers known Ea within tolerance.
- [ ] Ascorbate low-Ea pathway still forces real-time-data warning.
- [ ] Report distinguishes screening projection from label shelf-life claim.
- [ ] Supports multiple endpoints: potency, color, creatinine, peroxide, microbial/challenge where relevant.
- [ ] Missing assay data leaves shelf score confidence low rather than fabricating precision.

## Affected files / future touchpoints

- `compat/arrhenius.py`
- `compat/data.py`
- `calculated-stats-card-v3-upgraded.*`
- future: compat/stability_fit.py, data/stability_assays/*.csv

## Evidence references

- `compat/arrhenius.py:31-180` contains Q10/AF/pathway projection math.
- `compat/data.py:414-437` comments describe ascorbate oxidation and creatine cyclization Ea behavior.
- `.omc/wiki/...:61-67` states Tier 2 bench assays are required for true shelf-life.
