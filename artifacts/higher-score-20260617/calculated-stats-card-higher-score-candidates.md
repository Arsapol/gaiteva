# Calculated Formula Stats Card

> v0.2 calculation: deterministic expert-scoring from ingredient dose profiles + evidence multipliers + physical-chemistry gates. Scores are comparable estimates, not proof of efficacy.

## Model layers

- **Biological potential**: what the active profile could do before delivery/stability caps.
- **Formulation feasibility**: solubility + osmolality + GI/emulsion + shelf-readiness gate score.
- **Final deliverable score**: the score after physical caps/penalties.

## Score comparison

| Metric | V3.1 Dilution-Labeled Hybrid (5 mL core into 40 mL water + dry activator) | V3.2 Light-Core Dilution Hybrid (10% oil, 5 mL into 30 mL water + dry activator) | V3.3 Dry Make-Fresh Recovery Drink + Oil Micelle/Softgel |
|---|---:|---:|---:|
| Focus / alertness | 5.48 | 5.48 | 5.48 |
| Energy availability | 7.05 | 6.16 | 3.27 |
| Fatigue/stress tolerance | 8.53 | 8.44 | 8.06 |
| Fast recovery | 8.47 | 8.40 | 8.31 |
| ATP regeneration | 8.21 | 8.12 | 8.12 |
| Anti-inflammatory / antioxidant support | 8.68 | 8.68 | 8.62 |
| Respiratory / acid-base support | 6.67 | 6.67 | 6.62 |
| Hydration / electrolyte balance | 6.89 | 6.89 | 6.76 |
| GI tolerance | 7.25 | 7.60 | 8.00 |
| Onset speed | 6.25 | 5.92 | 5.21 |
| Shelf stability / commercial readiness | 7.45 | 7.45 | 8.70 |
| **Overall average** | **7.36** | **7.26** | **7.01** |

## Layer comparison

| Formula | Biological potential | Formulation feasibility | Final deliverable average |
|---|---:|---:|---:|
| V3.1 Dilution-Labeled Hybrid (5 mL core into 40 mL water + dry activator) | 7.36 | 8.43 | 7.36 |
| V3.2 Light-Core Dilution Hybrid (10% oil, 5 mL into 30 mL water + dry activator) | 7.20 | 8.51 | 7.26 |
| V3.3 Dry Make-Fresh Recovery Drink + Oil Micelle/Softgel | 6.72 | 8.93 | 7.01 |

## Rollups

| Formula | Performance support | Recovery/welfare | Commercial readiness |
|---|---:|---:|---:|
| V3.1 Dilution-Labeled Hybrid (5 mL core into 40 mL water + dry activator) | 7.38 | 7.59 | 7.45 |
| V3.2 Light-Core Dilution Hybrid (10% oil, 5 mL into 30 mL water + dry activator) | 7.12 | 7.65 | 7.45 |
| V3.3 Dry Make-Fresh Recovery Drink + Oil Micelle/Softgel | 6.28 | 7.66 | 8.70 |

## V3.1 Dilution-Labeled Hybrid (5 mL core into 40 mL water + dry activator) — calculation notes

- Architecture: `wet_core_plus_dry_activator`
- Final deliverable overall: **7.36/10**
- Biological potential: **7.36/10**
- Formulation feasibility: **8.43/10**
- Raw contribution points: `{"antiox": 6.08, "atp": 5.155, "energy": 3.665, "fatigue": 5.743, "focus": 2.385, "gi": 0.24, "hydration": 3.506, "onset": 2.945, "recovery": 5.63, "resp": 3.3}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | PASS; TDS 15.36% w/v | 10.00 |
| Osmolality / ORS | 129 mOsm/L → PASS | hydration cap 10.00 |
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

### Physical gate notes
- GI: moderate oil emulsion burden
- GI: emulsion not validated
- Shelf: 6+ month target active
- Shelf: 20% oil emulsion needs separation/oxidation testing
- Shelf: emulsion stability not validated
- Shelf: preservative challenge not validated
- Shelf: dry activator removes high-risk wet amines/vitamins
- Shelf: oil-phase actives need potency/distribution assay
- Osmolality: 129 mOsm/L -> PASS: <= 320 mOsm/L — within isotonic-ish hydration band
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
| Hydration / electrolyte balance | 6.89 | 6.89 | Medium |  |
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

## V3.2 Light-Core Dilution Hybrid (10% oil, 5 mL into 30 mL water + dry activator) — calculation notes

- Architecture: `wet_core_plus_dry_activator`
- Final deliverable overall: **7.26/10**
- Biological potential: **7.20/10**
- Formulation feasibility: **8.51/10**
- Raw contribution points: `{"antiox": 6.08, "atp": 5.007, "energy": 2.872, "fatigue": 5.569, "focus": 2.385, "gi": 0.24, "hydration": 3.506, "onset": 2.687, "recovery": 5.497, "resp": 3.3}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | PASS; TDS 12.19% w/v | 10.00 |
| Osmolality / ORS | 161 mOsm/L → PASS | hydration cap 10.00 |
| GI / emulsion burden | see notes | 7.60 |
| Shelf / commercial readiness | see notes | 7.45 |

### Penalty / cap ledger

| Target | Delta / cap | Reason |
|---|---:|---|
| GI | -0.4 | emulsion not validated |
| Shelf | -0.45 | 10% oil emulsion risk |
| Shelf | -0.8 | emulsion stability not validated |
| Shelf | -0.8 | preservative challenge not validated |
| Shelf | 0.8 | dry activator removes wet incompatibilities |
| Shelf | -0.3 | oil-phase active distribution assay needed |

### Physical gate notes
- GI: emulsion not validated
- Shelf: 6+ month target active
- Shelf: 10% oil emulsion needs separation/oxidation testing
- Shelf: emulsion stability not validated
- Shelf: preservative challenge not validated
- Shelf: dry activator removes high-risk wet amines/vitamins
- Shelf: oil-phase actives need potency/distribution assay
- Osmolality: 161 mOsm/L -> PASS: <= 320 mOsm/L — within isotonic-ish hydration band
- Solubility: no bottlenecks; TDS 12.19% w/v

### Metric confidence

| Metric | Final score | Biological potential | Confidence | Notes |
|---|---:|---:|---|---|
| Focus / alertness | 5.48 | 5.48 | Low |  |
| Energy availability | 6.16 | 6.16 | Medium |  |
| Fatigue/stress tolerance | 8.44 | 8.44 | High |  |
| Fast recovery | 8.40 | 8.40 | Medium |  |
| ATP regeneration | 8.12 | 8.12 | Medium |  |
| Anti-inflammatory / antioxidant support | 8.68 | 8.68 | High |  |
| Respiratory / acid-base support | 6.67 | 6.67 | Medium |  |
| Hydration / electrolyte balance | 6.89 | 6.89 | Medium |  |
| GI tolerance | 7.60 | 8.00 | Low | emulsion not validated |
| Onset speed | 5.92 | 5.92 | Medium |  |
| Shelf stability / commercial readiness | 7.45 | 9.00 | Medium | 6+ month target active; 10% oil emulsion needs separation/oxidation testing; emulsion stability not validated; preservative challenge not validated; dry activator removes high-risk wet amines/vitamins; oil-phase actives need potency/distribution assay |

### Ingredient contribution rows

| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |
|---|---:|---|---|---:|---:|---|---|
| MCT oil | 0.5 mL | oil | field | 0.71 | 1.00 | energy:1.683, fatigue:0.421, onset:0.481 | Oil energy; score capped by emulsion/GI tolerance. |
| D-ribose | 250 mg | wet | field | 0.91 | 1.00 | atp:1.552, energy:1.009, onset:0.621, recovery:1.397 | Field-supported ATP/recovery lever; wet Maillard driver. |
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

## V3.3 Dry Make-Fresh Recovery Drink + Oil Micelle/Softgel — calculation notes

- Architecture: `dry_make_fresh_plus_oil_cap`
- Final deliverable overall: **7.01/10**
- Biological potential: **6.72/10**
- Formulation feasibility: **8.93/10**
- Raw contribution points: `{"antiox": 5.949, "atp": 5.007, "energy": 1.189, "fatigue": 4.926, "focus": 2.385, "gi": 0.215, "hydration": 3.379, "onset": 2.206, "recovery": 5.338, "resp": 3.258}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | n/a | 10.00 |
| Osmolality / ORS | 116 mOsm/L → PASS | hydration cap 10.00 |
| GI / emulsion burden | see notes | 8.00 |
| Shelf / commercial readiness | see notes | 8.70 |

### Penalty / cap ledger

| Target | Delta / cap | Reason |
|---|---:|---|
| Shelf | -0.3 | oil-phase active distribution assay needed |

### Physical gate notes
- Shelf: 6+ month target active
- Shelf: oil-phase actives need potency/distribution assay
- Osmolality: 116 mOsm/L -> PASS: <= 320 mOsm/L — within isotonic-ish hydration band
- Osmolality: UNKNOWN osmoles for: taurine (molar mass missing in registry; osmolarity is under-estimated)

### Metric confidence

| Metric | Final score | Biological potential | Confidence | Notes |
|---|---:|---:|---|---|
| Focus / alertness | 5.48 | 5.48 | Low |  |
| Energy availability | 3.27 | 3.27 | Medium |  |
| Fatigue/stress tolerance | 8.06 | 8.06 | High |  |
| Fast recovery | 8.31 | 8.31 | Medium |  |
| ATP regeneration | 8.12 | 8.12 | Medium |  |
| Anti-inflammatory / antioxidant support | 8.62 | 8.62 | High |  |
| Respiratory / acid-base support | 6.62 | 6.62 | Medium |  |
| Hydration / electrolyte balance | 6.76 | 6.76 | Medium |  |
| GI tolerance | 8.00 | 8.00 | Medium |  |
| Onset speed | 5.21 | 5.21 | Medium |  |
| Shelf stability / commercial readiness | 8.70 | 9.00 | Medium | 6+ month target active; oil-phase actives need potency/distribution assay |

### Ingredient contribution rows

| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |
|---|---:|---|---|---:|---:|---|---|
| MCT oil | 0 mL | oil | field | 0.00 | 1.00 | energy:0.0, fatigue:0.0, onset:0.0 | Oil energy; score capped by emulsion/GI tolerance. |
| D-ribose | 250 mg | make_fresh | field | 0.91 | 1.00 | atp:1.552, energy:1.009, onset:0.621, recovery:1.397 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 100 mg | make_fresh | avian_indirect | 1.00 | 1.00 | antiox:0.48, fatigue:1.12, recovery:0.64, resp:1.2 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| LCLT | 50 mg | make_fresh | avian_indirect | 1.00 | 1.00 | atp:0.18, energy:0.18, fatigue:0.288, recovery:0.36, resp:0.288 | More preload/chronic than acute. |
| CoQ10 | 5 mg | dry | avian | 1.00 | 1.00 | antiox:1.8, atp:1.0, fatigue:0.6 | Chicken heat-stress mitochondrial ROS support; not acute stimulant proof. |
| Vitamin E acetate | 10 mg | dry | avian | 1.00 | 1.00 | antiox:1.6, fatigue:0.4 | Stable vitamin E source; not counted as strong in-bottle oil preservative. |
| MgCl2 | 40 mg | make_fresh | avian_indirect | 1.00 | 1.00 | atp:0.64, hydration:0.48, recovery:0.4, resp:0.24 | Mg-ATP/electrolyte support; GI cap applies. |
| NaCl | 25 mg | make_fresh | avian_indirect | 1.00 | 1.00 | hydration:0.96, onset:0.24, resp:0.48 | Cl-balanced hydration/acid-base support. |
| KCl | 10 mg | make_fresh | avian_indirect | 1.00 | 1.00 | hydration:0.72, resp:0.4 | K/Cl electrolyte support. |
| Sodium citrate | 12.5 mg | make_fresh | avian_indirect | 0.91 | 1.00 | hydration:0.146, resp:0.292 | Small buffer; penalize if over-used as alkali load. |
| L-tyrosine | 200 mg | dry | mechanism | 1.00 | 1.00 | focus:1.56, onset:0.91 | Dry-only focus lever; low water solubility. |
| B6/P5P | 2.5 mg | dry | mechanism | 1.00 | 1.00 | atp:0.195, focus:0.585, onset:0.195 | Cofactor; keep dry/light-protected. |
| Vitamin C | 75 mg | make_fresh | avian_indirect | 1.00 | 1.00 | antiox:0.96, focus:0.24, onset:0.24, recovery:0.56 | Useful make-fresh; wet storage loses potency. |
| Taurine | 100 mg | make_fresh | avian_indirect | 0.89 | 1.00 | antiox:0.572, fatigue:0.716, gi:0.215, recovery:0.716, resp:0.358 | Dry/make-fresh preferred with ribose. |
| Betaine | 200 mg | make_fresh | avian | 0.89 | 1.00 | antiox:0.537, fatigue:1.163, hydration:1.073, recovery:0.626 | Osmolyte/methyl donor; strong heat-stress support. |
| Creatine/GAA preload equivalent | 200 mg | dry | avian_indirect | 1.00 | 1.00 | atp:1.44, fatigue:0.64, recovery:0.64 | ATP/PCr score mainly if preloaded; wet degradation risk. |
