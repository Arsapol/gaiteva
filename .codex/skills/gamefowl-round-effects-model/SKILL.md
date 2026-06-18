---
name: gamefowl-round-effects-model
description: Models gamefowl supplement effects round by round across six 20-minute rounds with 20-minute rests. Use when the user asks about onset, peak, wearing off, signs to observe, redosing, capsule plus liquid timing, or per-round response during a fight protocol.
---

# Gamefowl Round Effects Model

Use this Skill to convert a formula, dosing time, and route plan into a **round-by-round effect model** for the project protocol: **6 rounds, 20 minutes fighting + 20 minutes rest**. The Skill focuses on timing, observable signs, redose decisions, and multi-route stacking.

This Skill does **not** replace `formula-safety-check`. If the answer proposes a new ingredient, dose increase, dose decrease, route change, or repeated dosing schedule that changes total exposure, also use `formula-safety-check` before presenting the recommendation as final.

## Inputs to collect or infer

If the user provides incomplete information, infer reasonable defaults and label them clearly.

- Bird weight range, usually 2.0-2.8 kg.
- Dose timing relative to round 1, such as 30, 45, 60, or 90 minutes pre-fight.
- All interventions, not just one capsule:
  - capsules or dry powders
  - liquids or oral drenches
  - sublingual drops
  - between-round hydration/electrolytes
  - cooling or handling actions
  - preload products from prior days
- Formula composition and dose per administration.
- Known field phenotype:
  - hot/aggressive/over-alert
  - balanced/precision type
  - dull/late-start/low-drive
  - heat-sensitive/panting-prone
  - crop/GI-sensitive
- Field observations from prior tests.

## Mandatory timeline

Always map dosing into the fixed fight timeline before interpreting effects.

For a dose given **30 min before round 1**:

| Phase | Time after dose |
|---|---:|
| Round 1 | 30-50 min |
| Rest 1 | 50-70 min |
| Round 2 | 70-90 min |
| Rest 2 | 90-110 min |
| Round 3 | 110-130 min |
| Rest 3 | 130-150 min |
| Round 4 | 150-170 min |
| Rest 4 | 170-190 min |
| Round 5 | 190-210 min |
| Rest 5 | 210-230 min |
| Round 6 | 230-250 min |

If the dose is given earlier or later, shift every row accordingly.

## Effect categories to model

Classify each ingredient or intervention by timing and role.

| Category | Typical examples | Modeling rule |
|---|---|---|
| Acute focus or drive | L-tyrosine, P5P, stimulant-like botanicals | Model onset, peak, precision risk, and duration. |
| Delayed precursor tail | L-phenylalanine to tyrosine hypothesis | Treat as plausible but unproven delayed support; do not claim precise release timing. |
| Chronic or preload support | creatine/GAA, glutamine, NAC, Mg, betaine | Credit mainly if given for days; single-event capsule gets only weak delayed-support credit unless field evidence says otherwise. |
| Rest-period support | glucose/electrolytes, DMG, citrulline, hydration, cooling | Model as recovery, heat, breathing, and refill support between rounds. |
| Risk modifiers | high tyrosine, rhodiola, protein/filler, high-osmolality liquids | Model over-arousal, GI load, crop load, transporter competition, and stacked stimulant burden. |

## Project field evidence to apply

Use these project observations unless the user supplies stronger newer field evidence:

- L-tyrosine around 130 mg can over-arouse some birds: continuous jumping or attacking, high drive, poor early accuracy, then accuracy returning around round 3 after energy expenditure.
- A non-fighting bird given tyrosine showed alertness for about 4 hours.
- Therefore, **alertness window is not the same as precision window**.
- Tyrosine may cover most or all of a six-round session, but high dose can overshoot the early sweet spot.
- Avoid routine mid-fight tyrosine re-dose unless signs clearly indicate low drive without heat stress or crop/GI load.

## Observable signs checklist

### Signs that effect is starting

| Domain | Useful signs |
|---|---|
| Alertness | brighter eyes, faster response to handler, more orientation to opponent |
| Drive | more willingness to engage, quicker launch, stronger forward intent |
| Motor control | stable landing, good balance, clean recovery after movement |
| Accuracy | fewer wasted jumps, better timing, higher hit quality |
| Breathing | faster is acceptable under load, but should settle during rest |
| Rest recovery | stands back up, posture resets, breathing decreases within rest period |

### Signs of sweet spot

- Alert but not frantic.
- Strike frequency may be moderate, but hit quality is high.
- Bird waits for timing instead of jumping continuously.
- Good landing, balance, and re-engagement.
- Handler response remains sharp without restless over-movement.
- Rest period produces visible reset.

### Signs of over-arousal or excessive catecholamine drive

- Jumping or attacking nonstop with poor accuracy.
- High output but wasted motion.
- Cannot wait for timing.
- Restless body language during rest.
- Breathing remains high while bird still tries to accelerate.
- Early rounds look powerful but inefficient.

When these signs appear, do **not** add more tyrosine, phenylalanine, rhodiola, or stimulant-like support. Prefer cooling, calm handling, hydration/electrolyte support, or waiting for arousal to settle.

### Signs that effect is wearing off

| Sign | More likely interpretation |
|---|---|
| slower response but still accurate | drive/focus tail declining |
| lower strike frequency with good timing | arousal settling, not necessarily failure |
| accuracy drops with fatigue | energy/heat/motor fatigue, not simply focus depletion |
| breathing does not settle in rest | heat/hydration/acid-base problem |
| crop feels heavy or swallowing slows | GI load; avoid more oral load |
| posture and balance degrade | fatigue, overheating, dehydration, or injury risk |

Do not equate "wearing off" with "needs another capsule". Choose the next intervention by signs.

## Multi-intervention ledger

Always list all interventions in one table before making a redose call.

| Time | Route | Product or action | Key actives | Intended role | Stack risk |
|---|---|---|---|---|---|

Include capsules, liquids, sublingual products, cooling, and prior preload. Then assess stacked burdens:

- total stimulant or catecholamine precursor load: tyrosine + phenylalanine + rhodiola or similar
- total B6 across capsule, drink, and preload
- total Mg across capsule, drink, and feed
- total sugar/osmolality and GI/crop load
- total liquid volume during rests
- overlapping antioxidant/redox actives such as NAC, ascorbate, metals
- heat stress and panting risk

## Redose decision rule

Redose decisions must be **state-based**, not fixed by clock alone.

| Current signs | Better action |
|---|---|
| high alert, poor accuracy, nonstop jumping | no stimulant; cool, calm, hydrate if crop allows |
| good alertness but panting or hot body | cooling plus electrolyte/hydration; avoid drive boosters |
| accurate but force drops | carbohydrate/electrolyte/recovery liquid if crop and breathing allow |
| low drive, calm breathing, crop not heavy | consider small booster matched to phenotype |
| heavy crop, slow swallowing, regurgitation risk | no more oral load |
| poor balance, abnormal posture, injury signs | stop performance dosing; prioritize welfare/veterinary assessment |

If considering a tyrosine or phenylalanine booster after round 3, first check whether the original tyrosine dose plausibly still covers round 4-6. If a prior field test showed about 4 hours of alertness, assume routine tyrosine re-dose is usually unnecessary.

## Required output format

Every analysis must include these sections:

1. **Assumptions and dose timing** — bird weight, formula, route, and dose time.
2. **Timeline table** — fixed six-round timing shifted to the actual dose time.
3. **Multi-intervention ledger** — all capsule, liquid, sublingual, cooling, and preload actions.
4. **Round-by-round prediction**:

| Round | Expected effect | Signs to watch | Risk | Handler action |
|---|---|---|---|---|
| R1 | | | | |
| R2 | | | | |
| R3 | | | | |
| R4 | | | | |
| R5 | | | | |
| R6 | | | | |

5. **Onset, peak, and wearing-off signs** — separate alertness from precision.
6. **Redose decision** — state-based recommendation with stop conditions.
7. **Formula implications** — whether to adjust tyrosine, phenylalanine, liquids, filler, or preload.
8. **Confidence and gaps** — distinguish field evidence, avian evidence, and inference.

## Phenotype-specific guidance

Use phenotype to avoid one-size-fits-all dosing.

| Phenotype | Default direction |
|---|---|
| hot or over-alert | lower tyrosine, remove or reduce phenylalanine/rhodiola, avoid mid-fight stimulant re-dose |
| balanced precision | moderate tyrosine, optional very low phenylalanine tail, emphasize hydration and cooling |
| dull or late-start | higher tyrosine only after field test; low phenylalanine may be tested for tail |
| late-round drop | prefer hydration/electrolyte/recovery support first; do not assume more focus precursor is needed |
| heat-sensitive | cooling and Cl-balanced electrolyte strategy outrank stimulant strategy |

## Safety and welfare guardrails

- Do not recommend dosing to mask injury, pain, severe fatigue, overheating, respiratory distress, or neurologic signs.
- If signs suggest heat stress, crop overload, poor balance, abnormal posture, or injury, prioritize stopping, cooling, hydration assessment, and veterinary care over performance support.
- Label unsupported claims clearly. Direct gamefowl round-by-round pharmacodynamic evidence is limited; many conclusions are field-informed inference.
