---
name: gamefowl-formula-review-workflow
description: Routes complete gamefowl formula reviews through safety, round-by-round effects, and scoring checks. Use when the user asks to check, analyze, review, improve, compare, redesign, or plan dosing for a gamefowl formula, especially capsule plus liquid protocols.
---

# Gamefowl Formula Review Workflow

Use this Skill as a lightweight router when the user asks for a broad gamefowl formula review. It coordinates the more specific project Skills so formula answers do not miss safety, timing, signs, redose, or scoring layers.

Do not use this Skill for isolated fact questions such as "what is MCC", "what is tyrosine", or "check only NAC solubility" unless the user also asks for a formula-level recommendation.

## Trigger examples

Use this Skill when the user asks:

- "check this formula"
- "analyze this formula"
- "review pros and cons"
- "improve this formula"
- "compare these formulas"
- "what should I give each round"
- "capsule plus liquid protocol"
- "should I repeat dose after round 3"
- "ออกฤทธิ์แต่ละยกยังไง"
- "ควรให้ซ้ำไหม"

## Required workflow

### Step 1 — Define the review frame

State assumptions before analysis:

- bird weight range
- fight protocol, defaulting to 6 rounds with 20 minutes fighting and 20 minutes rest
- product route or routes: capsule, dry powder, liquid, sublingual, preload, cooling
- timing of each administration
- whether the request is safety, effect timing, scoring, redesign, or all of them
- new field observations that should update wiki or memory

### Step 2 — Formula safety gate

Use `formula-safety-check` when the answer includes any of these:

- proposing a new formula
- changing an ingredient
- changing a dose
- adding a repeat dose
- moving an ingredient between capsule, liquid, sublingual, or preload
- recommending a stored liquid or make-fresh liquid
- discussing solubility, stability, compatibility, B6, Mg, pH, osmolality, or ingredient conflicts

Output at least a compact safety verdict. For high-risk or new ingredients, include the full 3-rule table required by `formula-safety-check`.

### Step 3 — Round-by-round effects model

Use `gamefowl-round-effects-model` whenever timing, redose, signs, or fight protocol matters.

The answer must include:

- timeline for all 6 rounds shifted to the actual dose time
- multi-intervention ledger for capsule, liquid, sublingual, preload, and cooling
- expected effect per round
- signs to watch when effect starts, peaks, and wears off
- over-arousal and heat/GI warning signs
- state-based redose recommendation, not clock-only redose

### Step 4 — Stats or comparison layer

Use `gamefowl-formula-stats-card` when the user asks to score, compare, rank, improve, or choose between formulas.

If no explicit score is requested, give only a short qualitative score summary such as high, medium, low confidence across:

- focus and precision
- energy and force
- fatigue resistance
- recovery between rounds
- antioxidant and heat stress support
- hydration and electrolytes
- GI/crop tolerance
- onset and duration

### Step 5 — Field evidence capture

If the user reports a real test result, field observation, or phenotype response:

- summarize it as field evidence before using it as a conclusion
- update `omx_wiki/` through the OMX wiki surface when persistent value is high
- add memory/notepad when it changes future dosing logic
- distinguish n=1 field evidence from peer-reviewed or avian evidence

### Step 6 — Final recommendation structure

For formula-level reviews, prefer this output order:

1. Bottom line
2. Assumptions
3. Safety verdict
4. Round-by-round effects and signs
5. Redose or multi-route protocol
6. Pros and cons
7. Improvements or variants by phenotype
8. Confidence and gaps

## Routing rules

- If the user asks only for a definition, answer directly and do not expand into a full workflow.
- If the user asks for only chemistry or solubility, use `formula-safety-check` without this router unless a formula-level recommendation is needed.
- If the user asks only for round timing, signs, or redose, use `gamefowl-round-effects-model`; this router can stay implicit.
- If the user asks broad formula review, run the full workflow.
- If workflow steps conflict, safety and welfare override scoring or performance recommendations.

## Stop conditions

Do not recommend additional performance dosing when signs indicate:

- overheating or panting that does not settle during rest
- crop overload, slow swallowing, or regurgitation risk
- poor balance, abnormal posture, or suspected injury
- over-arousal with poor accuracy and nonstop jumping
- unknown total B6, Mg, stimulant, or osmolality load after repeated products

In those cases, recommend cooling, hydration assessment, stopping further oral load, or veterinary/welfare action as appropriate.
