# Calculated Formula Stats Card

> v0.2 calculation: deterministic expert-scoring from ingredient dose profiles + evidence multipliers + physical-chemistry gates. Scores are comparable estimates, not proof of efficacy.

## Model layers

- **Biological potential**: what the active profile could do before delivery/stability caps.
- **Formulation feasibility**: solubility + osmolality + GI/emulsion + shelf-readiness gate score.
- **Final deliverable score**: the score after physical caps/penalties.

## Score comparison

| Metric | V3 Hybrid Core Emulsion + Dry Activator | V3.1 Diluted Hybrid Core (5 mL core into 60 mL water; dry activator separate) | V4 Split Core + Make-Fresh Low-Osm ORS Stick (60 mL) |
|---|---:|---:|---:|
| Focus / alertness | 5.48 | 5.48 | 5.48 |
| Energy availability | 7.05 | 7.05 | 7.74 |
| Fatigue/stress tolerance | 8.53 | 8.53 | 8.53 |
| Fast recovery | 8.47 | 8.47 | 8.62 |
| ATP regeneration | 8.21 | 8.21 | 8.21 |
| Anti-inflammatory / antioxidant support | 8.68 | 8.68 | 8.68 |
| Respiratory / acid-base support | 6.67 | 6.67 | 8.06 |
| Hydration / electrolyte balance | 2.50 | 6.89 | 9.20 |
| GI tolerance | 7.25 | 7.25 | 7.25 |
| Onset speed | 6.25 | 6.25 | 7.06 |
| Shelf stability / commercial readiness | 7.45 | 7.45 | 6.65 |
| **Overall average** | **6.96** | **7.36** | **7.77** |

## Layer comparison

| Formula | Biological potential | Formulation feasibility | Final deliverable average |
|---|---:|---:|---:|
| V3 Hybrid Core Emulsion + Dry Activator | 7.36 | 6.80 | 6.96 |
| V3.1 Diluted Hybrid Core (5 mL core into 60 mL water; dry activator separate) | 7.36 | 8.43 | 7.36 |
| V4 Split Core + Make-Fresh Low-Osm ORS Stick (60 mL) | 7.95 | 8.22 | 7.77 |

## Rollups

| Formula | Performance support | Recovery/welfare | Commercial readiness |
|---|---:|---:|---:|
| V3 Hybrid Core Emulsion + Dry Activator | 7.38 | 6.71 | 7.45 |
| V3.1 Diluted Hybrid Core (5 mL core into 60 mL water; dry activator separate) | 7.38 | 7.59 | 7.45 |
| V4 Split Core + Make-Fresh Low-Osm ORS Stick (60 mL) | 7.59 | 8.36 | 6.65 |

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
| Osmolality / ORS | 1309 mOsm/L → BLOCK | hydration cap 2.50 |
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
| Hydration cap | cap 2.5 | 1309 mOsm/L -> BLOCK: > 350 mOsm/L — HYPERTONIC. Pulls water into gut lumen, worsens dehydration. Must dilute / cut dose before use as hydration aid. |
| Hydration cap | cap 2.5 | UNKNOWN osmoles for: magnesium_chloride (molar mass missing in compat.data; osmolarity is under-estimated) |

### Physical gate notes
- GI: moderate oil emulsion burden
- GI: emulsion not validated
- Shelf: 6+ month target active
- Shelf: 20% oil emulsion needs separation/oxidation testing
- Shelf: emulsion stability not validated
- Shelf: preservative challenge not validated
- Shelf: dry activator removes high-risk wet amines/vitamins
- Shelf: oil-phase actives need potency/distribution assay
- Osmolality: 1309 mOsm/L -> BLOCK: > 350 mOsm/L — HYPERTONIC. Pulls water into gut lumen, worsens dehydration. Must dilute / cut dose before use as hydration aid.
- Osmolality: UNKNOWN osmoles for: magnesium_chloride (molar mass missing in compat.data; osmolarity is under-estimated)
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
| D-ribose | 300 mg | wet | field | 1.00 | 1.00 | energy:1.105, recovery:1.53, atp:1.7, onset:0.68 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 100 mg | wet | avian_indirect | 1.00 | 1.00 | fatigue:1.12, recovery:0.64, antiox:0.48, resp:1.2 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| LCLT | 50 mg | wet | avian_indirect | 1.00 | 1.00 | energy:0.18, fatigue:0.288, recovery:0.36, atp:0.18, resp:0.288 | More preload/chronic than acute. |
| CoQ10 | 5 mg | oil | avian | 1.00 | 1.00 | fatigue:0.6, atp:1.0, antiox:1.8 | Chicken heat-stress mitochondrial ROS support; not acute stimulant proof. |
| Vitamin E acetate | 10 mg | oil | avian | 1.00 | 1.00 | fatigue:0.4, antiox:1.6 | Stable vitamin E source; not counted as strong in-bottle oil preservative. |
| MgCl2 | 40 mg | wet | avian_indirect | 1.00 | 1.00 | recovery:0.4, atp:0.64, resp:0.24, hydration:0.48 | Mg-ATP/electrolyte support; GI cap applies. |
| NaCl | 25 mg | wet | avian_indirect | 1.00 | 1.00 | resp:0.48, hydration:0.96, onset:0.24 | Cl-balanced hydration/acid-base support. |
| KCl | 10 mg | wet | avian_indirect | 1.00 | 1.00 | resp:0.4, hydration:0.72 | K/Cl electrolyte support. |
| Sodium citrate | 12.5 mg | wet | avian_indirect | 0.91 | 1.00 | resp:0.292, hydration:0.146 | Small buffer; penalize if over-used as alkali load. |
| L-tyrosine | 200 mg | dry | mechanism | 1.00 | 1.00 | focus:1.56, onset:0.91 | Dry-only focus lever; low water solubility. |
| B6/P5P | 2.5 mg | dry | mechanism | 1.00 | 1.00 | focus:0.585, atp:0.195, onset:0.195 | Cofactor; keep dry/light-protected. |
| Vitamin C | 75 mg | dry | avian_indirect | 1.00 | 1.00 | focus:0.24, recovery:0.56, antiox:0.96, onset:0.24 | Useful make-fresh; wet storage loses potency. |
| Taurine | 125 mg | dry | avian_indirect | 1.00 | 1.00 | fatigue:0.8, recovery:0.8, antiox:0.64, resp:0.4, gi:0.24 | Dry/make-fresh preferred with ribose. |
| Betaine | 250 mg | dry | avian | 1.00 | 1.00 | fatigue:1.3, recovery:0.7, antiox:0.6, hydration:1.2 | Osmolyte/methyl donor; strong heat-stress support. |
| Creatine/GAA preload equivalent | 200 mg | dry | avian_indirect | 1.00 | 1.00 | fatigue:0.64, recovery:0.64, atp:1.44 | ATP/PCr score mainly if preloaded; wet degradation risk. |

## V3.1 Diluted Hybrid Core (5 mL core into 60 mL water; dry activator separate) — calculation notes

- Architecture: `wet_core_plus_dry_activator`
- Final deliverable overall: **7.36/10**
- Biological potential: **7.36/10**
- Formulation feasibility: **8.43/10**
- Raw contribution points: `{"antiox": 6.08, "atp": 5.155, "energy": 3.665, "fatigue": 5.743, "focus": 2.385, "gi": 0.24, "hydration": 3.506, "onset": 2.945, "recovery": 5.63, "resp": 3.3}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | PASS; TDS 15.36% w/v | 10.00 |
| Osmolality / ORS | 76 mOsm/L → PASS | hydration cap 10.00 |
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
- Osmolality: 76 mOsm/L -> PASS: <= 320 mOsm/L — within isotonic-ish hydration band
- Osmolality: UNKNOWN osmoles for: magnesium_chloride (molar mass missing in compat.data; osmolarity is under-estimated)
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
| D-ribose | 300 mg | wet | field | 1.00 | 1.00 | energy:1.105, recovery:1.53, atp:1.7, onset:0.68 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 100 mg | wet | avian_indirect | 1.00 | 1.00 | fatigue:1.12, recovery:0.64, antiox:0.48, resp:1.2 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| LCLT | 50 mg | wet | avian_indirect | 1.00 | 1.00 | energy:0.18, fatigue:0.288, recovery:0.36, atp:0.18, resp:0.288 | More preload/chronic than acute. |
| CoQ10 | 5 mg | oil | avian | 1.00 | 1.00 | fatigue:0.6, atp:1.0, antiox:1.8 | Chicken heat-stress mitochondrial ROS support; not acute stimulant proof. |
| Vitamin E acetate | 10 mg | oil | avian | 1.00 | 1.00 | fatigue:0.4, antiox:1.6 | Stable vitamin E source; not counted as strong in-bottle oil preservative. |
| MgCl2 | 40 mg | wet | avian_indirect | 1.00 | 1.00 | recovery:0.4, atp:0.64, resp:0.24, hydration:0.48 | Mg-ATP/electrolyte support; GI cap applies. |
| NaCl core | 25 mg | wet | avian_indirect | 1.00 | 1.00 | resp:0.48, hydration:0.96, onset:0.24 | Cl-balanced hydration/acid-base support. |
| KCl core | 10 mg | wet | avian_indirect | 1.00 | 1.00 | resp:0.4, hydration:0.72 | K/Cl electrolyte support. |
| Sodium citrate core | 12.5 mg | wet | avian_indirect | 0.91 | 1.00 | resp:0.292, hydration:0.146 | Small buffer; penalize if over-used as alkali load. |
| L-tyrosine dry cap | 200 mg | dry | mechanism | 1.00 | 1.00 | focus:1.56, onset:0.91 | Dry-only focus lever; low water solubility. |
| B6/P5P dry cap | 2.5 mg | dry | mechanism | 1.00 | 1.00 | focus:0.585, atp:0.195, onset:0.195 | Cofactor; keep dry/light-protected. |
| Vitamin C dry cap | 75 mg | dry | avian_indirect | 1.00 | 1.00 | focus:0.24, recovery:0.56, antiox:0.96, onset:0.24 | Useful make-fresh; wet storage loses potency. |
| Taurine dry cap | 125 mg | dry | avian_indirect | 1.00 | 1.00 | fatigue:0.8, recovery:0.8, antiox:0.64, resp:0.4, gi:0.24 | Dry/make-fresh preferred with ribose. |
| Betaine dry cap | 250 mg | dry | avian | 1.00 | 1.00 | fatigue:1.3, recovery:0.7, antiox:0.6, hydration:1.2 | Osmolyte/methyl donor; strong heat-stress support. |
| Creatine/GAA preload equivalent | 200 mg | dry | avian_indirect | 1.00 | 1.00 | fatigue:0.64, recovery:0.64, atp:1.44 | ATP/PCr score mainly if preloaded; wet degradation risk. |

## V4 Split Core + Make-Fresh Low-Osm ORS Stick (60 mL) — calculation notes

- Architecture: `wet_core_plus_dry_activator_make_fresh_ors`
- Final deliverable overall: **7.77/10**
- Biological potential: **7.95/10**
- Formulation feasibility: **8.22/10**
- Raw contribution points: `{"antiox": 6.08, "atp": 5.155, "energy": 4.465, "fatigue": 5.743, "focus": 2.385, "gi": 0.24, "hydration": 7.59, "onset": 3.669, "recovery": 5.95, "resp": 4.92}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | PASS; TDS 15.36% w/v | 10.00 |
| Osmolality / ORS | 266 mOsm/L → PASS | hydration cap 10.00 |
| GI / emulsion burden | see notes | 7.25 |
| Shelf / commercial readiness | see notes | 6.65 |

### Penalty / cap ledger

| Target | Delta / cap | Reason |
|---|---:|---|
| GI | -0.35 | moderate oil emulsion burden |
| GI | -0.4 | emulsion not validated |
| Shelf | -0.45 | 20% oil emulsion risk |
| Shelf | -0.8 | emulsion stability not validated |
| Shelf | -0.8 | preservative challenge not validated |
| Shelf | -0.3 | oil-phase active distribution assay needed |

### Physical gate notes
- GI: moderate oil emulsion burden
- GI: emulsion not validated
- Shelf: 6+ month target active
- Shelf: 20% oil emulsion needs separation/oxidation testing
- Shelf: emulsion stability not validated
- Shelf: preservative challenge not validated
- Shelf: oil-phase actives need potency/distribution assay
- Osmolality: 266 mOsm/L -> PASS: <= 320 mOsm/L — within isotonic-ish hydration band
- Osmolality: UNKNOWN osmoles for: magnesium_chloride (molar mass missing in compat.data; osmolarity is under-estimated)
- Solubility: no bottlenecks; TDS 15.36% w/v

### Metric confidence

| Metric | Final score | Biological potential | Confidence | Notes |
|---|---:|---:|---|---|
| Focus / alertness | 5.48 | 5.48 | Low |  |
| Energy availability | 7.74 | 7.74 | Medium |  |
| Fatigue/stress tolerance | 8.53 | 8.53 | High |  |
| Fast recovery | 8.62 | 8.62 | Medium |  |
| ATP regeneration | 8.21 | 8.21 | Medium |  |
| Anti-inflammatory / antioxidant support | 8.68 | 8.68 | High |  |
| Respiratory / acid-base support | 8.06 | 8.06 | Medium |  |
| Hydration / electrolyte balance | 9.20 | 9.20 | Medium |  |
| GI tolerance | 7.25 | 8.00 | Low | moderate oil emulsion burden; emulsion not validated |
| Onset speed | 7.06 | 7.06 | Medium |  |
| Shelf stability / commercial readiness | 6.65 | 9.00 | Low | 6+ month target active; 20% oil emulsion needs separation/oxidation testing; emulsion stability not validated; preservative challenge not validated; oil-phase actives need potency/distribution assay |

### Ingredient contribution rows

| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |
|---|---:|---|---|---:|---:|---|---|
| MCT oil | 1 mL | oil | field | 1.00 | 1.00 | energy:2.38, fatigue:0.595, onset:0.68 | Oil energy; score capped by emulsion/GI tolerance. |
| D-ribose | 300 mg | wet | field | 1.00 | 1.00 | energy:1.105, recovery:1.53, atp:1.7, onset:0.68 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 100 mg | wet | avian_indirect | 1.00 | 1.00 | fatigue:1.12, recovery:0.64, antiox:0.48, resp:1.2 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| LCLT | 50 mg | wet | avian_indirect | 1.00 | 1.00 | energy:0.18, fatigue:0.288, recovery:0.36, atp:0.18, resp:0.288 | More preload/chronic than acute. |
| CoQ10 | 5 mg | oil | avian | 1.00 | 1.00 | fatigue:0.6, atp:1.0, antiox:1.8 | Chicken heat-stress mitochondrial ROS support; not acute stimulant proof. |
| Vitamin E acetate | 10 mg | oil | avian | 1.00 | 1.00 | fatigue:0.4, antiox:1.6 | Stable vitamin E source; not counted as strong in-bottle oil preservative. |
| MgCl2 | 40 mg | wet | avian_indirect | 1.00 | 1.00 | recovery:0.4, atp:0.64, resp:0.24, hydration:0.48 | Mg-ATP/electrolyte support; GI cap applies. |
| NaCl core | 25 mg | wet | avian_indirect | 1.00 | 1.00 | resp:0.48, hydration:0.96, onset:0.24 | Cl-balanced hydration/acid-base support. |
| KCl core | 10 mg | wet | avian_indirect | 1.00 | 1.00 | resp:0.4, hydration:0.72 | K/Cl electrolyte support. |
| Sodium citrate core | 12.5 mg | wet | avian_indirect | 0.91 | 1.00 | resp:0.292, hydration:0.146 | Small buffer; penalize if over-used as alkali load. |
| L-tyrosine dry cap | 200 mg | dry | mechanism | 1.00 | 1.00 | focus:1.56, onset:0.91 | Dry-only focus lever; low water solubility. |
| B6/P5P dry cap | 2.5 mg | dry | mechanism | 1.00 | 1.00 | focus:0.585, atp:0.195, onset:0.195 | Cofactor; keep dry/light-protected. |
| Vitamin C dry cap | 75 mg | dry | avian_indirect | 1.00 | 1.00 | focus:0.24, recovery:0.56, antiox:0.96, onset:0.24 | Useful make-fresh; wet storage loses potency. |
| Taurine dry cap | 125 mg | dry | avian_indirect | 1.00 | 1.00 | fatigue:0.8, recovery:0.8, antiox:0.64, resp:0.4, gi:0.24 | Dry/make-fresh preferred with ribose. |
| Betaine dry cap | 250 mg | dry | avian | 1.00 | 1.00 | fatigue:1.3, recovery:0.7, antiox:0.6, hydration:1.2 | Osmolyte/methyl donor; strong heat-stress support. |
| Creatine/GAA preload equivalent | 200 mg | dry | avian_indirect | 1.00 | 1.00 | fatigue:0.64, recovery:0.64, atp:1.44 | ATP/PCr score mainly if preloaded; wet degradation risk. |
| Dextrose monohydrate ORS stick | 1200 mg | make_fresh | avian_indirect | 1.00 | 1.00 | energy:0.8, hydration:1.6, onset:0.4, recovery:0.32 | Make-fresh glucose/SGLT1 substrate; keep out of 6-12 month wet bottle. Profile from existing dextrose/glucose dossiers; needs independent review before wiki-ingest. |
| NaCl ORS stick | 100 mg | make_fresh | avian_indirect | 1.35 | 1.00 | resp:0.648, hydration:1.296, onset:0.324 | Cl-balanced hydration/acid-base support. |
| KCl ORS stick | 35 mg | make_fresh | avian_indirect | 1.35 | 1.00 | resp:0.54, hydration:0.972 | K/Cl electrolyte support. |
| Sodium citrate ORS stick | 70 mg | make_fresh | avian_indirect | 1.35 | 1.00 | resp:0.432, hydration:0.216 | Small buffer; penalize if over-used as alkali load. |
