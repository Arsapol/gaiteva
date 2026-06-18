# Topics 06+07 — pH/buffer-capacity/dilution prediction + assay-driven Arrhenius shelf-life projection

**Team/task:** research-improvement-44ddd92b / worker-5 / task 5  
**Date:** 2026-06-18  
**Scope:** research/documentation only. No formula or calculator code changed.  
**Output pair:** this audit artifact plus wiki-ready page `omx_wiki/research-compat-improvement-ph-arrhenius-2026-06-18.md`.

## Executive recommendation

Upgrade the compat calculator from **target-pH checking** to a two-part, evidence-gated decision system:

1. **Citrate pH/buffer/dilution predictor:** estimate pH from free citric acid + citrate salts + dilution volume, calculate buffer capacity around the target pH, and warn when dilution or alkali salts move the drink outside the intended pH/preservative/compatibility window.
2. **Assay-driven Arrhenius projection:** keep the existing literature-Ea pathway model as a prior, but let real 25/30/40 °C stress-assay observations fit or bound pathway-specific rates; never convert a short 40 °C assay into a label shelf life without real-time 25 °C confirmation, especially for low-Ea ascorbate oxidation.

Design effect: formula decisions stop treating pH and shelf life as static labels. The calculator can ask: “If this dry stick is mixed into 1 L, what pH and buffer reserve result?” and “Which measured degradation pathway is shelf-life limiting?” This protects the current dry-first/make-fresh strategy and gives future wet-SKU proposals an auditable no-go gate.

## Current repo state

### pH / buffer handling today

- `compat/ph_module.py` contains pure helpers for:
  - Henderson-Hasselbalch single-pKa ratio calculation.
  - `citrate_buffer_ratio(target_pH)`, which chooses the citric-acid pKa nearest a supplied pH.
  - `ph_window_check(target_pH)`, currently enforcing a hardcoded target window of pH 3.0–4.0.
  - `degradation_vs_ph(target_pH)`, qualitative guidance for ascorbate oxidation and Maillard browning.
- The module **does not predict pH** from formula ingredients. It requires `target_pH` as an input and therefore cannot answer whether a proposed citric-acid / sodium-citrate / potassium-citrate recipe will actually land there.
- It also does not calculate:
  - total analytical citrate concentration,
  - acid/base equivalents,
  - buffer capacity (`dB/dpH`),
  - dilution pH drift,
  - pH uncertainty from hydrate form or ingredient tolerance,
  - pH-dependent preservative active fraction.
- `compat/data.py` provides citric-acid pKa values `[3.13, 4.76, 6.40]`, citric-acid MW 192.12, trisodium citrate dihydrate MW 294.10, osmotic particle approximations, and electrolyte ion contributions.
- `compat/activity.py` already computes ionic strength and acknowledges Davies-validity limits. That is useful for a future pH predictor because pKa/activity corrections should be optional and clearly labeled as screening-grade.
- `compat_calc.py` prints “target pH 3.5” as a demo scenario. This demonstrates a window check, not an ingredient-derived pH prediction.

### Arrhenius / shelf-life handling today

- `compat/arrhenius.py` has pure functions for `arrhenius_k`, `q10`, `accel_factor`, `pathway_projection`, and `all_pathways`.
- `compat/data.py` registers three degradation pathways with literature-prior Ea ranges:
  - `ascorbate_oxidation`: 15/40/67 kJ/mol.
  - `maillard_browning`: 65/100/160 kJ/mol.
  - `creatine_cyclization`: 90/97/105 kJ/mol.
- The current model calculates Q10, acceleration factors, stress weeks for a 24-month equivalent, and an ICH caution string. Example current outputs at 40 °C stress / 25 °C storage:
  - ascorbate oxidation: AF typical ~2.2x; ~48.2 weeks at 40 °C for a 24-month 25 °C equivalent; low-Ea warning.
  - Maillard browning: AF typical ~6.9x; ~15.1 stress weeks.
  - creatine cyclization: AF typical ~6.5x; ~16.0 stress weeks.
- The model is **prior-only**. It has no schema for real assay observations, no fitting step, no confidence interval, no censoring support (e.g., “<5% loss at 8 weeks”), and no rule that measured real-time 25 °C data outranks accelerated data.

### Product-design context in wiki evidence

- The current formula direction is dry-first: `omx_wiki/gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md` states that dry-first strongly reduces hydrolysis, Maillard, microbial growth, photolysis, thiol oxidation, and preservative-at-pH-6 defects.
- The fight-day drink target is make-fresh/discard-same-day with citric acid acidification around pH ~3.8–4.2 in the redesign page, while `compat/ph_module.py` currently calls pH 3.0–4.0 the optimal stability window. This mismatch should be made explicit as a product-use-case policy decision, not hidden inside code.
- `omx_wiki/substance-citric-acid-anhydrous-also-monohydrate.md` says citric acid is stable, highly soluble, chelates trace metals, suppresses Maillard via low pH, and should be used as free acid while minimizing citrate salts.
- `omx_wiki/substance-sodium-citrate-trisodium-citrate-dihydrate-alkalinizin.md` and the recovery redesign warn that bulk citrate salts are alkalinizing/DEB-relevant and should stay trace-only in the fight-day drink.
- The prior compat reference `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md` already lists “buffer-capacity-after-dilution wrapper” as a remaining Tier-0 gap and states that a label shelf-life claim requires bench/real-time evidence.

## Topic 06 — How the pH/buffer-capacity/dilution improvement works

### Inputs to model

Minimum future input schema:

```text
components: [{name, grams, form, purity?, hydrate?, role?}]
water_ml_or_final_volume_ml
use_case: hydration_drink | acute_sublingual | dry_capsule | wet_concentrate
measured_initial_pH?       # optional calibration override
measured_post_dilution_pH? # optional validation observation
```

Required citrate species for first implementation:

- `citric_acid` as free acid, MW 192.12 g/mol or monohydrate-adjusted MW 210.14 if that form is used.
- `trisodium_citrate` as the conjugate-base/alkali source, currently modeled as dihydrate MW 294.10.
- Optional future `potassium_citrate` once the physical constants registry owns it consistently.

### Screening algorithm

1. **Convert masses to moles.** Track hydrate form explicitly so anhydrous vs monohydrate does not create a silent ~9% acid-equivalent error.
2. **Build total citrate pool (`C_T`).** Sum all citrate-bearing species.
3. **Build charge/alkalinity ledger.** Citric acid contributes acid equivalents; trisodium citrate contributes sodium and citrate base equivalents. Combine with strong ions from NaCl/KCl and other acid/base contributors when registered.
4. **Solve electroneutrality for pH** rather than choosing the nearest pKa:
   - For triprotic citric acid, use alpha fractions for H3Cit, H2Cit-, HCit2-, and Cit3- as a function of `[H+]` and pKa values.
   - Include strong-ion charge balance and water autoionization.
   - Return the pH root plus warnings if no physical root is found inside the product policy range.
5. **Calculate buffer capacity** around the pH root. For screening, report mmol/L acid or base needed to shift pH by ±0.1 and ±0.5. This is more useful to formulators than a single pH number because dilution and ingredient lot variation matter.
6. **Simulate dilution.** Re-run pH and buffer capacity at use dilution: concentrate → final drink, dry stick → 1 L, or stock drops → dosing water. Dilution lowers total buffer capacity even when pH changes modestly.
7. **Apply product-use-case gates.** Examples:
   - Fight-day ORS/make-fresh: acceptable pH may be wider for palatability and discard-same-day, but should still keep microbial/preservative claims honest.
   - Wet concentrate: pH must support preservative efficacy and stability after worst-case dilution and storage drift.
   - Dry capsule/preload: no standing-solution pH gate; only reconstitution warnings if users dissolve it.
8. **Surface uncertainty.** Label predicted pH as screening-grade until confirmed by meter reading in the actual matrix at temperature and dilution.

### Outputs to return

A future report should include:

- predicted neat pH and diluted pH,
- buffer capacity at predicted pH,
- total citrate mmol/L and free-acid/base split,
- strong-ion/DEB implications for sodium/potassium citrate,
- pH-window verdict per use-case,
- pH-dependent stability flags:
  - ascorbate oxidation rises toward/above pH ~4,
  - Maillard risk rises with pH and heat in reducing-sugar + amine systems,
  - sorbate/benzoate active fraction depends on undissociated acid fraction,
  - creatine cyclization is acid-catalyzed and should generally remain dry for shelf life.

### Formula design impact

- **Citric acid becomes a controlled q.s. lever, not a guessed gram amount.** Designers can specify “q.s. to measured pH X after 1 L dilution” and reject a recipe whose calculated buffer reserve is too weak.
- **Citrate salts stop being hidden pH raisers.** Sodium/potassium citrate can be useful trace buffers but also contribute alkali/DEB and can antagonize acid-dependent preservatives if overused.
- **Dilution labels become chemistry-critical.** A wet concentrate can appear acceptable neat but fail after dilution if active preservative fraction or buffer reserve collapses. Conversely, a dry stick can be safe because its wet window is short and discarded same-day.
- **pH policy can vary by product class.** The repo currently has pH 3.0–4.0 in code and pH ~3.8–4.2 in the redesign wiki. The improvement should make this an explicit gate table rather than a buried constant.
- **Assay planning improves.** Predicted pH and buffer capacity identify which pH levels to test during stress studies and which lots need meter confirmation.

### Risks and unknowns

- Ionic strength and activity can shift apparent pKa; `compat/activity.py` supports screening corrections but does not make them validated thermodynamics.
- The actual matrix contains sugars, amino acids, salts, possible preservatives, and temperature effects; a simple citrate-only model may be wrong by several tenths of a pH unit.
- Hydrate/form identity matters: citric acid anhydrous vs monohydrate and trisodium citrate dihydrate vs anhydrous must be explicit.
- pH meter method matters: temperature compensation, calibration buffers, ionic-strength effects, sample turbidity, and CO2 uptake can create audit drift.
- Palatability and avian tolerance are not solved by pH chemistry alone. Over-acidification can be counterproductive even when chemically stable.

## Topic 07 — How the assay-driven Arrhenius improvement works

### Inputs to model

Minimum future assay schema:

```text
pathway: ascorbate_oxidation | maillard_browning | creatine_cyclization | custom
analyte_or_marker: ascorbate, DHAA, creatine, creatinine, browning_A420, color_deltaE, etc.
formulation_id / lot_id
pH, water_activity, packaging, headspace, light, oxygen, metal_ppb
storage_conditions: [{temperature_C, time_days, measured_value, unit, replicate_id}]
acceptance_limit: e.g. >=90% potency, creatinine max, color max, pH drift max
model_type: zero_order | first_order | empirical_marker | censored_bound
```

### Fitting / projection algorithm

1. **Fit rate per pathway and temperature.** Use the assay marker appropriate to the mechanism:
   - ascorbate: potency loss and/or DHAA formation,
   - Maillard: color/browning or marker compound,
   - creatine: creatinine formation / creatine loss,
   - preservative/microbial: separate challenge-test logic, not Arrhenius alone.
2. **Choose kinetics form explicitly.** First-order is often reasonable for potency loss, but browning/color can be zero-order or empirical over a limited range. The report should state the assumption.
3. **Fit Arrhenius only when multiple temperatures exist.** With only one stress temperature, use the repo Ea prior as a bounded assumption and label the result “prior-constrained,” not measured.
4. **Calculate Ea and acceleration factor with uncertainty.** Return median/low/high or confidence intervals rather than a single shelf-life number.
5. **Project to 25 °C by pathway.** Shelf life is the earliest time any pathway crosses its acceptance limit.
6. **Apply ICH/real-time guardrails.** Accelerated data can support mechanism understanding and tentative ranking, but real-time 25 °C data must confirm shelf-life claims. Low-Ea ascorbate oxidation is especially resistant to compression: the current repo prior gives only ~2.2x acceleration at 40 °C vs 25 °C.
7. **Separate screening from label claims.** A 40 °C oven screen may be enough to reject a wet SKU early; it is not enough to grant a 12–24 month label shelf life.

### Outputs to return

A future report should include:

- pathway-specific fitted rates at each temperature,
- fitted or prior-constrained Ea,
- acceleration factor and uncertainty for each pathway,
- estimated time to each acceptance limit at 25 °C,
- “limiting pathway” ranking,
- ICH/real-time status:
  - `screen_only`,
  - `accelerated_supported_real_time_pending`,
  - `real_time_confirmed`,
  - `insufficient_data`,
- explicit storage-condition scope: packaging, light, oxygen, pH, water activity, preservative system.

### Formula design impact

- **Dry-first remains strongly favored until wet assays prove otherwise.** Dry SKUs avoid standing-water pathways and can often be justified with moisture/aw/packaging checks rather than wet-potency projections.
- **Wet SKUs need pathway-specific proof.** A wet sugar/amino-acid/vitamin matrix cannot borrow a generic Q10. It needs ascorbate/DHAA, color/Maillard, creatine/creatinine, pH drift, and microbial/challenge data as applicable.
- **Ascorbate is a special caution.** Low Ea means refrigeration/40 °C acceleration may not separate rates dramatically; metal/O2/light controls can dominate. Formula design should move vitamin C dry/separate unless a wet product has assays.
- **Maillard is heat-sensitive and pH-sensitive.** High Ea means warm stress screens can reveal browning risk, but final design still needs pH and water activity controls.
- **Creatine belongs dry for shelf life.** Acidic pH may help other pathways but can accelerate creatine cyclization; this trade-off becomes visible in the pathway ranking.
- **Shelf-life claims become acceptance-limit based.** The question changes from “what is the Q10?” to “which measured marker crosses the product-specific limit first?”

### Risks and unknowns

- Literature Ea values are priors, not finished-product truth. Matrix pH, ions, metals, light, oxygen, water activity, and packaging can change rates.
- Extrapolating from too-high stress temperatures can introduce different mechanisms; 50 °C should be treated as an abuse screen unless validated.
- Censored data and noisy assays can give false confidence if fitted as exact values.
- Color/browning markers may not map directly to biological efficacy or acceptability.
- Microbial stability is not an Arrhenius potency problem; water activity, pH, preservative efficacy, and challenge tests must remain separate gates.
- A calculator cannot replace real-time stability for commercial claims.

## Validation / audit checklist

### pH/buffer/dilution checklist

- [ ] Unit tests for triprotic citrate alpha fractions at pH 3.13, 4.76, and 6.40.
- [ ] Golden fixture for current fight-day ORS recipe from `omx_wiki/standardized-formulas-vnext2-per-100g-percent-and-usage-dose.md` using citric acid 0.7 g/L and sodium citrate dihydrate 0.3 g/L.
- [ ] Hydrate-form tests: citric acid anhydrous vs monohydrate and trisodium citrate dihydrate vs anhydrous must change acid/base equivalents correctly.
- [ ] Dilution tests: concentrate-to-use dilution must preserve moles and reduce buffer capacity appropriately.
- [ ] Gate tests for use-case policy: hydration drink vs wet concentrate vs dry capsule.
- [ ] Comparison against measured pH in actual matrix at 20–25 °C; prediction tolerance should be declared (e.g., ±0.2–0.3 pH units until calibrated).
- [ ] Explicit warnings when unmodeled acid/base substances are present.

### Arrhenius assay checklist

- [ ] Unit tests for existing `q10` and `accel_factor` equations remain unchanged.
- [ ] Golden fixtures using current prior-only outputs: ascorbate AF ~2.2, Maillard AF ~6.9, creatine AF ~6.5 at 40→25 °C.
- [ ] Schema tests for assay records: temperature, time, marker, units, lot, pH, packaging, and replicate metadata required.
- [ ] Fit tests using synthetic first-order data with known Ea.
- [ ] Censoring tests for “below detection,” “less than X loss,” and failed/noisy data.
- [ ] Projection report must identify limiting pathway and confidence band.
- [ ] Guardrail test: one-temperature accelerated data cannot return `real_time_confirmed`.
- [ ] Guardrail test: low-Ea ascorbate pathway always emits real-time/metal/O2/light caution.
- [ ] End-to-end fixture for a wet SKU showing no-go if any pathway crosses the acceptance limit early.

## Affected files for a future implementation

Research-only work changed no code. A future implementation would likely touch:

- `compat/ph_module.py` — add ingredient-derived pH, triprotic citrate speciation, buffer capacity, dilution reporting.
- `compat/arrhenius.py` — add assay-data fitting/projection while preserving current prior-only helpers.
- `compat/data.py` — ensure citrate species, hydrate forms, molar masses, pKa provenance, and degradation priors are registry-driven.
- `compat/activity.py` — optionally provide ionic-strength/activity corrections to pH/speciation reports.
- `compat/osmolality.py` — share volume and electrolyte/ion accounting with the pH predictor.
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py` — demo/report integration only after API design is stable.
- `substances/physical/*.json` — add or normalize potassium citrate, citrate hydrate/form records, assay metadata if registry-owned.
- `calculated-stats-card-v3-upgraded.*` — later integration point for shelf/readiness penalties and normalized scoring.
- `omx_wiki/*.md` — promote policy/gate documentation and validation evidence.

## Evidence references

Local repo/wiki evidence inspected:

- `/Users/arsapolm/Documents/my-projects/gaiteva/.omx/context/compat-stability-improvement-team-20260618T071451Z.md` — team topic list, constraints, known repo facts, and touchpoints.
- `compat/ph_module.py` — current pH window, Henderson-Hasselbalch, citrate ratio, qualitative degradation guidance.
- `compat/arrhenius.py` — current Arrhenius equations, per-pathway projection API, ICH caution strings.
- `compat/data.py` — citric acid pKa/MW/solubility, trisodium citrate MW/osmotic/electrolyte values, degradation Ea priors.
- `compat/activity.py` — ionic strength and Davies/Setschenow screening limits.
- `compat/osmolality.py` — volume-aware osmolarity/electrolyte gate that future pH dilution logic should align with.
- `compat_calc.py` — current demo uses target pH and prior-only Arrhenius pathways.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md` — prior compat calculator reference; identifies buffer-capacity-after-dilution as remaining Tier-0 gap and bench/real-time evidence hierarchy.
- `omx_wiki/substance-citric-acid-anhydrous-also-monohydrate.md` — citric acid role, pKa, solubility, stability, chelation, and dosage caveats.
- `omx_wiki/substance-sodium-citrate-trisodium-citrate-dihydrate-alkalinizin.md` — citrate salt alkalinizing/DEB warnings.
- `omx_wiki/substance-potassium-citrate-tripotassium-citrate-monohydrate.md` — citrate salt replacement/alkali concerns.
- `omx_wiki/substance-ascorbic-acid-vitamin-c.md` — pH/redox/light/metal sensitivity context.
- `omx_wiki/substance-creatine-monohydrate.md` — creatine dry-vs-wet and cyclization concerns.
- `omx_wiki/standardized-formulas-vnext2-per-100g-percent-and-usage-dose.md` — current standardized dry-stick formula amounts and pH/osmolality context.
- `omx_wiki/gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md` — product-class policy, dry-first rationale, pH ~3.8–4.2 make-fresh drink, and shelf-life caveats.

## Coordination / delegation notes

- Coordination protocol: coordinated - task file, inbox, context snapshot, artifact path, wiki path, and shared repo surfaces checked; no formula/code files modified.
- Subagents spawned: 3 (Review probe, Change-slice probe, Evidence-mapping probe).
- Subagent model: gpt-5.4-mini via installed `researcher`/`architect` roles.
- Serial searches before spawn: 0 deep repo searches after claim; probes were spawned before broad repo inspection.
- Findings integrated: pending until child reports return; final task transition will include exact subagent evidence line.
