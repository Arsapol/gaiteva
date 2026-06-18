---
title: "Gamefowl Formula V3.1 — Dilution-Labeled Higher-Score Hybrid after Stats-card v0.2"
tags: ["gamefowl", "formula-v31", "stats-card-v0.2", "hydration", "osmolality", "dry-activator", "formula-safety-check", "avian", "fatigue-stress-recovery"]
created: 2026-06-17T00:00:00+07:00
updated: 2026-06-17T00:00:00+07:00
sources: [".omx/context/higher-score-formula-after-stats-upgrade-20260617T000000Z.md", "artifacts/calculated-stats-card-higher-score-candidates.md", "artifacts/calculated-stats-card-higher-score-candidates.json", "OMX team find-a-new-or-updated-33e79731 worker-1 probes Pauli/Noether/Goodall 2026-06-17", "gamefowl-formula-v3-high-score-hybrid-core-emulsion-dry-activato.md", "gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md", "gamefowl-supplement-avian-verdict.md"]
links: ["gamefowl-formula-v3-high-score-hybrid-core-emulsion-dry-activato.md", "gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md", "standardized-formulas-vnext2-per-100g-percent-and-usage-dose.md", "gamefowl-supplement-avian-verdict.md", "substance-betaine-anhydrous.md", "substance-l-citrulline-citrulline-malate.md", "substance-d-ribose.md", "substance-coenzyme-q10-ubiquinone-coq10.md"]
category: decision
confidence: medium
schemaVersion: 1
---

# Gamefowl Formula V3.1 — Dilution-Labeled Higher-Score Hybrid after Stats-card v0.2

## Decision summary

**Recommended calculator winner:** **V3.1 Dilution-Labeled Hybrid**.

It beats the current V3 final deliverable score **6.96/10 → 7.36/10** in the stats-card v0.2 calculator by fixing the hydration/osmolality cap while keeping the V3 biological stack unchanged.

The gain is **not** a new biological claim. It is mostly a physical-chemistry/delivery fix:

- V3 direct-dose osmolality: **1477 mOsm/L → BLOCK**, hydration capped at **2.50/10**.
- V3.1 labeled dilution: **5 mL wet core into 40 mL water**, calculated **~129 mOsm/L → PASS**, hydration score restores to **6.89/10**.
- The dry activator is **not dissolved into the 40 mL hydration water** unless separately recalculated; it remains a dry capsule/topdress or separate at-use dose. This avoids hiding solute load in the hydration calculation.

**GO-CONDITIONAL** for prototype. **NO-GO** for any claim that the stored wet bottle alone is a hydration aid when dosed neat, or for any stored wet all-in-one containing ribose + amines/B6/ascorbate/NAC.

No pain-tolerance claim is made. Framing is limited to **fatigue/stress tolerance, recovery support, hydration/electrolyte balance, and oxidative-stress support**.

## Score comparison (stats-card v0.2)

Calculator artifacts:

- Formula JSON: `artifacts/higher-score-candidates.json`
- Markdown card: `artifacts/calculated-stats-card-higher-score-candidates.md`
- JSON result: `artifacts/calculated-stats-card-higher-score-candidates.json`

| Formula | Final deliverable | Biological potential | Formulation feasibility | Hydration | Osmolality gate | Shelf readiness |
|---|---:|---:|---:|---:|---|---:|
| V3 Hybrid benchmark | 6.96 | 7.36 | 6.80 | 2.50 | 1477 mOsm/L → BLOCK | 7.45 |
| **V3.1 Dilution-Labeled Hybrid** | **7.36** | **7.36** | **8.43** | **6.89** | **129 mOsm/L → PASS** | **7.45** |
| V3.2 Light-Core Dilution Hybrid | 7.26 | 7.20 | 8.51 | 6.89 | 142 mOsm/L → PASS | 7.45 |
| V3.3 Dry Make-Fresh Recovery Drink + Oil Micelle/Softgel | 7.01 | 6.72 | 8.93 | 6.76 | 106 mOsm/L → PASS | 8.70 |

Interpretation:

- **V3.1 wins the calculator** because it keeps V3's effect profile while removing the osmolality cap.
- **V3.2** is safer for GI/oil burden but loses biological score from lower MCT/ribose.
- **V3.3** has the cleanest shelf/feasibility profile but lower energy score because MCT is removed.

## V3.1 formula candidate

### Bottle A — stored wet core emulsion, per 100 mL

Same active profile as V3; the required change is the **use instruction**, not higher concentration.

| Ingredient | Amount / 100 mL | Per 5 mL dose | Role |
|---|---:|---:|---|
| MCT oil | 20 mL | 1.0 mL | oil energy phase; GI/emulsion risk remains moderate |
| D-ribose | 6 g | 300 mg | field-supported recovery/ATP-pathway lever; published avian skeletal-muscle evidence remains weak |
| DMG | 2 g | 100 mg | avian heat/oxidative/gut/pulmonary-stress support; tertiary amine, formulation-friendly |
| L-carnitine L-tartrate | 1 g | 50 mg | chronic/preload-leaning energy/cardiopulmonary support |
| CoQ10 | 100 mg | 5 mg | chicken heat-stress mitochondrial ROS/oxidative support; oil-phase, chronic not acute stimulant |
| Vitamin E acetate | 200 mg | 10 mg | avian antioxidant/heat-stress support; stable oil-soluble vitamin E source |
| MgCl2 | 0.8 g target | 40 mg | Mg/electrolyte support; GI/dropping watch |
| NaCl | 0.5 g | 25 mg | chloride-balanced electrolyte |
| KCl | 0.2 g | 10 mg | potassium + chloride |
| Sodium citrate dihydrate | 0.25 g | 12.5 mg | trace buffer only, not heavy alkalinizer |
| Citric acid | q.s. pH 4.0–4.5 | q.s. | pH/preservative support |
| Lecithin + polysorbate 80 + low gum system | validated q.s. | — | emulsion system; must pass stability testing |
| Preservative | validated at actual pH | — | challenge test required |
| Distilled water | q.s. to 100 mL | — | aqueous phase |

### Use instruction that makes V3.1 different from V3

**Label-required hydration instruction:**

> Mix **5 mL Bottle A** into **at least 40 mL clean cool water** immediately before use. Offer as the hydration/electrolyte liquid. Do not dose neat as a hydration aid.

Important boundary:

- The **dry activator is delivered separately** as a capsule/topdress or dry-at-use dose.
- If the dry activator is instead dissolved into the same 40 mL drink, the osmolality must be recalculated; do **not** assume the 115 mOsm/L result still holds.

### Dry Activator B — separate, per event dose

| Ingredient | Working dose | Role / evidence confidence | Storage rule |
|---|---:|---|---|
| L-tyrosine | 100–250 mg | focus/catecholamine precursor; low avian direct acute evidence | dry only; low water solubility |
| B6/P5P or pyridoxine-HCl | 2–3 mg B6-equivalent | cofactor; keep total B6 under session cap | dry/light-protected only |
| Vitamin C / ascorbate | 50–100 mg | avian heat/stress antioxidant support; make-fresh if used | dry or make-fresh only |
| Taurine | 100–150 mg | heat-stress/antioxidant support but more chronic/conditional in birds | dry; avoid stored ribose/sugar liquids |
| Betaine anhydrous | 200–300 mg | strong avian osmolyte/heat-stress support | dry/desiccated or make-fresh |
| Creatine or GAA equivalent | 150–250 mg creatine equivalent | ATP/PCr score mainly when preloaded; GAA is dry-feed preferred | dry/preload only |

## Avian-evidence-first alternative: vNext2 dry ORS + preload

The calculator winner above is the fastest way to beat **6.96** using the existing v0.2 profiles. The stricter avian-evidence-first recommendation is the already-vetted **two dry-SKU architecture**:

1. **Fight-day dry ORS stick** mixed fresh to 1 L water:
   - dextrose monohydrate **22 g/L**
   - NaCl **2.9 g/L**
   - KCl **1.1 g/L**
   - citric acid **0.7 g/L**
   - sodium citrate dihydrate **0.3 g/L**
   - free L-citrulline **1.0–1.3 g/L**
   - DMG **0.3–0.5 g/L**
   - optional D-ribose **up to ~5 g/L** only if field-evidence weighting is desired and osmolality remains <300 mOsm/L
2. **Dry preload/feed SKU** for 7–10 days:
   - GAA or creatine monohydrate, betaine, NAC, taurine, L-carnitine/LCLT, magnesium feed source, B6/B12 micro-premix, optional glutamine/trehalose stabilizer.

Why it matters:

- Strongest poultry/avian levers for fatigue/stress/recovery are **chloride-balanced DEB management, betaine, free L-citrulline, chronic GAA/creatine, NAC/DMG, taurine, and L-carnitine**.
- This split keeps amines, thiols, B vitamins, ascorbate, magnesium, and low-solubility chronic actives out of the stored drink.
- The drink stays hypotonic and make-fresh; the preload carries slower biology.

This alternative is **GO** as the cleaner product architecture, but current stats-card v0.2 lacks built-in dextrose/citrulline/NAC profiles, so this worker did not claim a deterministic higher calculator score for it in the same way as V3.1.

## Formula-safety-check gate table

| Substance / change | R1 Solubility | R2 Stability | R3 Compatibility | Verdict |
|---|---|---|---|---|
| **V3.1 dilution instruction** | PASS: wet solutes diluted into 40 mL delivered water; calculated osmolality ~129 mOsm/L with MgCl2 hexahydrate included | make fresh; no storage after dilution | fixes hydration cap without changing stored bottle chemistry | ✅ GO — mandatory label instruction |
| **MCT oil 20% emulsion** | not water-soluble; emulsion only | oxidation/phase separation risk | oil-phase actives can distribute unevenly | ⚠️ GO-CONDITIONAL — droplet/phase/peroxide testing |
| **D-ribose 300 mg/dose** | soluble; TDS acceptable in stored V3 core | reducing sugar; Maillard risk if stored with primary amines/B6/ascorbate | keep amines/vitamins dry/separate | ⚠️ FIELD-CONDITIONAL — no strong published avian skeletal-muscle proof; do not increase |
| **DMG 100 mg/dose** | soluble | robust; hygroscopic dry forms | tertiary amine = low Maillard concern | ✅ OK |
| **LCLT 50 mg/dose** | soluble | stable pH 3–6; chronic uptake | Ca-tartrate precipitation only if Ca present | ✅ OK, but acute claim modest |
| **CoQ10 5 mg/dose** | oil-phase only | light/O2/heat sensitive; HPLC potency required | physical crystallization/phase separation risk | ⚠️ GO-CONDITIONAL |
| **Vitamin E acetate 10 mg/dose** | oil-soluble | comparatively stable, but potency assay needed | compatible with oil phase; not counted as strong preservative | ⚠️ GO-CONDITIONAL |
| **MgCl2 40 mg/dose** | soluble | stable | MgCl2 hexahydrate osmoles now included in calculator; GI/droppings watch | ⚠️ FLAG |
| **NaCl + KCl + trace citrate** | soluble | stable salts | chloride-balanced; avoid heavy citrate alkalinization | ✅ OK |
| **L-tyrosine dry** | liquid solubility poor near pI; dry avoids issue | dry stable | LNAA competition; wet precipitation | ✅ dry only |
| **B6/P5P dry** | soluble but wet P5P/B6 is loss-prone | photolysis/Schiff-base risk in wet | sugars/amines accelerate loss | ✅ dry only; ❌ wet bottle |
| **Ascorbate/Vit C** | soluble | oxidizes in solution, metal/light/O2 sensitive | redox with Cu/metals; reducing-sugar matrix risk | ⚠️ dry/make-fresh only |
| **Taurine** | soluble | stable, but can brown with reducing sugars over storage | primary amine + ribose/glucose Maillard risk | ✅ dry/preload; avoid stored sugar liquid |
| **Betaine** | highly soluble/stable | hygroscopic as dry powder | no primary amine Maillard; methyl donor pairs with GAA | ✅ strong avian support, dry/desiccated |
| **GAA/creatine** | GAA low solubility; creatine moderate | wet degradation/creatinine risk | GAA methyl demand → pair with betaine/choline | ✅ dry preload only; ❌ drink/storage liquid |
| **NAC** | soluble but not the issue | thiol oxidizes in wet/O2/metals | redox with ascorbate/metals | ✅ dry preload; ❌ stored liquid |
| **Free L-citrulline** | soluble at drink dose | dry/make-fresh preferred | reducing sugar + amine can brown in stored wet product | ✅ make-fresh ORS; not stored wet |

## GO / NO-GO

**GO-CONDITIONAL: V3.1 Dilution-Labeled Hybrid prototype.**

Conditions:

1. Label requires **5 mL Bottle A diluted into ≥40 mL water** before it is counted as hydration support.
2. Dry activator stays **separate** from that hydration water unless the full mixed drink is recalculated and remains <300–320 mOsm/L.
3. 6-month shelf-life is only **plausible after validation**; 12-month shelf-life remains **unconfirmed**.
4. Required tests: preservative challenge at final pH, emulsion centrifuge/heat-cool/freeze-thaw, droplet size, pH drift, viscosity/syringeability, color/browning, peroxide/anisidine/rancidity, CoQ10/vitamin E potency/distribution.
5. Field observations must track intake, droppings/GI tolerance, recovery behavior, heat-stress signs, and calm alertness; do not claim pain tolerance.

**NO-GO:**

- neat 5 mL wet core marketed as hydration support;
- stored wet all-in-one with ribose/glucose + amino acids/taurine/B6/ascorbate/NAC;
- double-concentrated ORS or handler instruction to make it stronger;
- any 12-month shelf-life claim without real stability data.

## Subagent / peer review evidence

Subagents spawned: **3**, model **gpt-5.4-mini**.

- **Pauli** — osmolality candidate probe: confirmed the winning move is hypotonic delivery; suggested vNext2 dry ORS at ~258–291 mOsm/kg and warned the hydration cap returns if concentrated.
- **Noether** — shelf-life/safety probe: confirmed split architecture, chloride salts over citrate-heavy alkalinization, dry storage for NAC/B6/ascorbate/taurine/betaine/LCLT/GAA, and GO-conditional oil phase only after emulsion/potency tests.
- **Goodall** — avian evidence probe: ranked betaine, free L-citrulline, chloride-balanced electrolytes, GAA/creatine preload, NAC/DMG/taurine/LCLT above ribose for avian fatigue/stress/recovery confidence; reinforced no pain-tolerance framing.

Findings integrated:

- V3.1 is the deterministic calculator winner.
- vNext2 dry ORS/preload is the stronger avian-evidence architecture when product redesign is allowed.
- Ribose is retained only as field-supported/conditional, not as strong avian-published evidence.
- Dry activator must not be silently dissolved into the hydration calculation.

## Changelog

- 2026-06-17: Corrected MgCl2 osmolality constants in `compat.data`; V3.1 osmolality updated from ~115 to ~129 mOsm/L, still PASS.
- 2026-06-17: Created by OMX team `find-a-new-or-updated-33e79731` worker-1 after stats-card v0.2 upgrade; calculator artifacts generated under `artifacts/`.


---

## Update 2026-06-17 — CoQ10 no longer preferred in V3.x Bottle A

**Decision memory:** remove/de-prefer **CoQ10** from the default V3.1/V3.x Bottle A path because it is hard to mix reliably: water-insoluble, oil-phase-only, prone to crystallization/uneven distribution, and requires finished-emulsion HPLC potency/distribution testing.

**Default next prototype direction:** V3.2 should use a simpler Bottle A:
- keep the dilution rule (**5 mL into ≥40 mL water**);
- keep MCT/ribose/DMG/electrolyte core if field performance is desired;
- keep **vitamin E acetate** as the easier oil-phase antioxidant/vitamin E support;
- move antioxidant/focus complexity to **dry activator / preload** (ascorbate, taurine, betaine, NAC if preload, B vitamins dry only);
- reserve CoQ10 only for a separate oil capsule or premium variant after solubility/distribution/potency testing.

**Gate implication:** CoQ10 row in prior V3.1 gate should be read as **⚠️ REMOVE-BY-DEFAULT / premium-only**, not as a default GO ingredient.

**Changelog:** 2026-06-17: User corrected the formula direction; CoQ10 removed as default preferred active and alternative stack is vitamin E acetate + dry antioxidants.
