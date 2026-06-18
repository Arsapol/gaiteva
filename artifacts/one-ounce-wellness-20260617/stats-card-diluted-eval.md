# Calculated Formula Stats Card

> v0.2 calculation: deterministic expert-scoring from ingredient dose profiles + evidence multipliers + physical-chemistry gates. Scores are comparable estimates, not proof of efficacy.

## Model layers

- **Biological potential**: what the active profile could do before delivery/stability caps.
- **Formulation feasibility**: solubility + osmolality + GI/emulsion + shelf-readiness gate score.
- **Final deliverable score**: the score after physical caps/penalties.

## Score comparison

| Metric | 1 oz Recovery/Hydration Core — water-cup diluted evaluation (non-fight use) |
|---|---:|
| Focus / alertness | 0.00 |
| Energy availability | 3.27 |
| Fatigue/stress tolerance | 5.95 |
| Fast recovery | 6.88 |
| ATP regeneration | 5.46 |
| Anti-inflammatory / antioxidant support | 3.02 |
| Respiratory / acid-base support | 6.23 |
| Hydration / electrolyte balance | 6.91 |
| GI tolerance | 8.00 |
| Onset speed | 2.49 |
| Shelf stability / commercial readiness | 8.20 |
| **Overall average** | **5.13** |

## Layer comparison

| Formula | Biological potential | Formulation feasibility | Final deliverable average |
|---|---:|---:|---:|
| 1 oz Recovery/Hydration Core — water-cup diluted evaluation (non-fight use) | 4.47 | 8.80 | 5.13 |

## Rollups

| Formula | Performance support | Recovery/welfare | Commercial readiness |
|---|---:|---:|---:|
| 1 oz Recovery/Hydration Core — water-cup diluted evaluation (non-fight use) | 4.03 | 6.21 | 8.20 |

## 1 oz Recovery/Hydration Core — water-cup diluted evaluation (non-fight use) — calculation notes

- Architecture: `single_wet_bottle`
- Final deliverable overall: **5.13/10**
- Biological potential: **4.47/10**
- Formulation feasibility: **8.80/10**
- Raw contribution points: `{"antiox": 1.08, "atp": 2.372, "energy": 1.189, "fatigue": 2.708, "focus": 0.0, "hydration": 3.52, "onset": 0.861, "recovery": 3.497, "resp": 2.928}`

### Physical chemistry gate

| Gate | Result | Score / cap |
|---|---|---:|
| Solubility/TDS | PASS; TDS 17.21% w/v | 10.00 |
| Osmolality / ORS | 117 mOsm/L → PASS | hydration cap 10.00 |
| GI / emulsion burden | see notes | 8.00 |
| Shelf / commercial readiness | see notes | 8.20 |

### Penalty / cap ledger

| Target | Delta / cap | Reason |
|---|---:|---|
| Shelf | -0.8 | preservative challenge not validated |

### Physical gate notes
- Shelf: 6+ month target active
- Shelf: preservative challenge not validated
- Osmolality: 117 mOsm/L -> PASS: <= 320 mOsm/L — within isotonic-ish hydration band
- Solubility: no bottlenecks; TDS 17.21% w/v

### Metric confidence

| Metric | Final score | Biological potential | Confidence | Notes |
|---|---:|---:|---|---|
| Focus / alertness | 0.00 | 0.00 | Low |  |
| Energy availability | 3.27 | 3.27 | Medium |  |
| Fatigue/stress tolerance | 5.95 | 5.95 | High |  |
| Fast recovery | 6.88 | 6.88 | Medium |  |
| ATP regeneration | 5.46 | 5.46 | Medium |  |
| Anti-inflammatory / antioxidant support | 3.02 | 3.02 | High |  |
| Respiratory / acid-base support | 6.23 | 6.23 | Medium |  |
| Hydration / electrolyte balance | 6.91 | 6.91 | Medium |  |
| GI tolerance | 8.00 | 8.00 | Medium |  |
| Onset speed | 2.49 | 2.49 | Medium |  |
| Shelf stability / commercial readiness | 8.20 | 9.00 | Medium | 6+ month target active; preservative challenge not validated |

### Ingredient contribution rows

| Ingredient | Dose | Phase | Evidence | Dose factor | Solubility factor | Contributions | Notes |
|---|---:|---|---|---:|---:|---|---|
| D-ribose | 250 mg | wet | field | 0.91 | 1.00 | atp:1.552, energy:1.009, onset:0.621, recovery:1.397 | Field-supported ATP/recovery lever; wet Maillard driver. |
| DMG | 100 mg | wet | avian_indirect | 1.00 | 1.00 | antiox:0.48, fatigue:1.12, recovery:0.64, resp:1.2 | Formulation-friendly tertiary amine; avian heat/ascites lane. |
| Betaine anhydrous | 250 mg | wet | avian | 1.00 | 1.00 | antiox:0.6, fatigue:1.3, hydration:1.2, recovery:0.7 | Osmolyte/methyl donor; strong heat-stress support. |
| L-carnitine L-tartrate | 50 mg | wet | avian_indirect | 1.00 | 1.00 | atp:0.18, energy:0.18, fatigue:0.288, recovery:0.36, resp:0.288 | More preload/chronic than acute. |
| Magnesium chloride hexahydrate | 40 mg | wet | avian_indirect | 1.00 | 1.00 | atp:0.64, hydration:0.48, recovery:0.4, resp:0.24 | Mg-ATP/electrolyte support; GI cap applies. |
| Sodium chloride | 25 mg | wet | avian_indirect | 1.00 | 1.00 | hydration:0.96, onset:0.24, resp:0.48 | Cl-balanced hydration/acid-base support. |
| Potassium chloride | 10 mg | wet | avian_indirect | 1.00 | 1.00 | hydration:0.72, resp:0.4 | K/Cl electrolyte support. |
| Sodium citrate | 15 mg | wet | avian_indirect | 1.00 | 1.00 | hydration:0.16, resp:0.32 | Small buffer; penalize if over-used as alkali load. |
