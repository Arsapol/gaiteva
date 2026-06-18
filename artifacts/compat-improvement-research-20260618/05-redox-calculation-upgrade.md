# Compat improvement 5: Redox calculation upgrade

**Task/source context.** Worker-3 Task 3 research artifact generated 2026-06-18 from local evidence only. Required snapshot resolved at `/Users/arsapolm/Documents/my-projects/gaiteva/.omx/context/compat-stability-improvement-team-20260618T071451Z.md` because `.omx/context/` is not present inside this worker worktree. Scope is documentation/research only; no formula or calculator code changes are proposed here.

**Current evidence anchors used across this set.**
- `compat/osmolality.py:1-24`, `:86-170` — dissolved-fraction osmolality, ORS classification, and absolute Na/K/Cl completeness flag.
- `compat/solubility.py:49-200` — per-substance solubility, TDS, bottlenecks, and supersaturation warnings.
- `compat/data.py:368-406` plus `substances/physical/*.json` — external physical-constant overlays.
- `compat/redox.py:121-331` — ascorbate-focused redox screen with O2/light/metal/chelation drivers.
- `compat/ph_module.py:1-226` — Henderson-Hasselbalch helpers, pH-window check, degradation-vs-pH text.
- `compat/arrhenius.py:31-180` — Arrhenius `k`, Q10, acceleration factor, and per-pathway projections.
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py` — executable demos/fixtures.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md:46-87` — prior calculator reference page; no equivalent `omx_wiki/` page existed before this task.
- `calculated-stats-card-v3-upgraded.md:50-85`, `:124-156` — physical gate penalties already affect stats-card outputs but are not driven by a unified compat API.

## Priority / recommendation

Medium-high — critical for wet shelf decisions but must remain assay-bounded.

## Current repo state

`compat/redox.py` is focused on ascorbate. It estimates risk from metal level, chelator ratio, oxygen exposure, and light exposure, and carries a low-Ea warning that accelerated aging may under-predict ambient loss. `reformulate.py` surfaces this as a moderate ascorbate redox risk due to headspace O2 and clear packaging. Current support is useful but narrow: it does not model thiol antioxidants like NAC, copper/iron contaminant specs from supplier CoAs, peroxide/oil oxidation cross-effects, or packaging oxygen transmission rate.

## How the improvement works

Broaden redox into a mechanism ledger rather than a single ascorbate function. Add drivers for transition-metal impurities, dissolved oxygen/headspace, light, chelator identity/dose, antioxidant class, oil-phase oxidation, and packaging controls. Return a risk state plus required validation assays (e.g., ascorbate/DHAA, NAC/disulfide, peroxide value, colorimetry) and mitigation levers (opaque packaging, nitrogen purge, dry separation, chelator, same-day discard).

## How it affects formula design decisions

Formula designers can decide when wet storage is unacceptable and when make-fresh use is enough. It protects against false shelf confidence in ribose/ascorbate/NAC/copper-containing matrices and supports dry-first architecture for redox-labile actives while allowing same-day fresh drinks when chemistry risk is time-bounded.

## Risks / unknowns

Redox kinetics are matrix-specific; a screening score cannot replace stability assays. Chelators can reduce free metal but may not make redox-inactive complexes, and some metal/thiol systems have non-intuitive behavior. Packaging variables may be unknown during early design; reports should surface assumptions rather than guess.

## Validation checklist

- [ ] Existing ascorbate fixture still returns moderate risk for O2 + clear packaging.
- [ ] Wet NAC + metal/O2 fixture triggers thiol oxidation advisory/block for stored liquids but not dry-separated preload.
- [ ] Rules require real-time or assay evidence before 6-12 month shelf claims.
- [ ] Packaging fields (opaque/UV, low-O2, purge) change mitigation text without hiding residual risk.
- [ ] Report lists exact assays needed for each redox mechanism.

## Affected files / future touchpoints

- `compat/redox.py`
- `reformulate.py`
- `omx_wiki/substance-nac-n-acetylcysteine.md`
- `omx_wiki/substance-ascorbic-acid-vitamin-c.md`
- future: compat/redox_matrix.py

## Evidence references

- `compat/redox.py:121-331` implements ascorbate risk with metal/O2/light/chelation parameters.
- `reformulate.py` command evidence: moderate redox risk from headspace O2 and clear packaging.
- `omx_wiki/substance-nac-n-acetylcysteine.md` documents wet/stored NAC oxidation risk and dry-separation mitigation.
