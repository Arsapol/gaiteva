# Topics 02 + 09 — Volume-aware ORS/electrolyte gate and use-case-specific compatibility gates

Date: 2026-06-18
Worker: worker-2
Task: research-improvement-44ddd92b task 2
Scope: research/documentation only; no formula or calculator code changed.
Source context: `.omx/context/compat-stability-improvement-team-20260618T071451Z.md`

## Executive recommendation

Promote the current single hydration-oriented osmolality check into a route/use-case gate that reports:

1. **delivered concentration basis**: final mL/L after dilution, not just ingredient masses;
2. **Na/K/Cl ledger in mmol/L** and total per-session mmol/mg;
3. **glucose mmol/L and glucose:Na molar ratio**;
4. **route/use-case classification**: hydration drink, acute sublingual/oral-mucosal, dry capsule/premix, or wet concentrate;
5. **blocking vs advisory decision** tied to the route and claim.

The main design rule is: **osmolality is blocking for a swallowed hydration drink, but not automatically blocking for a brief acute oral-mucosal/sublingual product or for a dry capsule.** Dry products should be judged by dry-state controls; wet concentrates need both final-dilution checks and stored-liquid stability warnings.

## Current repo state

### Current calculator behavior

- `compat/osmolality.py` computes osmolarity from the **dissolved fraction** of each solute and classifies total mOsm/L as `PASS`, `MARGINAL`, or `BLOCK` using the current hydration bands: WHO ORS reference 245 mOsm/L, avian isotonic reference 300-320 mOsm/L, and hypertonic gate >350 mOsm/L.
- `osmolality_report()` combines osmolarity, `ors_gate()`, and `electrolyte_balance()` into a single hydration-oriented `blocking` boolean.
- `electrolyte_balance()` currently sums Na/K/Cl **mmol totals** from `compat.data.ELECTROLYTE_IONS`. It does not accept `water_ml`; therefore values are only mmol/L when the recipe is expressed per exactly 1 L, as in `reformulate.py` and `verify_dry_sku.py`.
- The current `complete_ors` criterion is `na > 0.0`. That is useful for catching “no sodium at all”, but too weak to certify a real ORS because trace sodium can pass the boolean without meeting an mmol/L target or a glucose:Na target.
- The current API does not compute glucose mmol/L or glucose:Na ratio even though the formula wiki and sugar dossiers treat glucose:Na as load-bearing for the SGLT1 hydration rationale.
- The current API does not take route/use-case input, so it cannot distinguish a swallowed hydration drink from an acute sublingual/oral-mucosal product, dry capsule, or wet concentrate.

### Current examples and evidence already in repo

- `compat_calc.py` demonstrates a failing liquid drench: the osmolality/electrolyte gate runs first and blocks the hyperosmolar, sodium-incomplete drench before chemistry levers matter.
- `reformulate.py` demonstrates a passing liquid ORS at **273.8 mOsm/L**, Na **74.1 mmol/L**, K **20.1 mmol/L**, Cl **64.6 mmol/L**, and glucose:Na **1.05** when calculated on its 1 L recipe basis.
- `verify_dry_sku.py` demonstrates the intended use-case split: dry capsule/preload products are eaten dry and do **not** receive a standing-solution osmolality gate; only the reconstituted fight-day drink is checked. That drink calculates at **291.2 mOsm/L**, Na **52.7 mmol/L**, K **14.8 mmol/L**, Cl **64.4 mmol/L**, glucose **111.0 mmol/L**, glucose:Na **2.11**.
- `concentrate.py` covers a 5x wet concentrate: the final 1:4 dilution can still be a PASS drink, but stored liquid reintroduces Maillard and microbial/preservation risk.
- `omx_wiki/field-osmolality-900-1000-ph58-65-oral-mucosal-tolerance.md` records field evidence that 900-1000 mOsm/L at pH 5.8-6.5 can be treated as acute oral-mucosal tolerance PASS under comparable short-contact conditions, while explicitly remaining separate from hydration/GI safety.
- `omx_wiki/gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md` and `omx_wiki/gamefowl-formula-v31-dilution-hybrid-higher-score-after-stats-v02.md` already encode the product-architecture split: make-fresh drink for hydration; dry preload/capsule for moisture-sensitive or low-solubility actives; wet concentrate only with explicit dilution/storage caveats.

## How the improvement works

### 1. Normalize every liquid calculation to delivered volume

For each formula, the future calculator/report should require:

- `route_kind`: `hydration_drink`, `acute_sublingual`, `dry_capsule`, `dry_premix`, `wet_concentrate`, or `wet_core_diluted`;
- `as_prepared_volume_ml`: volume in which the solutes are actually delivered;
- if concentrate: `concentrate_strength_x`, `dose_ml`, `diluent_ml`, and `final_delivered_volume_ml`;
- ingredient hydrate/salt form, especially dextrose monohydrate vs anhydrous dextrose and citrate salt hydrate state.

Then compute:

```text
ion_mmol_total = grams * ion_mmol_per_g
ion_mmol_per_l = ion_mmol_total / (final_delivered_volume_ml / 1000)

glucose_mmol_total = grams_dextrose / molar_mass_dextrose * 1000
glucose_mmol_per_l = glucose_mmol_total / (final_delivered_volume_ml / 1000)
glucose_to_na_ratio = glucose_mmol_total / na_mmol_total
```

Osmolality should continue using dissolved fraction, molar mass, osmotic particle count, and delivered volume:

```text
mOsm/L = dissolved_g / molar_mass_g_per_mol * osmotic_n / liters * 1000
```

### 2. Add a route/use-case gate matrix

| Use case | Main question | Osmolality decision | Electrolyte/glucose decision | Storage decision |
|---|---|---|---|---|
| Hydration drink / ORS | Will swallowed fluid support net water uptake? | **Blocking** if >350 mOsm/L or marked hypertonic; marginal 320-350; target current repo band <=320 and ideally <300 for current designs. | **Blocking** if sodium absent or clearly too low for the stated hydration claim; report Na/K/Cl mmol/L and glucose:Na. | Make fresh/discard same day unless preservative/challenge data exists. |
| Acute sublingual / oral-mucosal | Is short-contact oral tissue tolerance plausible? | **Advisory/route-specific**, not the ORS block. Repo field page supports 900-1000 mOsm/L at pH 5.8-6.5 for comparable short-contact oral exposure. | Do not imply hydration unless swallowed volume/electrolytes also pass ORS gate. | Watch irritant excipients, pH, contact time, repeat use. |
| Dry capsule / dry premix | Does a standing solution exist? | **N/A** unless label instructs dissolution. | Per-session mineral/sodium load can still be reported, but not as ORS mmol/L unless mixed into known water volume. | Governed by aw/moisture, hygroscopicity, caking, dose uniformity, oxidation/light. |
| Wet concentrate | Does final diluted dose pass, and can the concentrate survive storage? | Check both concentrate solubility and **final diluted mOsm/L**; final drink may pass while concentrate remains unsuitable as neat hydration. | Compute final Na/K/Cl and glucose:Na after dilution. | Stored water + reducing sugars/amines/actives creates microbial and Maillard risk; needs explicit shelf protocol or make-fresh limitation. |
| Wet core diluted at use | Does label dilution make the delivered dose safe for hydration? | Blocking if neat product is marketed as hydration while hypertonic; PASS can apply only to the labeled final dilution. | Report delivered electrolyte/ORS values at dilution, not bottle concentration alone. | Stored core still needs preservation/emulsion/stability validation. |

### 3. Split report severity by claim

The calculator should report separate severities rather than one global boolean:

- `hydration_blocking`: true/false, based on delivered drink osmolality and ORS completeness.
- `mucosal_tolerance_advisory`: pass/conditional/fail, based on route, pH, contact time, field threshold, and irritant excipients.
- `dry_state_advisory`: moisture/caking/aw/dose-uniformity flags for dry products.
- `storage_stability_advisory`: wet Maillard, microbial, preservative, redox, and packaging flags.
- `label_claim_allowed`: e.g., `hydration`, `oral_mucosal_tolerance_only`, `dry_preload_only`, or `not_a_hydration_drink`.

This prevents a high-osmolality sublingual product from being incorrectly called a hydration PASS, and prevents a dry capsule from being incorrectly penalized by a non-existent standing-solution gate.

## Formula-design impact

### Hydration drink design

- Keep hydration drinks dilute enough to pass the delivered osmolality gate.
- Keep Na/K/Cl visible in mmol/L, not just grams per stick.
- Keep glucose:Na in the documented project target zone when making an SGLT1 hydration claim. The current repo contains two useful anchors:
  - passing ORS demo: glucose:Na **1.05** at ~274 mOsm/L;
  - fight-day drink: glucose:Na **2.11** at ~291 mOsm/L.
- Pin hydrate forms. Dextrose monohydrate vs anhydrous dextrose changes glucose mmol and osmotic load enough to matter near a tight cap.
- Avoid “just concentrate it” as a field workaround. Higher concentration can break both hydration osmolality and palatability/intake.

### Acute sublingual/oral-mucosal design

- A 900-1000 mOsm/L short-contact product can remain acceptable under the repo field-evidence boundary, but only for comparable pH, contact time, excipients, and volume.
- Label claim should say oral-mucosal tolerance or rapid-contact use, **not hydration**, unless the swallowed/diluted product separately passes the hydration gate.
- pH and excipient irritancy become the main gate alongside repeat-use and contact-time monitoring.

### Dry capsule and dry premix design

- Do not apply liquid osmolality to dry products eaten dry.
- Report mineral/sodium/potassium load per dose where relevant, but reserve mmol/L language for known dilution volumes.
- Gate dry products through water activity, hygroscopicity, caking, dose uniformity, powder segregation, oxygen/light protection, and packaging.
- This supports the current vNext2 architecture: dry preload/capsule carries low-solubility or moisture-sensitive actives; make-fresh ORS carries the hydration function.

### Wet concentrate / wet core design

- Always calculate final delivered concentration after the label dilution.
- If neat concentrate is hypertonic, it must not be marketed or dosed as a hydration aid.
- A concentrate that dilutes to a PASS drink still needs a separate storage decision: reducing sugar + free amines in water, high aw, O2/light, preservative challenge, and refrigeration/short-shelf discipline.
- Formula cards should not “hide” dry activator solutes outside the hydration calculation if label instructions dissolve them in the same water.

## Risks and unknowns

- **Trace-sodium false PASS:** current `complete_ors = na > 0` can over-credit formulas with too little sodium.
- **Volume-mislabeled electrolytes:** current ion output is mmol total, not mmol/L unless recipe volume is 1 L.
- **No glucose:Na field in API:** glucose:Na is currently hand-derived from ingredient masses and docs.
- **Use-case ambiguity:** the same mOsm/L can be BLOCK for hydration but PASS/conditional for acute oral-mucosal tolerance.
- **Field evidence boundary:** the 900-1000 mOsm/L oral-mucosal tolerance page is practical field evidence, not controlled histopathology or repeated-use proof.
- **Hydrate-state drift:** dextrose monohydrate, anhydrous dextrose, sodium citrate hydrate form, and salt substitutions can move osmolality/ratio numbers.
- **Stats-card double counting:** future integration should avoid applying the same osmolality penalty once in compat and again in stats-card scoring unless intentionally separated.
- **Wet concentrate stability:** final dilution can pass while the stored concentrate remains shelf-risky.

## Validation / audit checklist

For future implementation and for manual formula reviews:

1. Record `route_kind` and exact label instruction.
2. Record final delivered volume and any concentrate dilution math.
3. Confirm ingredient salt/hydrate forms and molar masses.
4. Compute dissolved-fraction mOsm/L at final delivered volume.
5. Compute Na/K/Cl mmol total and mmol/L at final delivered volume.
6. Compute glucose mmol/L and glucose:Na molar ratio.
7. Classify osmolality as blocking only for hydration/drink claims, not globally.
8. For dry capsule/premix, mark solution osmolality N/A and run dry-state checks instead.
9. For acute sublingual/oral-mucosal, compare against route-specific field evidence and pH/contact/excipient boundaries.
10. For wet concentrate/core, separately check concentrate solubility/TDS, final diluted osmolality, and stored-liquid microbial/Maillard/redox risk.
11. Add golden fixtures for known examples:
    - failing `compat_calc.py` drench: hyperosmolar and sodium-incomplete block;
    - `reformulate.py` liquid ORS: ~274 mOsm/L, Na/K/Cl ~74/20/65, glucose:Na ~1.05;
    - `verify_dry_sku.py` fight-day drink: ~291 mOsm/L, Na/K/Cl ~53/15/64, glucose:Na ~2.11;
    - dry capsule/preload: osmolality N/A, dry-state advisory;
    - acute oral-mucosal 900-1000 mOsm/L pH 5.8-6.5: mucosal PASS/conditional, hydration not claimed;
    - wet concentrate: final dilution PASS possible, storage advisory remains.

## Affected files and surfaces

No code changed in this task. If implemented later, likely touchpoints are:

- `compat/osmolality.py` — add volume-aware electrolyte concentrations, glucose mmol/L, glucose:Na, route/use-case severity fields.
- `compat/data.py` and `substances/physical/*.json` — ensure molar masses, osmotic particle counts, hydrate forms, and ion mmol/g values are complete and provenance-tagged.
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py`, `concentrate.py` — update demos to call route-specific report modes.
- `compat/water_activity.py`, `compat/activity.py` — advisory surfaces for wet storage and ionic-strength refinements.
- `calculated-stats-card-v3-upgraded.*` and stats-card wiki pages — consume normalized route severity without double-counting.
- `omx_wiki/field-osmolality-900-1000-ph58-65-oral-mucosal-tolerance.md` — route-specific tolerance evidence.
- `omx_wiki/substance-dextrose-d-glucose.md`, `omx_wiki/substance-glucose-sucrose-drink-sugar-palatability.md`, `omx_wiki/substance-sodium-chloride-nacl.md`, `omx_wiki/substance-potassium-chloride-kcl.md`, `omx_wiki/substance-sodium-citrate-trisodium-citrate-dihydrate-alkalinizin.md` — ingredient-level rationale and caveats.
- Formula decision pages: `omx_wiki/gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md`, `omx_wiki/gamefowl-formula-v31-dilution-hybrid-higher-score-after-stats-v02.md`, and standardized formula pages.

## Evidence references

Local repo/context evidence used:

- `.omx/context/compat-stability-improvement-team-20260618T071451Z.md` — task context and ten improvement topics.
- `compat/osmolality.py` — current mOsm/L, electrolyte, and hydration blocking logic.
- `compat/data.py` — molar masses, osmotic particle counts, and Na/K/Cl mmol-per-gram table.
- `compat_calc.py` — failing hyperosmolar/sodium-incomplete drench demo.
- `reformulate.py` — passing liquid ORS example.
- `verify_dry_sku.py` — dry SKU vs reconstituted drink split and 291 mOsm/L drink verification.
- `concentrate.py` — wet concentrate final-dilution and storage-regression warning.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md` — prior calculator KB page.
- `omx_wiki/field-osmolality-900-1000-ph58-65-oral-mucosal-tolerance.md` — route-specific oral-mucosal field tolerance boundary.
- `omx_wiki/gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md` — dry SKU + fight-day ORS architecture and glucose:Na discussion.
- `omx_wiki/gamefowl-formula-v31-dilution-hybrid-higher-score-after-stats-v02.md` — dilution-labeled wet core and dry activator boundary.
- `omx_wiki/substance-dextrose-d-glucose.md` and `omx_wiki/substance-glucose-sucrose-drink-sugar-palatability.md` — glucose/SGLT1, sugar concentration, make-fresh, and glucose:Na rationale.
- `omx_wiki/substance-sodium-chloride-nacl.md`, `omx_wiki/substance-potassium-chloride-kcl.md`, `omx_wiki/substance-sodium-citrate-trisodium-citrate-dihydrate-alkalinizin.md` — electrolyte and chloride/citrate design rationale.

Subagent findings integrated:

- Review probe `019ed997-2e44-78a0-8b17-16a020fde6da` / Franklin: single global hydration gate, trace-sodium false PASS risk, route distinction, label wording.
- Test probe `019ed997-409c-71d0-834b-510445726d62` / Huygens: no automated test harness, golden fixture needs, current demo commands, concentrate coverage.
- Change-slice probe `019ed997-59ca-7083-bc8a-5189238351e2` / Carson: safe documentation slices, migration hazards, use-case matrix, hydrate-state drift, double-count risk.

## Coordination protocol

Coordination protocol: coordinated - task JSON changed from generic stale inbox text to scoped Topics 2+9; current task file was treated as source of truth, subagents were read back with the updated scope, output paths were kept to task-owned artifact/wiki files, and shared code/formula files were left untouched.
