# Calculated Formula Stats Card

> v0.2 calculation: deterministic expert-scoring from ingredient dose profiles + evidence multipliers + physical-chemistry gates. Scores are comparable estimates, not proof of efficacy.

## Model layers

- **Biological potential**: what the active profile could do before delivery/stability caps.
- **Formulation feasibility**: solubility + osmolality + GI/emulsion + shelf-readiness gate score.
- **Final deliverable score**: the score after physical caps/penalties.

## Score comparison

| Metric | Route A Wet Core | V3 Hybrid Core Emulsion + Dry Activator |
|---|---:|---:|
| Focus / alertness | 0.57 | 5.48 |
| Energy availability | 7.83 | 7.05 |
| Fatigue/stress tolerance | 6.45 | 8.53 |
| Fast recovery | 7.89 | 8.47 |
| ATP regeneration | 6.42 | 8.21 |
| Anti-inflammatory / antioxidant support | 4.48 | 8.68 |
| Respiratory / acid-base support | 6.12 | 6.67 |
| Hydration / electrolyte balance | 2.07 | 2.50 |
| GI tolerance | 6.10 | 7.25 |
| Onset speed | 4.67 | 6.25 |
| Shelf stability / commercial readiness | 3.70 | 7.45 |
| **Overall average** | **5.12** | **6.96** |

## Layer comparison

| Formula | Biological potential | Formulation feasibility | Final deliverable average |
|---|---:|---:|---:|
| Route A Wet Core | 5.17 | 4.83 | 5.12 |
| V3 Hybrid Core Emulsion + Dry Activator | 7.36 | 6.80 | 6.96 |

## Rollups

| Formula | Performance support | Recovery/welfare | Commercial readiness |
|---|---:|---:|---:|
| Route A Wet Core | 5.68 | 5.33 | 3.70 |
| V3 Hybrid Core Emulsion + Dry Activator | 7.38 | 6.71 | 7.45 |

## Route A Wet Core — calculation notes

- Architecture: `single_wet_bottle`
- Final deliverable overall: **5.12/10**
- Biological potential: **5.17/10**
- Formulation feasibility: **4.83/10**
- Raw contribution points: `{"antiox": 1.785, "atp": 3.078, "energy": 4.584, "fatigue": 3.109, "focus": 0.175, "gi": 0.186, "hydration": 0.696, "onset": 1.886, "recovery": 4.674, "resp": 2.84}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | TIGHT; TDS 34.33% w/v | 7.00 |
| Osmolality / ORS | 2646 mOsm/L → BLOCK | hydration cap 2.50 |
| GI / emulsion burden | see notes | 6.10 |
| Shelf / commercial readiness | see notes | 3.70 |

### Penalty / cap ledger

| Target | Delta / cap | Reason |
|---|---:|---|
| GI | -0.7 | MCT oil burden |
| GI | -0.8 | high-oil emulsion burden |
| GI | -0.4 | emulsion not validated |
| Shelf | -2.3 | wet reducing sugar + primary amine Maillard/browning risk; wet ribose + ascorbate/redox shelf risk |
| Shelf | -1.1 | 30% oil emulsion risk |
| Shelf | -0.8 | emulsion stability not validated |
| Shelf | -0.8 | preservative challenge not validated |
| Shelf | -0.3 | TDS >20% w/v: salting-out / crystallization risk |
| Hydration cap | cap 2.5 | 2646 mOsm/L -> BLOCK: > 350 mOsm/L — HYPERTONIC. Pulls water into gut lumen, worsens dehydration. Must dilute / cut dose before use as hydration aid. |
| Hydration cap | cap 2.5 | UNKNOWN osmoles for: taurine (molar mass missing in registry; osmolarity is under-estimated) |

### Physical gate notes
- GI: MCT 1.5 mL/dose adds oil/GI burden
- GI: high-oil emulsion burden
- GI: emulsion not validated
- Shelf: 6+ month target active
- Shelf: wet reducing sugar + primary amine Maillard/browning risk
- Shelf: wet ribose + ascorbate/redox shelf risk
- Shelf: 30% oil emulsion needs separation/oxidation testing
- Shelf: emulsion stability not validated
- Shelf: preservative challenge not validated
- Shelf: TDS >20% w/v: salting-out / crystallization risk
- Osmolality: 2646 mOsm/L -> BLOCK: > 350 mOsm/L — HYPERTONIC. Pulls water into gut lumen, worsens dehydration. Must dilute / cut dose before use as hydration aid.
- Osmolality: UNKNOWN osmoles for: taurine (molar mass missing in registry; osmolarity is under-estimated)
- Solubility: no bottlenecks; TDS 34.33% w/v

### Metric confidence

| Metric | Final score | Biological potential | Confidence | Notes |
|---|---:|---:|---|---|
| Focus / alertness | 0.57 | 0.57 | Medium |  |
| Energy availability | 7.83 | 7.83 | Medium |  |
| Fatigue/stress tolerance | 6.45 | 6.45 | Medium |  |
| Fast recovery | 7.89 | 7.89 | Medium |  |
| ATP regeneration | 6.42 | 6.42 | Medium |  |
| Anti-inflammatory / antioxidant support | 4.48 | 4.48 | Medium |  |
| Respiratory / acid-base support | 6.12 | 6.12 | Medium |  |
| Hydration / electrolyte balance | 2.07 | 2.07 | Low |  |
| GI tolerance | 6.10 | 8.00 | Low | MCT 1.5 mL/dose adds oil/GI burden; high-oil emulsion burden; emulsion not validated |
| Onset speed | 4.67 | 4.67 | Medium |  |
| Shelf stability / commercial readiness | 3.70 | 9.00 | Low | 6+ month target active; wet reducing sugar + primary amine Maillard/browning risk; wet ribose + ascorbate/redox shelf risk; 30% oil emulsion needs separation/oxidation testing; emulsion stability not validated; preservative challenge not validated; TDS >20% w/v: salting-out / crystallization risk |

### Ingredient contribution rows

| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |
|---|---:|---|---|---:|---:|---|---|
| MCT oil | 1.5 mL | oil | field | 1.23 | 1.00 | energy:2.915, fatigue:0.729, onset:0.833 | Oil energy; score capped by emulsion/GI tolerance. |
| D-ribose | 500 mg | wet | field | 1.29 | 1.00 | atp:2.195, energy:1.427, onset:0.878, recovery:1.975 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 150 mg | wet | avian_indirect | 1.23 | 1.00 | antiox:0.588, fatigue:1.372, recovery:0.784, resp:1.47 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| LCLT | 100 mg | wet | avian_indirect | 1.35 | 1.00 | atp:0.243, energy:0.243, fatigue:0.389, recovery:0.486, resp:0.389 | More preload/chronic than acute. |
| MgCl2 | 40 mg | wet | avian_indirect | 1.00 | 1.00 | atp:0.64, hydration:0.48, recovery:0.4, resp:0.24 | Mg-ATP/electrolyte support; GI cap applies. |
| Sodium citrate | 125 mg | wet | avian_indirect | 1.35 | 1.00 | hydration:0.216, resp:0.432 | Small buffer; penalize if over-used as alkali load. |
| Taurine | 75 mg | wet | avian_indirect | 0.78 | 1.00 | antiox:0.496, fatigue:0.62, gi:0.186, recovery:0.62, resp:0.31 | Dry/make-fresh preferred with ribose. |
| Sodium ascorbate | 40 mg | wet | avian_indirect | 0.73 | 1.00 | antiox:0.701, focus:0.175, onset:0.175, recovery:0.409 | Useful make-fresh; wet storage loses potency. |

## V3 Hybrid Core Emulsion + Dry Activator — calculation notes

- Architecture: `wet_core_plus_dry_activator`
- Final deliverable overall: **6.96/10**
- Biological potential: **7.36/10**
- Formulation feasibility: **6.80/10**
- Raw contribution points: `{"antiox": 6.08, "atp": 5.155, "energy": 3.665, "fatigue": 5.743, "focus": 2.385, "gi": 0.24, "hydration": 3.506, "onset": 2.945, "recovery": 5.63, "resp": 3.3}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | PASS; TDS 15.36% w/v | 10.00 |
| Osmolality / ORS | 1477 mOsm/L → BLOCK | hydration cap 2.50 |
| GI / emulsion burden | see notes | 7.25 |
| Shelf / commercial readiness | see notes | 7.45 |

### Penalty / cap ledger

| Target | Delta / cap | Reason |
|---|---:|---|
| GI | -0.35 | moderate oil emulsion burden |
| GI | -0.4 | emulsion not validated |
| Shelf | -0.45 | 20% oil emulsion risk |
| Shelf | -0.8 | emulsion stability not validated |
| Shelf | -0.8 | preservative challenge not validated |
| Shelf | 0.8 | dry activator removes wet incompatibilities |
| Shelf | -0.3 | oil-phase active distribution assay needed |
| Hydration cap | cap 2.5 | 1477 mOsm/L -> BLOCK: > 350 mOsm/L — HYPERTONIC. Pulls water into gut lumen, worsens dehydration. Must dilute / cut dose before use as hydration aid. |

### Physical gate notes
- GI: moderate oil emulsion burden
- GI: emulsion not validated
- Shelf: 6+ month target active
- Shelf: 20% oil emulsion needs separation/oxidation testing
- Shelf: emulsion stability not validated
- Shelf: preservative challenge not validated
- Shelf: dry activator removes high-risk wet amines/vitamins
- Shelf: oil-phase actives need potency/distribution assay
- Osmolality: 1477 mOsm/L -> BLOCK: > 350 mOsm/L — HYPERTONIC. Pulls water into gut lumen, worsens dehydration. Must dilute / cut dose before use as hydration aid.
- Solubility: no bottlenecks; TDS 15.36% w/v

### Metric confidence

| Metric | Final score | Biological potential | Confidence | Notes |
|---|---:|---:|---|---|
| Focus / alertness | 5.48 | 5.48 | Low |  |
| Energy availability | 7.05 | 7.05 | Medium |  |
| Fatigue/stress tolerance | 8.53 | 8.53 | High |  |
| Fast recovery | 8.47 | 8.47 | Medium |  |
| ATP regeneration | 8.21 | 8.21 | Medium |  |
| Anti-inflammatory / antioxidant support | 8.68 | 8.68 | High |  |
| Respiratory / acid-base support | 6.67 | 6.67 | Medium |  |
| Hydration / electrolyte balance | 2.50 | 6.89 | Medium | hydration capped at 2.50 by osmolality/electrolyte gate |
| GI tolerance | 7.25 | 8.00 | Low | moderate oil emulsion burden; emulsion not validated |
| Onset speed | 6.25 | 6.25 | Medium |  |
| Shelf stability / commercial readiness | 7.45 | 9.00 | Medium | 6+ month target active; 20% oil emulsion needs separation/oxidation testing; emulsion stability not validated; preservative challenge not validated; dry activator removes high-risk wet amines/vitamins; oil-phase actives need potency/distribution assay |

### Ingredient contribution rows

| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |
|---|---:|---|---|---:|---:|---|---|
| MCT oil | 1 mL | oil | field | 1.00 | 1.00 | energy:2.38, fatigue:0.595, onset:0.68 | Oil energy; score capped by emulsion/GI tolerance. |
| D-ribose | 300 mg | wet | field | 1.00 | 1.00 | atp:1.7, energy:1.105, onset:0.68, recovery:1.53 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 100 mg | wet | avian_indirect | 1.00 | 1.00 | antiox:0.48, fatigue:1.12, recovery:0.64, resp:1.2 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| LCLT | 50 mg | wet | avian_indirect | 1.00 | 1.00 | atp:0.18, energy:0.18, fatigue:0.288, recovery:0.36, resp:0.288 | More preload/chronic than acute. |
| CoQ10 | 5 mg | oil | avian | 1.00 | 1.00 | antiox:1.8, atp:1.0, fatigue:0.6 | Chicken heat-stress mitochondrial ROS support; not acute stimulant proof. |
| Vitamin E acetate | 10 mg | oil | avian | 1.00 | 1.00 | antiox:1.6, fatigue:0.4 | Stable vitamin E source; not counted as strong in-bottle oil preservative. |
| MgCl2 | 40 mg | wet | avian_indirect | 1.00 | 1.00 | atp:0.64, hydration:0.48, recovery:0.4, resp:0.24 | Mg-ATP/electrolyte support; GI cap applies. |
| NaCl | 25 mg | wet | avian_indirect | 1.00 | 1.00 | hydration:0.96, onset:0.24, resp:0.48 | Cl-balanced hydration/acid-base support. |
| KCl | 10 mg | wet | avian_indirect | 1.00 | 1.00 | hydration:0.72, resp:0.4 | K/Cl electrolyte support. |
| Sodium citrate | 12.5 mg | wet | avian_indirect | 0.91 | 1.00 | hydration:0.146, resp:0.292 | Small buffer; penalize if over-used as alkali load. |
| L-tyrosine | 200 mg | dry | mechanism | 1.00 | 1.00 | focus:1.56, onset:0.91 | Dry-only focus lever; low water solubility. |
| B6/P5P | 2.5 mg | dry | mechanism | 1.00 | 1.00 | atp:0.195, focus:0.585, onset:0.195 | Cofactor; keep dry/light-protected. |
| Vitamin C | 75 mg | dry | avian_indirect | 1.00 | 1.00 | antiox:0.96, focus:0.24, onset:0.24, recovery:0.56 | Useful make-fresh; wet storage loses potency. |
| Taurine | 125 mg | dry | avian_indirect | 1.00 | 1.00 | antiox:0.64, fatigue:0.8, gi:0.24, recovery:0.8, resp:0.4 | Dry/make-fresh preferred with ribose. |
| Betaine | 250 mg | dry | avian | 1.00 | 1.00 | antiox:0.6, fatigue:1.3, hydration:1.2, recovery:0.7 | Osmolyte/methyl donor; strong heat-stress support. |
| Creatine/GAA preload equivalent | 200 mg | dry | avian_indirect | 1.00 | 1.00 | atp:1.44, fatigue:0.64, recovery:0.64 | ATP/PCr score mainly if preloaded; wet degradation risk. |
