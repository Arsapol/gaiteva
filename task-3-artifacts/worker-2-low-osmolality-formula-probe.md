---
title: "Worker-2 Evidence Probe — Low-Osmolality V3/V4 Formula Candidates"
tags: ["gamefowl", "formula-v4", "stats-card-v0.2", "hydration", "osmolality", "worker-2"]
created: 2026-06-17 Asia/Bangkok
category: research
confidence: medium
---

# Worker-2 Evidence Probe — Low-Osmolality V3/V4 Formula Candidates

## Bottom line

The quickest score gain over V3 is not a new stimulant/recovery claim; it is fixing the hydration gate. V3 scored **6.96/10** because the calculator treated the 5 mL dose as direct-dose and capped hydration at **2.50** from **1309 mOsm/L**. Declaring and enforcing a make-fresh dilution volume removes that cap while preserving the shelf-stable wet-core + dry-activator architecture.

**Best candidate from this worker slice: V4 Make-Fresh SGLT1 ORS Hybrid**
- Calculated final deliverable: **7.51/10** vs V3 **6.96/10**.
- Biological potential: **7.55/10**.
- Formulation feasibility: **8.43/10**.
- Hydration/electrolyte metric: **8.29/10**.
- Osmolality gate: **94 mOsm/L PASS** when mixed into **50 mL** water.
- Score gain source: mostly hydration/osmolality feasibility, plus a small true hydration improvement from make-fresh dextrose.

## Candidate A — V3.1 protocol-only dilution update

**Change:** keep V3 ingredients unchanged, but label/administer as: **mix the 5 mL core dose into 50 mL clean water before use**. Dry activator remains dry/make-fresh.

Calculator result (`task-3-artifacts/v31-calculated-card.md`):

| Formula | Biological potential | Formulation feasibility | Final deliverable | Hydration | Osmolality gate |
|---|---:|---:|---:|---:|---|
| V3 direct-dose benchmark | 7.36 | 6.80 | 6.96 | 2.50 | 1309 mOsm/L BLOCK |
| V3.1 diluted 50 mL | 7.36 | 8.43 | **7.36** | 6.89 | 92 mOsm/L PASS |

**Use when:** easiest path; no new ingredient/sourcing change; merely converts V3 from direct hypertonic bolus to defined make-fresh drink.

## Candidate B — V4 Make-Fresh SGLT1 ORS Hybrid (recommended prototype)

**Use protocol:** at event use, mix **5 mL core + dry/make-fresh stick into 50 mL water**. Do not market as pain tolerance; claim hydration/recovery/fatigue-stress support only.

### Per event dose

**Bottle A — wet/oil core (stored; 5 mL dose):**

| Ingredient | Dose | Reason |
|---|---:|---|
| MCT oil | 1.0 mL | acute energy; already in V3; oil burden capped |
| D-ribose | 150 mg | retained field-supported recovery sugar, reduced to lower TDS/osmotic liability |
| DMG | 100 mg | avian heat/oxidative/respiratory support lane |
| L-carnitine L-tartrate | 50 mg | chronic/cardiometabolic support, modest acute credit |
| CoQ10 | 5 mg | chicken heat-stress mitochondrial ROS support; oil phase |
| Vitamin E acetate | 10 mg | avian antioxidant support; stable oil-compatible vitamin E source |
| MgCl2 | 40 mg | Mg/Cl trace support; keep elemental Mg modest |
| NaCl | 25 mg | sodium + chloride; SGLT1 partner / DEB neutral |
| KCl | 10 mg | potassium + chloride; avoids citrate alkalosis drift |
| Sodium citrate | 12.5 mg | small buffer only; avoid heavy alkalinization |

**Stick B — dry/make-fresh activator (added to 50 mL water at use):**

| Ingredient | Dose | Reason |
|---|---:|---|
| Dextrose (D-glucose) | 200 mg | SGLT1 hydration carrier; make-fresh to avoid stored sugar/amine chemistry |
| L-tyrosine | 200 mg | focus/alertness lever; dry-only due solubility/storage |
| B6/P5P equivalent | 2.5 mg | cofactor; keep total session B6 <15 mg |
| Vitamin C / ascorbate | 75 mg | make-fresh antioxidant/cofactor; do not store wet with metals/sugars |
| Taurine | 125 mg | conditional stress/osmolyte support; dry avoids stored ribose/amine issue |
| Betaine anhydrous | 250 mg | poultry-supported osmolyte/methyl donor |
| Creatine or GAA preload equivalent | 200 mg | PCr/ATP support if preloaded; dry only |

Calculator result (`task-3-artifacts/v4-ors-card.md`):

| Formula | Biological potential | Formulation feasibility | Final deliverable | Hydration | Osmolality gate |
|---|---:|---:|---:|---:|---|
| V3 direct-dose benchmark | 7.36 | 6.80 | 6.96 | 2.50 | 1309 mOsm/L BLOCK |
| V4 make-fresh ORS hybrid | **7.55** | **8.43** | **7.51** | **8.29** | 94 mOsm/L PASS |

Notes:
- The dextrose profile is an external calculator profile built from the existing reviewed wiki dossier (`substance-dextrose-d-glucose.md`), not a silent script edit.
- MgCl2 molar mass is missing in the current osmolality compatibility table, so osmolality is under-estimated; at 50 mL there is still large headroom below 320 mOsm/L, but this should be fixed before final publication.

## Candidate C — lower-oil fallback

If GI/oil tolerance is the field bottleneck, reduce MCT from 1.0 mL to 0.75 mL and target 15% oil in the core. Calculator: **7.35/10**, slightly lower than V3.1/V4 but may be better tolerated in individual birds.

## Formula-safety gate (research pass)

| Substance/change | R1 Solubility | R2 Stability | R3 Compatibility | Verdict |
|---|---|---|---|---|
| Defined 50 mL delivered water | N/A | make-fresh; no shelf burden | fixes hypertonic direct-dose gate | ✅ GO |
| Dextrose 200 mg make-fresh | Wiki dossier: very soluble; intended drink concentration ~4 g/L, far below solubility | stable enough make-fresh; reducing sugar should not be stored wet with amines/vitamins | pair with Na for SGLT1; keep separate from stored amino/vitamin matrix | ✅ ADD-strong, make-fresh only |
| D-ribose reduced 300→150 mg | freely soluble; lower TDS than V3 | reducing sugar; less storage burden at lower dose but still keep away from amino acids | field-supported but mechanism-confounded; not SGLT1 hydration carrier | ⚠️ KEEP-conditional |
| NaCl/KCl/MgCl2 chloride salts | high solubility per existing dossiers | stable | Cl-balanced; avoid citrate-only alkalosis; Mg phosphate/carbonate precipitation not present here | ✅ OK |
| Sodium citrate low dose | soluble/stable | stable | keep low to avoid alkalosis overshoot in panting bird | ✅ OK low-dose |
| Dry tyrosine/B6/ascorbate/taurine/betaine/creatine-GAA | dry forms avoid wet solubility and degradation bottlenecks | dry/make-fresh; do not store all-in-one wet | avoid ribose/dextrose + amino/vitamin wet storage; keep B6 total <15 mg/session, Mg <150 mg/session | ✅/⚠️ OK with dry split |
| CoQ10/vitamin E acetate oil phase | water-insoluble; oil-phase only | light/O2/assay risks remain | emulsion distribution/potency must be tested | ⚠️ conditional |

## GO / NO-GO

**GO-CONDITIONAL** for V4 as a prototype candidate to hand to the leader: it beats V3 in the v0.2 calculator (**7.51 vs 6.96**) by fixing the osmolality/hydration cap and adding a make-fresh SGLT1 glucose carrier.

**GO-CONDITIONAL** for V3.1 protocol-only dilution if the team wants the lowest-risk update with no new formula profile (**7.36 vs 6.96**).

**NO-GO** for direct-dose hydration claims on the original V3 5 mL bolus.

**NO-GO** for a pure wet all-in-one bottle that stores dextrose/ribose with amino acids, B vitamins, ascorbate, and trace metals for 6–12 months.

## Blocking gaps before final/wiki decision

1. Fix calculator osmolality data for MgCl2 so the 94 mOsm/L estimate is not undercounted.
2. Run independent verifier on the new dextrose external profile and V4 dose math.
3. Finished-product stability still needs pH drift, preservative challenge, emulsion phase separation, peroxide/anisidine/rancidity, viscosity/syringeability, color/browning, and potency assays for CoQ10/vitamin E.
4. Field palatability/drinking compliance must be checked; a perfect osmolality drink fails if birds refuse it.
5. 6-month shelf life is plausible only after validation; 12-month shelf life remains unconfirmed.

## Evidence anchors used

- Ground truth: `.omx/context/higher-score-formula-after-stats-upgrade-20260617T000000Z.md`.
- Benchmark card: `omx_wiki/calculated-stats-card-route-a-vs-v3-hybrid.md`.
- V3 decision: `omx_wiki/gamefowl-formula-v3-high-score-hybrid-core-emulsion-dry-activato.md`.
- Avian frame: `omx_wiki/gamefowl-supplement-formula-avian-grounded-evaluation.md`.
- Dextrose dossier: Shibata 2023 PMID 37321034; Zhou 1998 PMID 9603349; reviewed in `omx_wiki/substance-dextrose-d-glucose.md`.
- Betaine dossier: Sayed & Downing 2011 PMID 21177455; reviewed in `omx_wiki/substance-betaine-anhydrous.md`.
- CoQ10: Kikusato et al. 2016 PMID 26707541 / DOI 10.1111/asj.12543.
- Electrolyte dossiers: `substance-sodium-chloride-nacl.md`, `substance-potassium-chloride-kcl.md`, `substance-magnesium-chloride-mgcl2.md`.

## Verification

- PASS: `python calculated_stats_card.py --preset v3_hybrid --json-in v31-low-osm-hybrid.json` produced V3.1 **7.36/10** and osmolality **92 mOsm/L PASS**.
- PASS: `python calculated_stats_card.py --preset v3_hybrid --json-in v4-ors-hybrid.json --profiles dextrose-profile.json` produced V4 **7.51/10** and osmolality **94 mOsm/L PASS**.
- PASS: variants run showed no-ribose diluted hybrid **6.93/10** (does not beat V3), lower-ribose **7.25/10**, and low-oil **7.35/10**.
