---
title: "Substance: Copper (trace, DBH cofactor)"
tags: ["copper", "substance-dossier", "gamefowl", "vnext2", "dbh-cofactor", "trace-mineral", "TBCC", "tribasic-copper-chloride"]
created: 2026-06-16T06:46:17.809Z
updated: 2026-06-16T06:46:17.809Z
sources: ["PMID 15971525", "DOI 10.1007/s12011-010-8623-3", "EFSA Journal 2355", "PMC7705045", "DOI 10.1038/s41598-021-86477-8", "PMID 36671529", "PMC8234185", "PMC8230424", "NRC 1994 Nutrient Requirements of Poultry", "PMC11282359", "ScienceDirect S0377840117303395"]
links: ["substance-l-tyrosine.md", "substance-ascorbic-acid-vitamin-c.md", "gamefowl-capsule-restructure-vnext2-function-split-tyrosine-forw.md"]
category: reference
confidence: high
schemaVersion: 1
---

# Substance: Copper (trace, DBH cofactor)

# Substance Dossier: Copper (trace, DBH cofactor)

## 1. Identity

| Field | Value |
|---|---|
| Common name | Copper |
| Recommended source form | Tribasic copper chloride (TBCC) = Cu₂(OH)₃Cl |
| Alternative acceptable form | Copper bis-glycinate chelate [Cu(Gly)₂] |
| Rejected forms | CuO (CuO; near-zero bioavailability); CuSO₄·5H₂O (pro-oxidant risk with co-formulated ascorbate) |
| Target elemental Cu dose | 0.1–0.3 mg elemental Cu per capsule |
| Role in this formula | Cofactor for dopamine-β-hydroxylase (DBH; EC 1.14.17.1), the cuproenzyme that converts dopamine → norepinephrine; also requires ascorbate as co-reductant |
| CAS – TBCC | 1332-65-6 |
| CAS – Cu bis-glycinate | 13479-54-4 |

---

## 2. Three-Rule Formula-Safety Check (R1–R3)

### Recommended form: TBCC [Cu₂(OH)₃Cl, ~58% Cu]

**R1 — Solubility / dissolution in gut (DRY capsule context)**
TBCC is sparingly water-soluble as a powder but dissolves readily in the acidic gastric environment (pH 1.5–2.5). Because the capsule is DRY, aqueous solubility during storage is irrelevant; gastric dissolution is the gate. TBCC dissolves in stomach acid to release Cu²⁺ ions available for intestinal absorption. This is not a limitation.
Verdict: PASS for dry capsule.

**R2 — Dry-mix / storage stability**
TBCC is specifically valued in premix science for low reactivity in the dry state. Studies in broiler starter crumbles show TBCC preserves vitamin A, D₃, E, and riboflavin significantly better than CuSO₄ after 10–21 days storage at room temperature (PMID 15971525; Springer 10.1007/s12011-010-8623-3). Mechanism: TBCC releases Cu²⁺ ions slowly from its crystal lattice compared to the highly soluble, immediately ionising CuSO₄·5H₂O; lower free Cu²⁺ activity in the dry matrix means less catalytic oxidation of co-formulated vitamins.
Verdict: PASS — superior to CuSO₄ for long-term dry storage.

**R3 — Compatibility: Cu + ascorbate + P5P in dry capsule**
- **In solution**: Cu²⁺ catalyses ascorbate oxidation via a Fenton-type redox cycle (Cu²⁺ + ascorbate → Cu⁺ + ascorbyl radical; Cu⁺ + O₂ → Cu²⁺ + O₂•⁻; cascade generates H₂O₂ and hydroxyl radical). This is a well-documented pro-oxidant risk in AQUEOUS or high-humidity environments (Nature Sci Rep DOI:10.1038/s41598-021-86477-8).
- **In DRY capsule**: Without bulk water, the catalytic cycle cannot proceed at meaningful rates. Vitamin destruction in dry premixes is driven by trace moisture and contact surface area — TBCC minimises both compared to CuSO₄ because: (a) its low water activity keeps the matrix drier, and (b) it releases fewer free Cu²⁺ ions in the absence of acid. The premix vitamin-stability literature confirms TBCC is the safest inorganic Cu source for ascorbate co-formulation.
- **P5P**: No known direct incompatibility with TBCC at micro-gram Cu doses. P5P is more stable than pyridoxine HCl; no catalytic oxidation risk at this Cu:P5P ratio has been documented.
- **Cu + NAC** (if ever added): NAC thiol groups do chelate Cu²⁺ and can form reactive Cu-thiolate complexes in solution — avoid co-formulating if NAC is added to the same capsule.
Verdict: R3 CONDITIONAL PASS — safe in dry capsule; do not expose to >60% RH long-term; seal capsules with desiccant.

---

## 3. Avian Evidence

### NRC Copper Requirements (NRC 1994, Nutrient Requirements of Poultry, 9th ed.)

| Parameter | Value |
|---|---|
| Broiler requirement | 8 mg Cu/kg complete feed |
| Turkey poult requirement | 8 mg Cu/kg |
| Maximum tolerable level (MTL), poultry | ~300 mg Cu/kg feed (NRC 1994); performance suppression begins at this level |
| Toxicity threshold | 300 mg/kg CuSO₄ reported to reduce feed efficiency and cause liver/kidney histopathology in broilers (PMC8234185, PMC8230424) |

### Dose safety math for this capsule

Assume a 2 kg gamefowl consuming ~120 g feed/day (6% BW):
- Feed Cu baseline (NRC requirement level): 8 mg/kg × 0.120 kg = 0.96 mg Cu/day from diet
- Capsule addition: 0.1–0.3 mg Cu/capsule (1–3 capsules/day scenario) = 0.1–0.9 mg Cu/day supplemental
- Total: ~1.1–1.9 mg Cu/day = ~9–16 mg Cu/kg feed equivalent
- MTL = 300 mg/kg. Capsule addition is **3–5% of MTL** — trivially safe, orders of magnitude below toxicity.

### Bioavailability ranking (poultry / broilers)

| Form | Relative bioavailability vs CuSO₄ | Evidence |
|---|---|---|
| TBCC [Cu₂(OH)₃Cl] | ~109% (95% CI 102–116%) | PMID 15971525 |
| Cu bis-glycinate/amino-acid chelate | ~88–147% (variable) | ScienceDirect S0377840104000823; PMC7009167 |
| CuSO₄·5H₂O | 100% (reference) | Standard |
| Copper gluconate | ~100% (estimated, limited avian data) | UNKNOWN — no direct avian RBA study found |
| CuO (cupric oxide) | ~0% (essentially inert in birds) | ScienceDirect S0377840117303395 |

---

## 4. Copper Source Comparison Table

| Form | %Cu | Avian bioavailability | Premix pro-oxidant risk | Dry stability | Notes |
|---|---|---|---|---|---|
| CuSO₄·5H₂O | 25.5% | 100% (ref) | HIGH — free Cu²⁺ degrades vitamins | Poor vs TBCC | Cheap, soluble, but worst for vitamin co-formulation |
| TBCC Cu₂(OH)₃Cl | ≥58% | ~109% (superior) | LOW — slow Cu²⁺ release in dry matrix | EXCELLENT | **Recommended for this use case** |
| Cu bis-glycinate [Cu(Gly)₂] | ~30% | 88–147% (variable) | LOW-MODERATE — chelate limits free Cu²⁺ | Good | Good alternative; higher cost; better human supplement precedent |
| Copper gluconate | 14–15% | ~100% (estimated) | MODERATE | Good | Low %Cu means higher filler mass; limited avian data |
| CuO (cupric oxide) | ~80% | ~0% (inert in birds) | VERY LOW | Excellent | Rejected — no bioavailability in poultry |

---

## 5. Verdict

**RECOMMENDED FORM: TBCC (tribasic copper chloride, Cu₂(OH)₃Cl)**

Rationale:
1. Highest confirmed avian bioavailability of any inorganic Cu form (~109% vs CuSO₄)
2. Lowest premix pro-oxidant activity — the only inorganic form with published data showing vitamin A, D₃, E, and riboflavin protection in broiler feed vs CuSO₄
3. High %Cu (≥58%) means the physical mass of Cu ingredient per capsule is tiny (0.17–0.52 mg TBCC to deliver 0.1–0.3 mg elemental Cu), minimising filler load
4. Established regulatory acceptance: EFSA-approved as a feed additive for all species (EFSA 2355)
5. Dry-capsule compatibility with ascorbate: the crystal structure limits free Cu²⁺ release in dry state; the Fenton-type Cu-ascorbate reaction requires aqueous phase

**SECOND CHOICE: Cu bis-glycinate** — appropriate if premium supplement-grade supply is preferred over feed-grade TBCC, or if regulatory context requires organic trace mineral.

**REJECTED**:
- CuSO₄·5H₂O: pro-oxidant in dry premix; will degrade the co-formulated ascorbate over shelf life
- CuO: negligible bioavailability in poultry (confirmed by multiple broiler studies)
- Copper gluconate: low %Cu (14–15%) increases capsule mass; limited avian bioavailability data

---

## 6. Dose Arithmetic

### TBCC to deliver target elemental Cu

```
%Cu in TBCC = 58.12%
To deliver 0.1 mg Cu → 0.1 / 0.5812 = 0.172 mg TBCC
To deliver 0.2 mg Cu → 0.2 / 0.5812 = 0.344 mg TBCC
To deliver 0.3 mg Cu → 0.3 / 0.5812 = 0.516 mg TBCC
```

These are sub-milligram masses — blend with excipient (maltodextrin or microcrystalline cellulose) for accurate dispensing.

### Cu bis-glycinate (backup)

```
%Cu in Cu(Gly)₂ = ~30%
To deliver 0.2 mg Cu → 0.2 / 0.30 = 0.667 mg chelate
```

---

## 7. Cautions

- **Moisture**: Seal capsules with silica gel desiccant packets. Even TBCC's vitamin-protective advantage erodes in high-humidity conditions; target storage <40% RH.
- **Cu + high-dose ascorbate in solution**: If the capsule dissolves in a high-dose vitamin C drink or water bolus, Fenton chemistry becomes possible. At 25–50 mg ascorbate and 0.1–0.3 mg Cu the risk is low but non-zero in aqueous media; this is acceptable for capsule-then-drink protocol, not for direct water-dissolved premix.
- **Cu:Zn antagonism**: High supplemental Cu competes with Zn absorption (shared intestinal transporter ZIP4/DMT1). At 0.1–0.3 mg/capsule this is physiologically negligible vs dietary Zn but worth noting if formula also adds Zn.
- **Cu + NAC**: If NAC is ever added to this capsule, Cu²⁺ can form Cu-thiolate complexes (pro-oxidant in solution); separate into different capsules.
- **Toxicity watchpoint**: NRC MTL is 300 mg Cu/kg feed; capsule contribution reaches at most ~16 mg Cu/kg feed equivalent at aggressive 3-capsule dosing — 19-fold safety margin.

---

## 8. Cross-links

- [[substance-l-tyrosine]] — L-Tyrosine is the upstream catecholamine precursor (Tyr → DOPA → Dopamine); Cu-DBH is the next enzymatic step converting Dopamine → Norepinephrine
- [[substance-ascorbic-acid-vitamin-c]] — Ascorbate is both a DBH co-reductant (regenerates enzyme-bound Cu) AND the co-formulated vitamin in this capsule; dry-state Cu-ascorbate compatibility is the key safety gate for copper source selection
- [[gamefowl-capsule-restructure-vnext2-function-split-tyrosine-forward]] — The vNext2 capsule restructure that prompted this copper source selection; contains DBH-pathway rationale and capsule architecture

---

## 9. Sources

| Citation | Type | Tier |
|---|---|---|
| PMID 15971525 — Aitken et al. (2005) Poultry Science: TBCC vs CuSO₄, broiler performance, vitamin E oxidation stability | Primary RCT | 1 |
| DOI 10.1007/s12011-010-8623-3 — Zhou et al. (2010) Biol Trace Elem Res: vitamin A/D₃/E/riboflavin stability TBCC vs CuSO₄, broiler starter | Primary study | 1 |
| EFSA Journal 2355 — EFSA FEEDAP Panel (2012): Safety/efficacy of TBCC for all species | Regulatory review | 1 |
| PMC7705045 — Copper hydroxychloride vs CuSO₄ broiler growth, bioavailability | Primary RCT | 1 |
| DOI 10.1038/s41598-021-86477-8 — Buettner et al. (2021) Sci Rep: Ascorbate oxidation kinetics by Cu and Fe | Mechanistic | 1 |
| PMID 36671529 — Combined Cu + vitamin C systemic oxidative stress, kidney injury | Primary study | 1 |
| PMC8234185 / PMC8230424 — Cu toxicity (300 mg/kg) in broilers, vitamins C/E mitigation | Primary studies | 1 |
| NRC (1994) Nutrient Requirements of Poultry, 9th revised edition — Cu requirement 8 mg/kg, MTL ~300 mg/kg | Authoritative reference | 1 |
| PMC11282359 — Cu glycinate RBA in beef steers (best available chelate RBA study, non-avian) | Primary study, indirect | 2 |
| ScienceDirect S0377840117303395 — CuO vs CuSO₄ in broilers; dicopper oxide bioavailability | Primary study | 1 |

---

## 10. Changelog

| Date | Change |
|---|---|
| 2026-06-16 | Initial dossier created. TBCC recommended over CuSO₄, Cu-chelate, gluconate, CuO. Safety math vs NRC MTL confirmed. Three-rule analysis for dry-capsule Cu+ascorbate co-formulation. |

