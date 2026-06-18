# Compat improvement 6: pH, buffer-capacity, and dilution prediction

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

Medium-high — pH controls stability, preservative efficacy, palatability, and mineral forms.

## Current repo state

`compat/ph_module.py` provides Henderson-Hasselbalch helpers, a pH target-window check, and qualitative degradation-vs-pH text. It can say pH 3.0-4.0 is stabilizing for ascorbate/Maillard but does not predict final pH from a full formula, buffer capacity after dilution, neutralization by citrate/salts, or pH shift after adding dry stick to water. The prior wiki page also lists buffer-capacity-after-dilution as a remaining Tier-0 gap.

## How the improvement works

Add a pH/buffer module that estimates final pH from acid/base species, citrate forms, target water volume, and dilution. Minimum viable implementation can use Henderson-Hasselbalch plus alkalinity/acid equivalents and report low-confidence assumptions; a stronger version solves charge balance for citrate/phosphate/carbonate/amino-acid zwitterions. It should output pH, buffer capacity, pH-after-dilution, preservative active fraction, and stability windows for ascorbate, Maillard, creatine, and sorbate.

## How it affects formula design decisions

Designers can tune citrate/citric acid/Na-citrate ratios without accidentally moving a drink into poor preservative efficacy or acid-palate intolerance. It also clarifies when pH is a shelf-stability lever versus when high water activity and redox still require make-fresh or preservative challenge testing.

## Risks / unknowns

pH prediction from ingredient lists is approximate unless measured in the real water matrix. Amino acids, minerals, and high ionic strength can shift apparent pKa. A model may overstate preservative efficacy if it ignores microbial challenge results. Reports should require measured pH for any final candidate.

## Validation checklist

- [ ] Fixture predicts/labels pH target window for current `compat_calc.py` target pH 3.5.
- [ ] Dilution fixture reports pH before/after adding a dry stick to 1 L water.
- [ ] Sorbate active-fraction warning changes with pH.
- [ ] Measured pH field can override prediction while preserving prediction error for audit.
- [ ] Low-confidence cases list which acid/base constants are missing.

## Affected files / future touchpoints

- `compat/ph_module.py`
- `compat/data.py`
- `reformulate.py`
- `verify_dry_sku.py`
- future: compat/buffer.py

## Evidence references

- `compat/ph_module.py:1-226` contains HH helpers and qualitative degradation-vs-pH.
- `.omc/wiki/...:63` identifies buffer-capacity-after-dilution as remaining Tier-0 hardening.
- `compat_calc.py` output: pH 3.5 is within target window and suppresses Maillard while slowing ascorbate oxidation.
