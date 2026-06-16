---
title: "Formulation Compatibility/Stability Calculator (compat/) — osmolality-gated, Codex-reviewed"
tags: ["compat-calculator", "formula-safety-check", "osmolality", "ORS", "arrhenius", "solubility", "tier0", "codex-reviewed", "gamefowl", "vnext2", "python"]
created: 2026-06-16T15:08:37.985Z
updated: 2026-06-16T15:08:37.985Z
sources: []
links: ["gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign.md", "formula-safety-check.md", "standardized-formulas-vnext2-per-100g-percent-and-usage-dose.md", "gamefowl-supplement-formula-avian-grounded-evaluation.md"]
category: reference
confidence: medium
schemaVersion: 1
---

# Formulation Compatibility/Stability Calculator (compat/) — osmolality-gated, Codex-reviewed

# Formulation Compatibility/Stability Calculator (`compat/`)

A Python package that models the **real governing physics** of a water-based gamefowl recovery/hydration supplement. Built from a 5-framework compatibility guide, but only the frameworks that actually apply to an ionic/sugar/amino-acid aqueous system were kept. Team-researched, Codex (gpt-5.5) peer-reviewed, and cross-validated against the existing [[gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign]] design.

Code lives at repo root: `compat/` package + `compat_calc.py` (failing-original demo), `reformulate.py` (passing liquid ORS), `verify_dry_sku.py` (dry-SKU gate check). Commits `d2c7d51`, `dab6be8`, `82b658c` on `chore/formula-skills-wiki`.

## The 5-framework verdict (what applies, what was cut)

| Framework | Equation | Verdict for this aqueous product |
|---|---|---|
| Gibbs ΔG=ΔH−TΔS | free energy | **BACKUP only** — flags spontaneity, not rate; primary safety = reactivity matrix ([[formula-safety-check]] gate) |
| Hansen HSP (Ra/RED) | cohesion distance | **REMOVED** — van-der-Waals/regular-solution theory; invalid for electrolytes, zwitterions, and water itself. Aqueous dissolution is governed by lattice vs hydration enthalpy + Ksp, not δd/δp/δh |
| Stokes' Law | settling velocity | **Undissolved-fraction ONLY** — dissolved solutes don't settle. Relevant only when a solute exceeds its ceiling (e.g. tyrosine) |
| HLB blend | emulsifier ratio | **REMOVED** — needs an oil phase/interface; none exists (glycerin is water-miscible) |
| Arrhenius k=A·e^(−Ea/RT) | shelf-life | **PRIMARY** — but per-pathway, not one global Q10 |

Confirmed by 3 parallel research agents + Codex: removing Hansen + HLB is scientifically correct for a fully water-soluble ionic/sugar/amino-acid system.

## The governing levers (final model)

**LEVER 0 — Osmolality + electrolyte balance (BLOCKING, biological).** Added after Codex review. For an oral-rehydration product this is the *first* gate, not an afterthought: a hyperosmolar drench pulls water INTO the gut lumen and fails as hydration even if every chemistry check passes. Water uptake is driven by Na⁺/glucose cotransport (SGLT1) — **glucose without sodium does not move water.** Reference bands: WHO low-osm ORS ≈ 245 mOsm/L; avian isotonic ≈ 300–320; cap < ~330.

**LEVER 1 — Additive solubility / TDS.** Per-substance g/100mL ceiling, total dissolved solids %w/v, salting-out flag >20%, bottleneck detection. (Codex refinement: true name is *speciation-adjusted saturation index* — single-solute ceilings are a screen, not strictly additive in a dense matrix.)

**LEVER 2 — pH 3.0–4.0 via citrate buffer.** Suppresses ascorbate oxidation AND Maillard browning simultaneously (browning negligible pH<4). Caveat: pH 3–4 is not a free pass for ascorbate — O₂/Cu/Fe/light can dominate (see Tier-0 redox).

**LEVER 3 — Per-pathway Arrhenius.** Split by mechanism with literature Ea bands (low/typical/high):
- ascorbate_oxidation: LOW Ea ~15–67 kJ/mol → AF only ~2× at 40 vs 25°C → **ICH Q1A real-time 25°C data mandatory**, oven test under-predicts.
- maillard_browning: HIGH Ea 65–160 → AF ~7× → accelerated aging predictive.
- creatine_cyclization: ~90–105, pH-dependent → predictive.

## Package modules

| File | Role |
|---|---|
| `data.py` | per-substance constants: solubility, density, pKa, MW, osmotic-N, electrolyte ions + per-pathway Ea. Provenance-tagged (dossier vs literature) |
| `solubility.py` | additive solubility, TDS, salting-out + bottleneck flags |
| `arrhenius.py` | per-pathway shelf-life, Q10, acceleration factor, ICH warnings |
| `ph_module.py` | pH-window check, citrate buffer (Henderson-Hasselbalch), degradation-vs-pH |
| `stokes.py` | settling gated to undissolved fraction only |
| `gibbs.py` | backup thermodynamic safety screen (labeled non-primary) |
| `osmolality.py` | **BLOCKING** osmolarity + Na/K/Cl balance + SGLT1 reasoning |
| `redox.py` | Tier-0: ascorbate metal/O₂/light/chelation risk; low-Ea ICH warning |
| `activity.py` | Tier-0: ionic strength + Davies γ± + Setschenow salting correction |
| `water_activity.py` | Tier-0: Raoult/Norrish aw + FDA microbial thresholds |

## Trust-hardening tiers (Codex-ordered)

- **Tier 0 (in code now):** osmolality + Na/K/Cl (blocking), redox metal/O₂ flag, ionic-strength/activity correction, water-activity/microbial flag. Remaining: buffer-capacity-after-dilution wrapper.
- **Tier 1 (no lab):** supplier CoA + contaminant metals, moisture/aw, particle size, polymorph, microbial limits, packaging OTR/WVTR, matrix-specific Ea as priors.
- **Tier 2 (bench — the only thing that makes numbers TRUE):** saturation/osmolality/aw/dose-uniformity in real matrix; accelerated 25/30/40°C (50°C stress-screen only) with HPLC ascorbate+DHAA / creatine+creatinine, colorimetry, microbial/challenge; parallel real-time 25°C.

**Honest hierarchy:** Tier 0 is enough for a GO/NO-GO *formulation* decision. A *label* shelf-life claim requires Tier 2 — no calc or literature substitutes for assaying your own product.

## Key findings produced

1. **Naive 150 mL drench (glycerin + dextrose + tyrosine + creatine etc.) = NO-GO**: 1542 mOsm/L (~6× WHO ORS), no electrolytes. Glycerin alone = 724 mOsm/L. Tyrosine (ceiling 0.045 g/100mL) and creatine (1.4) can't dissolve at dose. **The binding problem was osmotic load + missing electrolytes, not stability.**
2. **Reformulated liquid ORS passes**: 274 mOsm/L, Na 74/K 20/Cl 65 (matches WHO low-osm ORS), 0 bottlenecks — achieved by removing glycerin, cutting dextrose to cotransport level, adding NaCl/KCl/Na-citrate, and moving insoluble/high-osmotic actives to the dry SKU.
3. **Dry-SKU cross-validation**: the calc independently reproduced the vNext2 fight-day drink numbers exactly — **291 mOsm/L** (wiki claim 291), Na 52.7/K 14.8/Cl 64.4 (claim ~53/15/64), complete ORS. Margin to the 300 cap is only **+9 mOsm/L → the dextrose-MONOHYDRATE spec is load-bearing** (anhydrous MW 180 vs 198 → ~302, over cap; manufacturing must not substitute).
4. aw ≈ 0.995 for any liquid → microbially unstable on its own; low pH ≠ preservation. Confirms the dry-first / make-fresh design choice.

## Codex review (gpt-5.5, 2026-06-16)

Artifact: `.omc/artifacts/ask/codex-context-research-evaluation-...md`. Confirmed Hansen/HLB removal and the chemistry levers. Headline correction: **the product was treated as a chemistry problem first; the first biological gate for an avian oral drench is osmotic + electrolyte load at bolus concentration.** That correction is now enforced as blocking LEVER 0. Added missing levers: osmolality, Na/K/Cl + acid-base, free-metal redox, water activity/microbial, packaging/reconstitution state.

## How to use

```
python3 compat_calc.py      # failing-original demo (NO-GO contrast)
python3 reformulate.py      # passing liquid ORS (274 mOsm/L)
python3 verify_dry_sku.py   # dry-SKU gate check (drink = 291 mOsm/L, PASS)
```
Each module also has a `__main__` smoke test. All functions pure/immutable; constants in `data.py` are read-only.

## Links
- [[gamefowl-recovery-hydration-formula-vnext2-two-dry-sku-redesign]] — the design this validates
- [[standardized-formulas-vnext2-per-100g-percent-and-usage-dose]] — fight-day drink recipe verified here
- [[gamefowl-supplement-formula-avian-grounded-evaluation]]
- Per-substance dossiers under tag `substance-dossier` supplied the `data.py` constants

