# Topics 3 + 5 — Pairwise incompatibility matrix + redox calculation upgrade

## Current repo state

Task 3 was refined to focus on improvement topic 3 (machine-readable pairwise incompatibility matrix) and topic 5 (redox calculation upgrade). The current repository has useful ingredients but no central rule engine:

- Pairwise incompatibility knowledge is mostly prose in `omx_wiki/substance-*.md` dossiers and the formula-safety workflow, not a machine-readable matrix.
- `compat/gibbs.py` is intentionally a backup thermodynamic screen; the existing calculator and prior `.omc` wiki page warn that `dG < 0` is not a practical incompatibility or rate guarantee.
- `compat/redox.py` is focused on ascorbate and uses qualitative/string-style inputs for metal level, chelation, oxygen exposure, and light exposure. It is useful as a Tier-0 screen but not a quantitative shelf-life model.
- `compat_calc.py` manually demonstrates Gibbs as backup and redox/pH/osmolality as practical gates; `reformulate.py` surfaces moderate ascorbate redox risk from headspace O2 and clear packaging.
- `calculated-stats-card-v3-upgraded.md` already penalizes wet reducing-sugar + primary-amine Maillard risk, wet ribose + ascorbate/redox shelf risk, preservative challenge gaps, emulsion validation gaps, and TDS/osmolality blocks, but those penalties are not generated from a single pairwise/redox API.

Current executable evidence captured in this worker pass:

- `python3 compat_calc.py` — failing wet drench: **1542 mOsm/L -> BLOCK**, no added Na/K/Cl, tyrosine and creatine bottlenecks; chemistry levers are moot until the biological gate passes.
- `python3 reformulate.py` — passing ORS: **274 mOsm/L -> PASS**, Na 74.1 / K 20.1 / Cl 64.6 mmol/L, with moderate ascorbate redox risk from headspace O2 and clear packaging plus high-aw challenge-test warning.
- `python3 verify_dry_sku.py` — dry Products 1/2 exempt from standing-solution osmolality; reconstituted drink **291 mOsm/L -> PASS**, aw high-risk but same-day discard mitigates the brief wet window.

## How the improvement works

### Topic 3: machine-readable pairwise incompatibility matrix

Create a versioned matrix such as `substances/compatibility/pairwise-rules.json` plus a pure evaluator such as `compat/pairwise.py`. Each rule should include:

- `rule_id`, `version`, `status`, `source_refs`, and `last_reviewed`.
- `a` and `b` selectors by exact `compat_key` and/or class, for example `reducing_sugar`, `primary_amine`, `thiol`, `transition_metal`, `weak_acid`, `polyvalent_cation`, `oil_phase_active`, `preservative`.
- `phase_context`: dry, wet stored, make-fresh, concentrate, reconstituted drink, oil emulsion, capsule/premix.
- `mechanism`: Maillard/browning, metal-catalyzed oxidation, thiol disulfide formation, precipitation/complexation, preservative inactivation, phase partitioning, pH-driven degradation.
- `severity`: pass, advisory, marginal, block, unknown; with confidence and whether dry separation or same-day reconstitution downgrades severity.
- `mitigations`: dry separation, opaque/low-O2 packaging, chelator, pH window, dilution, same-day discard, order-of-addition, supplier CoA metal limits.
- `validation`: HPLC/potency, colorimetry, peroxide value, pH, measured osmolality, turbidity/precipitation, microbial/challenge, dose uniformity.

The evaluator should expand ingredient classes and exact pairs, return a rule ledger, and never silently treat an unmodeled pair as safe. Unknown class membership should reduce confidence or add an explicit unknown.

### Topic 5: redox calculation upgrade

Broaden `compat/redox.py` from an ascorbate-specific qualitative screen into a mechanism ledger. Minimum useful fields:

- Ingredient mass, MW, and calculated moles for redox-active compounds.
- Transition-metal input from formula additions and supplier CoA contaminant ppm (Cu, Fe, Mn where relevant), not just qualitative strings.
- Chelator identity and molar ratio (citrate/EDTA/etc.) with a warning that chelation is not automatically redox-proof.
- Oxygen exposure: headspace, dissolved oxygen assumption, purge status, container OTR, hold time after reconstitution.
- Light exposure: clear/amber/opaque and UV protection.
- Matrix context: pH, water activity, phase, oil/emulsion, storage temperature, make-fresh vs stored.
- Mechanism outputs for ascorbate oxidation, thiol oxidation (NAC/cysteine-like), oil peroxide risk, ribose/ascorbate co-loss, and transition-metal catalysis.

The report should return qualitative risk plus required assays. Quantitative projections should remain low-confidence unless backed by product-specific stress/real-time data.

## How it affects formula design decisions

A pairwise matrix and stronger redox screen would make wet/dry architecture decisions auditable instead of prose-only:

- **Wet stored products**: ribose + ascorbate, reducing sugars + primary amines, NAC/thiols + metals/O2, and oil-emulsion oxidation become explicit shelf/commercial-readiness risks.
- **Dry split SKUs**: tyrosine, ascorbate, taurine, NAC, and other redox- or solubility-sensitive actives can be separated from wet matrices and scored as dry-storage/dose-uniformity problems instead of wet-shelf blocks.
- **Make-fresh drinks**: same-day reconstitution can downgrade some redox and Maillard risks, but high-aw and challenge-test warnings remain for any stored liquid claim.
- **Manufacturing controls**: supplier CoA metal ppm, dextrose form, chelator level, packaging OTR/light barrier, and hold-time instructions become formula inputs rather than afterthoughts.
- **Stats-card integration**: physical chemistry penalties can be generated from rule hits and redox mechanism hits, then displayed as caps/penalties with evidence instead of free-text scoring.

## Risks / unknowns

- A sparse matrix can miss hazards; a broad class rule can over-block benign combinations. Rules need applicability windows and confidence.
- Pairwise rules miss three-way interactions such as ascorbate + Cu + O2 + light unless the rule engine supports mechanism drivers beyond pairs.
- `compat/redox.py` is currently qualitative; turning strings into numbers requires reliable MW, ppm, packaging, pH, oxygen, and hold-time data that may be missing during early design.
- Chelation can reduce free metal without guaranteeing redox inactivity. Reports must state residual risk.
- Redox and Maillard rates are matrix-specific. Screening output cannot support a 6-12 month shelf claim without assays.
- Subagent review found `compat/data.py` overlay loading is `Path.cwd()` sensitive; pairwise/redox upgrades should avoid adding more cwd-sensitive data loading.
- Subagent review found unknown molar masses can undercount osmoles; the same issue would affect redox mole ratios if MWs are missing.

## Validation / audit checklist

- [ ] Matrix schema validates all rule rows and requires provenance/source refs.
- [ ] Known dossier rules are represented: reducing sugar + primary amine, ribose + ascorbate/redox, NAC/thiol + metals/O2, citrate as chelator/protective but not redox-proof, taurine + reducing sugar context, LCLT + calcium/tartrate context.
- [ ] Dry-separated and make-fresh contexts downgrade risks only when hold-time/storage assumptions are explicit.
- [ ] Existing `reformulate.py` ascorbate case still returns moderate redox risk for O2 + clear packaging.
- [ ] Wet NAC + metal/O2 fixture triggers thiol oxidation advisory/block for stored liquid, but dry preload is treated as a storage/packaging issue rather than a wet-shelf block.
- [ ] Supplier CoA metal ppm and formula-added copper/iron convert to molar metal estimates when MW/assay data are present.
- [ ] Missing MW, missing metal ppm, unknown packaging, or unknown hold time produce `unknown`/low-confidence flags, not silent passes.
- [ ] Stats-card shelf/commercial-readiness penalties can cite exact matrix/redox rule IDs.
- [ ] Bench validation list is emitted per mechanism: HPLC ascorbate/DHAA, NAC/disulfide, colorimetry, peroxide value, pH, turbidity/precipitation, microbial/challenge, and real-time/stress stability.

## Affected files

Current evidence surfaces:

- `compat/redox.py`
- `compat/gibbs.py`
- `compat/ph_module.py`
- `compat/water_activity.py`
- `compat/activity.py`
- `compat/data.py`
- `compat_calc.py`
- `reformulate.py`
- `verify_dry_sku.py`
- `calculated-stats-card-v3-upgraded.md`
- `calculated-stats-card-v3-upgraded.json`
- `omx_wiki/substance-*.md` dossiers, especially NAC, ascorbic acid, taurine, citric acid, LCLT, potassium sorbate, ribose.
- `.codex/skills/formula-safety-check/SKILL.md`
- `.codex/skills/gamefowl-formula-stats-card/SKILL.md`

Future implementation touchpoints:

- `substances/compatibility/pairwise-rules.json`
- `substances/compatibility/schema.json`
- `compat/pairwise.py`
- `compat/redox_matrix.py` or expanded `compat/redox.py`
- `compat/report.py` unified evaluator
- stats-card integration code that consumes normalized rule/redox outputs

## Evidence references

- Context snapshot: `/Users/arsapolm/Documents/my-projects/gaiteva/.omx/context/compat-stability-improvement-team-20260618T071451Z.md` lists topics 3 and 5 and the required research/doc constraints.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md:21-31` — Gibbs is backup only; Arrhenius/reactivity are primary practical screens.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md:46-65` — existing package modules and Tier 0/Tier 2 validation boundaries.
- `compat/redox.py:121-331` — ascorbate risk implementation with metal/O2/light/chelation drivers.
- `compat/gibbs.py` — backup screen caveat that thermodynamic spontaneity is not practical reaction rate.
- `calculated-stats-card-v3-upgraded.md:59-71` — wet Maillard/redox, TDS, preservative/challenge, and hydration cap penalties.
- `omx_wiki/substance-nac-n-acetylcysteine.md` — wet/stored NAC oxidation and dry-separation rationale.
- Subagent review probe `019ed997-3455-7883-a98f-1fb55219e01d` — sodium-only ORS caveat, cwd-sensitive overlays, unknown molar mass undercount, qualitative redox limits.
- Subagent change-slice probe `019ed997-4b7c-7f33-b93a-cd81e91d46ce` — safe slices for registry hardening, unified report, use-case dispatch, pairwise matrix, assay-backed shelf-life, aw packaging.
- Subagent KB probe `019ed997-6455-74f3-ab7e-0f96a0be3423` — citation anchors and decision-tree/wiki discoverability gap.
