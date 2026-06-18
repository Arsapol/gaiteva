# Gamefowl Formula Candidate V4 — Split Core + Make-Fresh Low-Osm ORS Stick

**Worker:** worker-4  
**Date:** 2026-06-17 Asia/Bangkok  
**Status:** candidate synthesis artifact only; worker-4 had no claimable task, so this is not committed/wiki-ingested.  
**Benchmark to beat:** V3 Hybrid final deliverable **6.96/10** after stats-card v0.2 upgrade.  
**Claim boundary:** welfare-positive hydration/recovery/fatigue-stress tolerance only. Do **not** claim pain tolerance.

## Decision summary

The cleanest way to beat V3 is not to cram more actives into the stored bottle. V3 already has strong biological potential (**7.36/10**) but loses final score because the 5 mL direct-dose liquid is hyperosmolar (**1309 mOsm/L → BLOCK**) and hydration is capped at **2.50/10**.

Two candidate updates clear the cap:

1. **V3.1 mandatory dilution:** keep V3 unchanged, but require mixing the 5 mL core into **60 mL water** before use. Calculator score rises to **7.36/10**.
2. **V4 split ORS:** keep the stable V3 core + separate dry activator, and add a **make-fresh 60 mL low-osm glucose/Na/K/citrate ORS stick**. Calculator score rises to **7.77/10** and hydration rises to **9.20/10**.

**Recommended candidate for leader integration:** **V4 split ORS**, because it gives a real SGLT1 glucose+Na hydration backbone rather than merely diluting the existing core.

## Stats-card v0.2 calculator result

Artifacts:
- `/private/tmp/worker4_v4_calc.md`
- `/private/tmp/worker4_v4_calc.json`
- Custom formula input: `/private/tmp/worker4_v4_candidates.json`
- External dextrose profile: `/private/tmp/worker4_dextrose_profile.json`

| Formula | Final deliverable | Biological potential | Formulation feasibility | Hydration | Recovery/welfare | Shelf/readiness |
|---|---:|---:|---:|---:|---:|---:|
| V3 benchmark | 6.96 | 7.36 | 6.80 | 2.50 | 6.71 | 7.45 |
| V3.1 diluted | 7.36 | 7.36 | 8.43 | 6.89 | 7.59 | 7.45 |
| **V4 split ORS** | **7.77** | **7.95** | **8.22** | **9.20** | **8.36** | **6.65** |

**Why V4 wins:** mostly formulation feasibility + hydration/osmolality, with a modest biological bump from dextrose/SGLT1 and stronger Na/K/Cl/citrate balance. Shelf/readiness is lower than V3.1 because a make-fresh stick adds handling/validation complexity, not because dry ORS is chemically unstable.

## Formula architecture

### A) Stored Core Emulsion — same V3 core, per 100 mL

| Ingredient | Amount / 100 mL | Per 5 mL event dose | Role |
|---|---:|---:|---|
| MCT oil | 20 mL | 1.0 mL | energy-dense oil phase |
| D-ribose | 6.0 g | 300 mg | field-supported ATP/recovery lever; no direct avian skeletal-muscle proof |
| DMG | 2.0 g | 100 mg | avian-indirect heat/oxidative/pulmonary-stress support |
| L-carnitine L-tartrate | 1.0 g | 50 mg | chronic/preload-leaning energy/cardiopulmonary support |
| CoQ10 | 100 mg | 5 mg | mitochondrial/oxidative-stress support; oil-phase active |
| Vitamin E acetate | 200 mg | 10 mg | stable vitamin E source; not counted as strong oil preservative |
| MgCl2 | 0.8 g nominal | 40 mg | Mg-ATP/electrolyte support; modest Mg |
| NaCl | 0.5 g | 25 mg | Na/Cl electrolyte support |
| KCl | 0.2 g | 10 mg | K/Cl electrolyte support |
| Sodium citrate dihydrate | 0.25 g | 12.5 mg | small buffer only; not alkali-loading |
| Acid/preservative/emulsifier/water | q.s. | q.s. | target pH/preservative/emulsion validation required |

### B) Make-fresh ORS Stick — per 60 mL event serving

Mix one stick into **60 mL cool water**, then add the 5 mL core dose. Use same day; discard leftovers.

| Ingredient | mg / 60 mL serving | % of dry stick |
|---|---:|---:|
| Dextrose monohydrate | 1200 mg | 85.41% |
| Sodium chloride | 100 mg | 7.12% |
| Potassium chloride | 35 mg | 2.49% |
| Sodium citrate dihydrate | 70 mg | 4.98% |
| **Total** | **1405 mg** | **100%** |

Approximate delivered electrolyte math in 60 mL after core + ORS:
- Glucose:Na molar ratio: **~2.03:1** (within existing wiki target ~1.8–2.1:1)
- Na: **~49.7 mM**
- K: **~10.1 mM**
- Cl: **~45.7 mM**
- Calculator osmolality: **266 mOsm/L → PASS**

### C) Dry activator / separate cap

Keep separate from the wet core and ORS until use to avoid stored glucose/ribose + amine/vitamin/redox incompatibilities.

| Ingredient | Per event dose | Role / caveat |
|---|---:|---|
| L-tyrosine | 200 mg | focus/catecholamine precursor; mechanism confidence only, dry only |
| B6/P5P | 2.5 mg | cofactor; keep session B6 total <15 mg |
| Vitamin C | 75 mg | antioxidant/cofactor; make-fresh/dry only |
| Taurine | 125 mg | osmolyte/cardiac/heat-stress support; dry only with sugars |
| Betaine anhydrous | 250 mg | avian-supported osmolyte/methyl support |
| Creatine/GAA equivalent | 200 mg | preload/chronic ATP-PCr support; do not over-credit as acute-only effect |

## Formula-safety gate

| Substance/change | R1 solubility | R2 stability | R3 compatibility | Verdict |
|---|---|---|---|---|
| Dextrose monohydrate ORS | Existing dossier: ~91 g/100 mL; intended 1.2 g/60 mL = 2 g/100 mL, large headroom | Dry stable. Reconstituted sugar drink must be same-day only. | Intended synergy with Na via SGLT1. Do not store with amines/B6/ascorbate. | ✅ ADD-strong make-fresh only |
| NaCl ORS + core | Existing dossier: ~360 g/L; huge headroom | Stable | Na for SGLT1; Cl balances DEB and avoids citrate-only alkalinization | ✅ OK |
| KCl ORS + core | Existing dossier: ~340 g/L; huge headroom | Stable | K/Cl electrolyte support | ✅ OK |
| Sodium citrate, small dose | Existing dossier: very soluble | Stable itself | Use as trace buffer only; avoid heavy alkali loading because exerted/panting birds may already have respiratory alkalosis component | ⚠️ ADD-conditional, small buffer only |
| Dry activator separation | n/a | Removes wet instability for tyrosine/B6/C/taurine/betaine | Prevents stored Maillard/redox conflicts with glucose/ribose | ✅ architecture fix |
| Stored core emulsion | Solubility/TDS PASS in calculator | 6 mo plausible only after validation; 12 mo unconfirmed | Oil-phase distribution, preservative challenge, emulsion stability still open | ⚠️ GO-CONDITIONAL |

## GO / NO-GO

**GO-CONDITIONAL for prototype V4 split ORS** because it beats V3 in the v0.2 calculator (**7.77 vs 6.96**) and fixes the load-bearing hydration cap (**266 mOsm/L PASS vs 1309 mOsm/L BLOCK**).

**GO for immediate low-risk label/process update V3.1**: declare `delivered_water_ml=60` / mandatory dilution; this alone scores **7.36**.

**NO-GO for production or wiki-final until:**
1. Independent peer review confirms the external dextrose profile used in the calculator.
2. `compat.data` gets MgCl2 molar mass/osmotic constants or the MgCl2 osmole gap is manually bounded.
3. Stored core passes pH drift, preservative challenge, droplet/phase separation, peroxide/rancidity, viscosity/syringeability, and CoQ10/vitamin E distribution/potency checks.
4. Field intake verifies the bird will actually drink/accept the 60 mL serving under stress.
5. No claims are framed as pain tolerance or injury masking.

## Sources reused from local wiki

- `omx_wiki/substance-dextrose-d-glucose.md` — SGLT1/glucose hydration dossier; PMID 37321034, PMID 9603349; solubility.
- `omx_wiki/substance-glucose-sucrose-drink-sugar-palatability.md` — chicken glucose/sucrose palatability and rejection window; PMID 35679679; make-fresh Maillard controls.
- `omx_wiki/substance-sodium-chloride-nacl.md`
- `omx_wiki/substance-potassium-chloride-kcl.md`
- `omx_wiki/substance-sodium-citrate-trisodium-citrate-dihydrate-alkalinizin.md`
- `omx_wiki/gamefowl-formula-v3-high-score-hybrid-core-emulsion-dry-activato.md`
- `omx_wiki/calculated-stats-card-route-a-vs-v3-hybrid.md`
