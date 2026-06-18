---
title: "Compat improvement 9: Separate gates by product/use-case: hydration drink, acute sublingual, dry capsule, wet concentrate"
tags: ["compat-calculator", "stability", "research-improvement", "task-3", "gamefowl"]
created: 2026-06-18T07:20:00Z
updated: 2026-06-18T07:20:00Z
category: reference
confidence: medium
schemaVersion: 1
---

# Compat improvement 9: Separate gates by product/use-case: hydration drink, acute sublingual, dry capsule, wet concentrate

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

High — avoids both false blocks and false passes.

## Current repo state

The current code strongly models water-based hydration products. `verify_dry_sku.py` manually explains that Products 1 and 2 are eaten dry and therefore do not have a standing-solution osmolality gate; Product 3 reconstituted in 1 L does. `calculated-stats-card-v3-upgraded.md` separately applies wet-core/emulsion penalties. There is not yet a formal `use_case` gate profile controlling which checks are blocking vs advisory.

## How the improvement works

Define gate profiles for at least four use cases: hydration drink/reconstituted ORS, acute sublingual/bolus, dry capsule/premix, and wet concentrate/emulsion. Each profile should specify required inputs, blocking gates, advisory gates, validation evidence, and what claims are allowed. For example, hydration drink requires volume-aware ORS; dry capsule requires aw/hygroscopicity/caking/dose uniformity; wet concentrate requires preservative challenge, emulsion stability, redox, and dilution instructions.

## How it affects formula design decisions

A dry tyrosine focus capsule should not be rejected for in-bottle solubility, while a wet hydration claim should be blocked for hyperosmolar load even if actives dissolve. This supports product architecture decisions: split dry/wet systems, same-day reconstitution, and dilution labeling can be scored on their actual risk surfaces.

## Risks / unknowns

Use-case labels can be abused to bypass a real exposure. A dry stick becomes a liquid when reconstituted; a concentrate must be evaluated at both bottle concentration and use dilution. The profile should force explicit route, water volume, hold time, and claim type.

## Validation checklist

- [ ] Dry products return `osmolality_exempt` only when no standing liquid claim exists.
- [ ] Reconstituted dry stick runs hydration-drink gate at labeled volume.
- [ ] Wet concentrate evaluates both stored concentrate and use dilution.
- [ ] Sublingual/acute profile includes mucosal tolerance and bolus osmotic caution without pretending to be ORS.
- [ ] Stats-card scoring uses the same use-case profile as compat report.

## Affected files / future touchpoints

- `verify_dry_sku.py`
- `compat/osmolality.py`
- `calculated-stats-card-v3-upgraded.*`
- future: compat/profiles.py

## Evidence references

- `verify_dry_sku.py` output: dry Products 1/2 have no standing-solution osmolality gate; Product 3 drink is 291 mOsm/L PASS.
- `calculated-stats-card-v3-upgraded.md:124-156` shows wet-core-plus-dry-activator physical gate notes.
- Context snapshot improvement topic 9 explicitly requests separate gates by use-case.


## Subagent-integrated edge cases

- Review probe found `compat/osmolality.py` currently labels the electrolyte gate as Na/K/Cl balance, but `complete_ors` is only `na > 0.0`; sodium-only formulas can pass the completeness flag. Future ORS work must test K/Cl sufficiency and glucose:Na ratio, not just sodium presence.
- Review probe found `compat/data.py` overlay loading is `Path.cwd()` sensitive. If the calculator is imported from a non-repo cwd, overlay-backed constants such as `magnesium_chloride` can disappear. Future registry work should resolve overlays relative to project root or module root.
- Review probe found unknown molar masses are surfaced but do not fail the osmolality gate; this can undercount osmoles. The unified report should downgrade confidence or block hydration claims when osmolarity-critical MW data are missing.
- Review probe found `compat/water_activity.py` threshold prose has a possible 0.85/0.91 wording mismatch even though classification math appears sound. Documentation and tests should cover prose as well as math for audit reliability.
