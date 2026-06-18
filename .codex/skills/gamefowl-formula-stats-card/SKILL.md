---
name: gamefowl-formula-stats-card
description: Build reusable scorecards for gamefowl/avian supplement formulas. Use when the user asks to create, score, compare, rank, or refine a "stats card" for formula effects such as focus, endurance/fatigue resistance, recovery, ATP regeneration, inflammation/oxidative stress, respiratory support, hydration/electrolytes, GI tolerance, onset speed, or 6-12 month shelf stability; also use when evaluating single-bottle vs split-SKU formula tradeoffs.
---

# Gamefowl Formula Stats Card

## Core rule

Turn subjective formula claims into a numeric card with evidence boundaries. Do not score "pain tolerance" as a desirable endpoint; rename it **fatigue/stress tolerance** so the formula does not mask injury or distress.

If you recommend adding/removing/re-dosing substances, also use `formula-safety-check` before presenting the recommendation.

## Workflow

1. **Capture context**
   - Species/use case, bird weight if known, dose volume, timing, frequency, target shelf-life, and whether the product must be one bottle.
   - Formula table: ingredient, salt/form, amount per 100 mL or per dose, delivery route, storage condition.

2. **Score each metric 0-10**
   - Use the rubric in `references/rubric.md` when a detailed rubric is needed.
   - Always include **confidence**: High / Medium / Low.
   - Separate **acute effect** from **chronic/preload effect**.
   - Mark evidence type: avian trial, non-avian inference, physicochemical mechanism, field observation, or unknown.

3. **Output two tables**
   - **Formula stats card**: metric, score, confidence, key drivers, limiting factors.
   - **Ingredient contribution matrix**: ingredient vs metrics, using `++`, `+`, `0`, `-`, `--`, with one-line mechanism notes.

4. **Add interpretation**
   - Top 3 strengths.
   - Top 3 bottlenecks.
   - Best next experiment or field observation to improve confidence.
   - Shelf-life risk if target is 6-12 months.

## Default metrics

Use these unless the user asks otherwise:

1. Focus / alertness
2. Energy availability
3. Fatigue/stress tolerance
4. Fast recovery
5. ATP regeneration
6. Anti-inflammatory / antioxidant support
7. Respiratory / acid-base support
8. Hydration / electrolyte balance
9. GI tolerance
10. Onset speed
11. Shelf stability / commercial readiness

Optional rollups:
- **Performance-support score** = average of focus, energy, fatigue tolerance, onset.
- **Recovery/welfare score** = average of recovery, antioxidant, respiratory, hydration, GI tolerance.
- **Commercial-readiness score** = shelf stability plus formula simplicity/manufacturability.

## Scoring discipline

- Prefer conservative scores when acute avian evidence is absent.
- Do not let a strong mechanism produce a high score if the ingredient only works chronically but the use case is acute.
- Penalize stored wet formulas for reducing sugar + amine + vitamin/ascorbate combinations when shelf-life is 6-12 months.
- Penalize high oil emulsions if syringeability, separation, oxidation, and preservative challenge testing are unproven.
- Keep claims welfare-positive: hydration, recovery, respiratory support, fatigue resistance, and reduced oxidative stress.

## Useful script

Run `scripts/make_stats_card.py` to generate a blank Markdown card:

```bash
python /path/to/gamefowl-formula-stats-card/scripts/make_stats_card.py --formula "Route A Core" --out stats-card.md
```

Run `scripts/calculated_stats_card.py` when the user wants the score to be calculated rather than expert-estimated:

```bash
python /path/to/gamefowl-formula-stats-card/scripts/calculated_stats_card.py \
  --preset route_a --preset v3_hybrid \
  --out calculated-stats-card.md --json-out calculated-stats-card.json
```

For new substances, do not edit the Python script first. Create a reviewed external profile JSON, then pass it with `--profiles`:

```bash
python /path/to/gamefowl-formula-stats-card/scripts/calculated_stats_card.py \
  --json-in custom-formula.json \
  --profiles new-substance-profiles.json \
  --out calculated-custom-stats-card.md
```

Use `references/substance-profile-template.json` as the schema. If a formula contains an unknown substance without a profile, the calculator must list it as `UNKNOWN PROFILE` and give it zero contribution rather than silently inventing a score. Create profiles only after `formula-safety-check` has a dossier/review for the substance.

Run `scripts/audit_provenance.py` whenever profiles/constants are added or edited. Reviewed/verified records without field-level `source_refs` are invalid.

### Unknown-substance onboarding

The calculator is data-driven. Do **not** add a new substance by hardcoding Python dictionaries.

When a formula contains a new key:

1. Run the detector to create draft registry records:

```bash
python /path/to/gamefowl-formula-stats-card/scripts/onboard_substances.py \
  --json-in custom-formula.json \
  --out-dir substances
```

This writes:

- `substances/effects/<key>.json` — biological/effect scoring profile
- `substances/physical/<key>.json` — solubility, molar mass, osmotic, ion, pH/stability constants

2. Research the draft with `formula-safety-check` before scoring it:
   - search reliable sources for CAS/salt/hydrate identity, molar mass, solubility, osmotic particle count, ion mmol/g, pH/stability, degradation, and compatibility;
   - search avian/poultry evidence for effect profile and dose relevance;
   - write/update the `omx_wiki/substance-*.md` dossier with citations;
   - independently verify the dossier/profile.

3. Add field-level provenance before review approval:
   - effect profiles must include `sources` and `source_refs` for `ref`, `evidence`, every non-zero `effects.<metric>`, `chronic_only`, `wet_reactive_class` when present, and `notes`;
   - physical profiles must include `sources` and `source_refs` for `formula`, `molar_mass_g_per_mol`, `osmotic_n`, `solubility_g_per_100ml_25c`, `density_kg_m3`/`pka` when present, every `ions_mmol_per_g.<ion>`, and `note`;
   - use `wiki:<substance-dossier>` refs for cited facts, `rubric:stats-card-v0.2` for scoring-model judgement, `osmotic-model:screening-v0.2` for osmotic particle assumptions, and `calc:ion-stoichiometry-from-mw` for ion mmol/g calculations.

4. Only after review, change `review_status` from `draft` to `reviewed` or `verified`.

5. Run the provenance audit and fix every error before relying on the profile:

```bash
python /path/to/gamefowl-formula-stats-card/scripts/audit_provenance.py --project-root .
```

6. Rerun the calculator. Draft/rejected records must not silently create benefit points.

Use `references/physical-profile-template.json` for physical constants and `references/substance-profile-template.json` for effect profiles.

Calculation model (v0.2):
- ingredient effect profile by metric
- dose saturation against reference dose
- evidence multiplier: avian > field/avian-indirect > mechanism > non-avian/unknown
- timing multiplier so chronic/preload evidence does not overstate acute effects
- physical gates: solubility via the project `compat` package when available, dissolved-fraction contribution caps, direct-dose osmolality/ORS cap, wet ribose/amine/vitamin/redox risk, oil-emulsion burden, GI/oil/Mg burden, preservative/emulsion validation penalties
- layer reporting: biological potential, formulation feasibility, and final deliverable score
- confidence labels per metric plus an explicit penalty/cap ledger
- output raw contribution points so a future session can audit why each score changed
- registry loading: default profiles live in `registry/effects/*.json` and `registry/physical/*.json`; project-specific profiles live in `substances/effects/*.json` and `substances/physical/*.json`

If a liquid concentrate is diluted before use, custom JSON should set `delivered_water_ml`; otherwise the osmolality gate assumes the dose is used directly from the bottle.
