# Compat/Stability Decision Tree — Formula Actions by Product Class

## Current repo state

The calculator currently exists as pure `compat/` modules plus script fixtures. `compat_calc.py` is the failing wet-drench contrast, `reformulate.py` is the passing ORS contrast, and `verify_dry_sku.py` proves dry products are not subject to standing-solution osmolality until reconstituted. The prior explainer is `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md`; this page mirrors the decision logic into `omx_wiki/` for easier use.

## How the improvement works

Use product class before interpreting gates:

1. **Hydration drink / reconstituted ORS**: run dissolved-fraction osmolarity first; require volume-aware Na/K/Cl/glucose evidence; block hypertonic or electrolyte-incomplete drinks before chemistry levers.
2. **Dry capsule or dry preload**: skip standing-solution osmolality; evaluate hygroscopicity, water activity/moisture protection, caking, segregation, dose uniformity, and route/timing evidence.
3. **Dry stick mixed into water**: evaluate dry storage first, then run hydration-drink gates at labeled reconstitution volume and hold time.
4. **Wet concentrate / emulsion**: evaluate bottle concentration for solubility, redox, aw, preservative challenge, emulsion separation, and then evaluate use dilution separately.
5. **Acute sublingual / oral-mucosal exposure**: do not reuse hydration-drink thresholds blindly; evaluate mucosal tolerance, pH, osmotic load, dose, contact time, and GI spillover separately.

## How it affects formula design decisions

The decision tree prevents two common errors: falsely blocking dry products because an active is insoluble in a hypothetical bottle, and falsely approving wet hydration claims because actives dissolve while osmolality/electrolytes fail. It supports split SKU designs, same-day mixing labels, and manufacturing controls such as dextrose monohydrate specification.

## Risks / unknowns

- Current ORS completeness is too weak (`complete_ors` is sodium-only), so Na/K/Cl/glucose ratio work remains needed.
- Registry overlays are cwd-sensitive; constants can drift or disappear outside repo-root execution.
- Unknown molar masses can undercount osmoles and should reduce confidence or block hydration claims.
- Redox, aw, and Arrhenius are screening tools; wet shelf claims still need assays and challenge/real-time studies.
- Route-specific thresholds for gamefowl mucosal tolerance require field/bench validation.

## Validation checklist

- [ ] `compat_calc.py` remains a wet-drench NO-GO contrast (~1542 mOsm/L BLOCK). 
- [ ] `reformulate.py` remains a passing ORS contrast (~274 mOsm/L PASS). 
- [ ] `verify_dry_sku.py` keeps dry products exempt and reconstituted drink ~291 mOsm/L PASS. 
- [ ] Future report API includes product class, route, volume, hold time, and storage state.
- [ ] Any use-case profile has explicit blocking vs advisory gates and required validation evidence.

## Affected files

- `compat/osmolality.py`, `compat/solubility.py`, `compat/redox.py`, `compat/water_activity.py`, `compat/ph_module.py`, `compat/arrhenius.py`
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py`
- `calculated-stats-card-v3-upgraded.*`
- `substances/physical/*.json`
- Future: `compat/profiles.py`, `compat/report.py`, `compat/schema.py`

## Evidence references

- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md:33-87` for gate order and known findings.
- `verify_dry_sku.py` output captured by worker-3: dry Products 1/2 no standing-solution osmolality; Product 3 drink 291 mOsm/L PASS.
- `reformulate.py` output captured by worker-3: 274 mOsm/L PASS with Na 74.1/K 20.1/Cl 64.6.
- Review subagent `019ed997-3455-7883-a98f-1fb55219e01d` for edge cases and validation gaps.
