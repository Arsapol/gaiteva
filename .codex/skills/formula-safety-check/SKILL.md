---
name: formula-safety-check
description: Evidence-backed formulation-chemistry gate for liquid/oral supplements, especially gamefowl/avian formulas. Use when Codex is proposing, reviewing, adding, removing, swapping, or re-dosing an ingredient; changing concentration, dilution, salt form, pH, osmolality, preservative, or SKU architecture; recommending any substance for a solution/syrup/drink; or building/updating substance dossiers. Requires checking water solubility, in-solution stability/degradation, ingredient compatibility, avian/poultry evidence, cited sources, peer review, and wiki dossier updates before presenting GO/NO-GO.
---

> Migrated from `.claude/skills/formula-safety-check/SKILL.md` for Codex/OMX on 2026-06-16. Prefer `omx_wiki/` for persistent project knowledge.

# Formula Safety Check — 3-Rule Formulation Gate

A HARD GATE. Before any **new formula, new substance, ingredient swap, dose change, or dilution change** for a liquid/oral supplement is presented as a recommendation, run all 3 rules for EVERY affected substance and output the result table. Do not let a suggestion stand with any cell left blank — fill it with evidence or mark it `UNKNOWN — blocking gap`. Never silently assume soluble / stable / compatible.

## When this fires
- Proposing a new formula or new formula version
- Adding, removing, or substituting any ingredient
- Changing a dose, concentration, or dilution ratio
- Recommending any substance (even a casual "you could add X")
- Reviewing someone else's proposed formula change

## Procedure
1. **Reuse first** — `wiki_query({query:"<substance>", tags:["substance-dossier"]})`. If a dossier exists, reuse it; only research the gaps.
2. **Avian/animal context** — for animal formulas, read wiki page `gamefowl-supplement-formula-avian-grounded-evaluation` (DEB, Mg laxative limit, B6 avian ceiling, etc.).
3. **Research unknowns from RELIABLE sources** (see Source Standard below) per project routing rules (web search / official references available in Codex). EVERY claim must carry a citation — no uncited facts.
4. **Run the 3 rules** (below) for every affected substance + every new pair.
5. **Peer-review the research** — hand the findings + sources to a SECOND reviewer (e.g. native `critic`, `researcher`, `verifier`, or `$ask` external advisor) to verify correctness, source quality, and the Rule-3 conflict matrix BEFORE declaring GO. Authoring and review are separate passes; never self-approve research in the same lane.
6. **Write/update the Substance Dossier** (mandatory, see below) with cited sources.
7. **Output the table** + GO/NO-GO. Never present the formula suggestion without it.

## Source Standard (RELIABLE sources only)
Every fact in the dossier and the gate table MUST cite a source, ranked by reliability:
- **Tier 1 (prefer):** peer-reviewed journals (PubMed/PMID, DOI), NRC *Nutrient Requirements of Poultry* / *Vitamin Tolerance of Animals*, pharmacopeia/official solubility & stability monographs, government/veterinary references (Merck Vet Manual).
- **Tier 2 (acceptable, label as such):** review articles, textbooks, manufacturer technical data sheets for physicochemical constants.
- **Tier 3 (flag explicitly, do not rely on alone):** patents, forums, marketing, unsourced web pages, single anecdotes.
Record PMID/DOI/edition where possible. If only Tier 3 exists, mark the claim `LOW-CONFIDENCE` and treat as a blocking gap until corroborated. Never substitute model memory for a citation.

## Rule 1 — Water solubility (ละลายน้ำได้ดีไหม + อัตราส่วน)
- State **aqueous solubility** (mg/mL or g/100mL at ~25 °C; note temperature dependence).
- Compute **intended in-solution concentration** = substance mg ÷ solvent mL.
- **Headroom ratio** = solubility ÷ intended concentration:
  - ≥ 3 → ✅ SOLUBLE (safe margin)
  - 1–3 → ⚠️ TIGHT (may precipitate on cooling/storage)
  - < 1 → ❌ EXCEEDS / INSOLUBLE — will not dissolve; BLOCK
- Note **salt form** (citrate vs oxide vs chloride differ hugely) and any modifier the formula relies on (glycerin, pH, heat, co-solvent, chelator).

## Rule 2 — In-solution stability (ความเสื่อมสภาพในรูปสารละลาย)
- Identify degradation pathways in water: **hydrolysis, oxidation, photodegradation, thermal, pH-dependent breakdown, Maillard/browning, epimerization, microbial**.
- State the substance's **stable pH window** vs the formula's actual pH.
- State realistic **shelf-life in solution** + storage (refrigerate / amber bottle / inert headspace / make-fresh).
- Confirm the **preservative is effective at the formula pH AND after use-dilution** (K-sorbate / benzoate efficacy falls above pH ~6).
- Flag loss-prone actives: **B12, ascorbate, P5P, thiols (NAC) oxidize**; reducing sugars brown.

## Rule 3 — Ingredient-ingredient compatibility (สารขัดแย้งกันไหม)
Check each pair; report `pair → mechanism → mitigation`.

| Conflict class | Watch for | Typical fix |
|---|---|---|
| Precipitation / chelation | Divalent cations (Ca²⁺, Mg²⁺, Zn²⁺, Fe²⁺) + citrate / phosphate / carbonate / oxalate → insoluble salt | Separate phase, lower one, change salt form, raise solubilizer |
| Redox | Oxidizers vs reducers; Fe/Cu catalyze ascorbate & NAC-thiol oxidation | Remove trace metals, add chelator (EDTA), inert headspace |
| pH conflict | Acid-stable substance + alkaline buffer (or reverse) → one degrades | Re-target pH, split into two products |
| Maillard | Reducing sugars (ribose, glucose, maltodextrin) + amines (taurine, amino acids, B6) → browning, potency loss | Lower sugar, separate, cold storage |
| Physiological antagonism | Ingredients cancelling effect or competing for absorption/transport | Re-time dosing, drop redundant one |
| Acid-base / DEB | Net Na+K vs Cl imbalance (animal formulas) | Add Cl to control DEB; see avian wiki page |

## Output format (always produce)

| Substance | R1 Solubility (mg/mL / ratio) | R2 Stability (pathway / pH / shelf-life) | R3 Conflicts (pair → mechanism → fix) | Verdict |
|---|---|---|---|---|

Verdicts: ✅ OK · ⚠️ FLAG (usable with mitigation) · ❌ BLOCK. End with a one-line **GO / NO-GO** and a bullet list of blocking gaps (any `UNKNOWN` or ❌). The gate is complete only after the research is peer-reviewed AND the Substance Dossier(s) are written/updated.

## Substance Dossier Knowledge Base (MANDATORY)

Every substance investigated gets ONE persistent wiki page. Researching a new substance OR finding new info about an existing one → create/update its dossier in the SAME session. This is part of completing the gate, not optional — knowledge must not evaporate. Over time these dossiers connect the dots across formulas.

**Before researching:** `wiki_query({query:"<substance>", tags:["substance-dossier"]})`. Reuse what exists; research only the gaps.

**After any finding:** `wiki_ingest` (merges/appends, never overwrites):
- title: substance name; category: `reference`; tags: `[<substance>, "substance-dossier", ...]`
- `sources`: pass every PMID/DOI/edition used (sources are required, not optional)

**Dossier template (per substance):**
1. **Identity** — name, salt form(s), synonyms, CAS if known
2. **Three-rule findings** — R1 solubility (mg/mL, temp); R2 in-solution stability (pathways, stable pH, shelf-life, light/O2/metal sensitivity); R3 known conflicts. Each line cited.
3. **Avian/poultry evidence** — requirement, max tolerable, mechanism, onset (acute vs chronic), dose ranges + citations, or explicit "NO AVIAN DATA"
4. **Verdict for our use** — ADD-strong / conditional / SKIP / BLOCK + product/phase (preload vs fight-day)
5. **Cross-links** — `[[other-substance]]` for related / substitute / antagonist pairs (e.g. GAA ↔ creatine ↔ arginine; dextrose ↔ SGLT1-rehydration; ribose ↔ skip-list), plus [[gamefowl-supplement-formula-avian-grounded-evaluation]] and [[gamefowl-formula-v-next-team-codex-recovery-hydration-redesign]]
6. **Sources** — full citation list (Tier per Source Standard), with PMID/DOI
7. **Peer review** — who reviewed (agent/codex), date, verdict (confirmed / corrected — note what changed)
8. **Changelog** — date-stamped one-liners of what was learned each update

**Connect-the-dots rule:** when a substance interacts with or substitutes another, add reciprocal `[[cross-links]]` in BOTH dossiers so the graph stays connected.

## Worked mini-example
Adding **magnesium oxide 50 mg/mL** to a citrate buffer at pH 5.8:
- R1: MgO aqueous solubility ~0.0086 mg/mL → ratio ≪ 1 → ❌ BLOCK (insoluble; use Mg citrate/chloride instead).
- R2: stable, but as suspension it sediments.
- R3: Mg²⁺ + citrate → soluble Mg-citrate (OK) but Mg²⁺ + any phosphate present → precipitate.
- Verdict: ❌ BLOCK — switch salt form to a soluble Mg.
