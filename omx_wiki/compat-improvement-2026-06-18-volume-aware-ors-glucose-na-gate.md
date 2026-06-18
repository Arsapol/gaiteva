---
title: "Compat improvement 2: Volume-aware electrolyte/ORS gate and glucose:Na ratio"
tags: ["compat-calculator", "stability", "research-improvement", "task-3", "gamefowl"]
created: 2026-06-18T07:20:00Z
updated: 2026-06-18T07:20:00Z
category: reference
confidence: medium
schemaVersion: 1
---

# Compat improvement 2: Volume-aware electrolyte/ORS gate and glucose:Na ratio

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

High — this is the most design-critical biological gate for hydration products.

## Current repo state

`compat/osmolality.py` computes mOsm/L from dissolved grams and water volume, then classifies the total against WHO/avian bands. It separately totals electrolyte millimoles but does not convert Na/K/Cl to mmol/L in the return object, and `complete_ors` currently means sodium is present rather than sodium, glucose, potassium, chloride, and ratio ranges being in-bounds. The demos show why this matters: the failing drench is ~1542 mOsm/L and lacks electrolytes; the reformulated ORS is ~274 mOsm/L with Na 74/K 20/Cl 65 mmol/L; the fight-day drink is ~291 mOsm/L with Na 52.7/K 14.8/Cl 64.4.

## How the improvement works

Promote `electrolyte_balance` into a volume-aware ORS evaluator. It should return mmol/L for Na, K, Cl, citrate/base equivalents, glucose/dextrose mmol/L, glucose:Na molar ratio, and separate gates for hydration drink, maintenance drink, and acute bolus. It should distinguish osmolarity (particles/L) from osmolality (particles/kg water) in naming, or explicitly label the current calculation as screening osmolarity. Add an `ors_profile` object with target ranges and a reasoned verdict.

## How it affects formula design decisions

Hydration formulas would be adjusted by dilution, dextrose form, and electrolyte salt choice instead of simply reducing total grams. The dextrose-monohydrate manufacturing spec becomes a hard design control because anhydrous substitution can push the 291 mOsm/L drink toward the cap. Designers can tune sodium and glucose together for SGLT1 water uptake rather than treating sugar as an independent energy lever.

## Risks / unknowns

Reference bands are species/use-case approximations, not a measured gamefowl clinical endpoint. Over-tight glucose:Na ranges may reject useful non-ORS acute products. The model also assumes dissolved fractions and ideal particle counts; dense sugar/salt matrices may require measured osmolality.

## Validation checklist

- [ ] Unit tests assert mmol/L, not just absolute mmol, for reformulated ORS and fight-day drink.
- [ ] Glucose:Na ratio is present and flagged when sodium or glucose is missing.
- [ ] Reports show osmolarity vs osmolality terminology clearly.
- [ ] Unknown molar mass or hydration state blocks ratio confidence rather than silently passing.
- [ ] Manufacturing spec check catches dextrose monohydrate vs anhydrous substitution.

## Affected files / future touchpoints

- `compat/osmolality.py`
- `compat/data.py`
- `substances/physical/default-compat-physical.json`
- `reformulate.py`
- `verify_dry_sku.py`
- future: compat/ors.py

## Evidence references

- `compat/osmolality.py:36-40` defines reference constants.
- `compat/osmolality.py:98-129` totals electrolyte millimoles but not mmol/L.
- Command evidence: `reformulate.py` outputs 274 mOsm/L, Na 74.1/K 20.1/Cl 64.6; `verify_dry_sku.py` outputs 291 mOsm/L, Na 52.7/K 14.8/Cl 64.4.


## Subagent-integrated edge cases

- Review probe found `compat/osmolality.py` currently labels the electrolyte gate as Na/K/Cl balance, but `complete_ors` is only `na > 0.0`; sodium-only formulas can pass the completeness flag. Future ORS work must test K/Cl sufficiency and glucose:Na ratio, not just sodium presence.
- Review probe found `compat/data.py` overlay loading is `Path.cwd()` sensitive. If the calculator is imported from a non-repo cwd, overlay-backed constants such as `magnesium_chloride` can disappear. Future registry work should resolve overlays relative to project root or module root.
- Review probe found unknown molar masses are surfaced but do not fail the osmolality gate; this can undercount osmoles. The unified report should downgrade confidence or block hydration claims when osmolarity-critical MW data are missing.
- Review probe found `compat/water_activity.py` threshold prose has a possible 0.85/0.91 wording mismatch even though classification math appears sound. Documentation and tests should cover prose as well as math for audit reliability.
