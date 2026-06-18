# Topics 1+10 — Unified `compat.evaluate_formula(...)` API/report + normalized scoring

Date: 2026-06-18  
Worker: `worker-1`  
Scope: research/documentation only; no formula or calculator code changed.

## Executive recommendation

Create one public compatibility entry point, tentatively `compat.evaluate_formula(...)`, that calls the existing focused modules and returns a machine-readable report with normalized severities and score impacts. Then make the stats-card consume this report instead of re-encoding physical gates in its own private scoring logic.

The key change is not a new chemistry equation; it is a contract: every formula review should expose the same blocker/warning/advisory structure, the same applicability labels, the same evidence/provenance fields, and the same compatibility/stability/commercial-readiness scores. This would make formula tradeoffs auditable across liquid ORS, acute sublingual/drench, dry capsule, dry premix, wet concentrate, and split-SKU designs.

## Current repo state

### Compatibility calculator

Current `compat/` is a set of pure, focused modules rather than a unified evaluator.

| Current path | Current role | Notes for unified API |
|---|---|---|
| `compat/osmolality.py` | Osmolarity + ORS/electrolyte gate | Already returns structured `osmolality_report(...)` with `ors_gate`, `electrolyte_balance`, and `blocking`. It is the strongest template for a normalized gate object. |
| `compat/solubility.py` | Solubility, TDS, bottlenecks, supersaturation warnings | Returns structured `additive_report(...)`; needs normalized severity for bottlenecks vs advisory crystallization risk. |
| `compat/ph_module.py` | pH window and pH-linked degradation heuristics | Useful as a stability gate, but does not yet report buffer capacity or dilution drift. |
| `compat/arrhenius.py` | Per-pathway Q10 / acceleration-factor projection | Provides pathway projections but not a formula-level shelf-life verdict. |
| `compat/redox.py` | Ascorbate metal/O2/light risk | Tier-0 advisory; should feed shelf score and validation checklist. |
| `compat/activity.py` | Ionic strength and Setschenow correction | Advisory/uncertainty layer; should not silently hard-block without validity notes. |
| `compat/water_activity.py` | Water activity and microbial-risk screen | Important commercial-readiness gate for wet products. |
| `compat/stokes.py` | Settling for undissolved fraction | Applicability-gated: only meaningful when particles remain undissolved. |
| `compat/gibbs.py` | Backup thermodynamic screen | Explicitly backup-only; should be labeled non-primary in unified output. |
| `compat/data.py` and `substances/physical/*.json` | Constants/profiles/provenance | Need stable IDs and source references in report output. |

`compat_calc.py` is currently a demo orchestrator, not a reusable API. It prints an applicability header, runs osmolality first, then solubility, pH, Arrhenius, Stokes, and Gibbs, and ends with a narrative overall verdict. This proves the sequence but does not expose a reusable object for downstream tooling.

`reformulate.py` and `verify_dry_sku.py` demonstrate product-state-specific interpretation: the passing liquid ORS is about 274 mOsm/L with complete Na/K/Cl; the dry SKU treats capsules/premix as dry products and only applies standing-solution osmolality to the reconstituted drink, which calculates about 291 mOsm/L with complete ORS.

### Stats-card integration

The stats-card calculator already imports project `compat` modules, but it does so through private helper functions in `.codex/skills/gamefowl-formula-stats-card/scripts/calculated_stats_card.py`:

- `solubility_analysis(...)` calls `compat.solubility.additive_report(...)`, converts bottlenecks/TDS/unknown profiles into a `solubility_score`, and reduces ingredient contribution when solution-phase delivery is insoluble.
- `osmolality_analysis(...)` calls `compat.osmolality.osmolality_report(...)`, converts `PASS/MARGINAL/BLOCK` plus ORS completeness into `osmolality_score` and `hydration_cap`.
- `physical_scores(...)` combines solubility, osmolality, oil/emulsion burden, wet-reactivity classes, preservative challenge, and shelf penalties into GI and shelf/commercial-readiness scores.
- Output files such as `calculated-stats-card-v3-upgraded.md/json` already show layer reporting: biological potential, formulation feasibility, final deliverable average, physical gate notes, confidence, and a penalty/cap ledger.

Current gap: stats-card is the only place where normalized numeric physical scores are assembled. `compat/` itself cannot yet produce the same combined, auditable compatibility/stability/readiness score for non-stats-card consumers.

## Proposed `compat.evaluate_formula(...)` contract

### Suggested function signature

```python
def evaluate_formula(
    components: list[dict] | list[tuple[str, float]],
    *,
    product_type: str,
    water_ml: float | None = None,
    delivered_water_ml: float | None = None,
    phase_map: dict[str, str] | None = None,
    target_ph: float | None = None,
    storage: dict | None = None,
    use_case: str = "oral_hydration",
    evidence_level: str = "screening",
) -> dict:
    """Return normalized compatibility/stability/readiness report."""
```

`product_type` should drive applicability before scoring, with an enum such as:

- `hydration_drink` / reconstituted ORS
- `acute_sublingual_or_drench`
- `dry_capsule`
- `dry_premix`
- `wet_concentrate`
- `wet_core_plus_dry_activator`

### Suggested top-level return shape

```json
{
  "schema_version": "compat-eval-v0.1",
  "formula_id": "optional-name-or-hash",
  "product_type": "hydration_drink",
  "registry_snapshot": "compat-data-plus-physical-overlays@<hash-or-date>",
  "applicability": {
    "standing_solution": true,
    "hydration_claim": true,
    "dry_ingestion": false,
    "notes": ["osmolality gate applies at delivered concentration"]
  },
  "overall": {
    "verdict": "PASS|MARGINAL|BLOCK|INSUFFICIENT_DATA",
    "blocking": false,
    "score_0_10": 8.2,
    "confidence": "High|Medium|Low",
    "summary": "short human-readable conclusion"
  },
  "scores": {
    "compatibility": 0.0,
    "stability": 0.0,
    "commercial_readiness": 0.0,
    "hydration_cap": 0.0,
    "stats_card_adjustments": []
  },
  "findings": [],
  "gates": {},
  "unknowns": [],
  "validation_checklist": [],
  "provenance": []
}
```

### Normalized finding object

Every module should emit findings using the same object shape:

```json
{
  "id": "osmolality.hypertonic",
  "module": "compat.osmolality",
  "severity": "BLOCKER|WARNING|ADVISORY|INFO|INSUFFICIENT_DATA",
  "applies": true,
  "metric": "hydration|solubility|shelf|gi|commercial_readiness",
  "score_delta": -2.5,
  "cap": {"metric": "hydration", "max_score": 2.5},
  "message": "1542 mOsm/L > 350 mOsm/L hypertonic gate",
  "evidence": {
    "value": 1542,
    "unit": "mOsm/L",
    "threshold": 350,
    "source": "compat.osmolality.HYPERTONIC_GATE"
  },
  "next_action": "dilute, cut osmotic load, or move actives to dry SKU"
}
```

### Gate normalization

Recommended severity mapping:

| Severity | Meaning | Formula-design consequence | Stats-card consequence |
|---|---|---|---|
| `BLOCKER` | Product cannot support the stated claim/use case without redesign. | Stop and redesign before optimizing efficacy. | Cap affected metric; lower feasibility; surface in overall verdict. |
| `WARNING` | Material risk that can be mitigated by product architecture or validation. | Prefer split SKU, make-fresh, lower concentration, packaging, or bench assay. | Penalize shelf/GI/feasibility; lower confidence. |
| `ADVISORY` | Relevant but not decisive at screening level. | Add to label/process/testing checklist. | Small penalty or no numeric change; add validation item. |
| `INFO` | Applicability, assumption, or pass evidence. | Audit trace. | No penalty. |
| `INSUFFICIENT_DATA` | Missing physical/effect constants or unvalidated assay input. | Do not claim a pass; gather data or create reviewed profile. | Conservative score and low confidence. |


### Product-mode decision matrix

| Product mode | What the unified report should gate | What it must not do | Design consequence |
|---|---|---|---|
| Hydration drink / reconstituted ORS | Delivered-concentration osmolality, Na/K/Cl completeness, glucose:Na cotransport logic, solubility, aw if stored wet. | Do not use oral-mucosal tolerance data to justify a swallowed hydration drink. | Keep low-osmolality Na/K/Cl path; move high-osmotic or insoluble actives out. |
| Acute sublingual / oral-mucosal drench | Mucosal tolerance, pH, irritancy, bolus volume, short contact time, solubility/suspension behavior. | Do not classify 900-1000 mOsm/L mucosal-tolerated boluses as ORS/hydration products. | Separate fast acute delivery from hydration claims. |
| Dry capsule / dry preload premix | Dry stability, hygroscopicity, caking, dose uniformity, ingredient safety. | Do not apply standing-solution osmolality unless the product is reconstituted. | Dry-first can preserve focus/preload actives without failing liquid gates. |
| Wet concentrate | In-bottle solubility/TDS, aw/preservation, redox, pH drift, dilution instructions, delivered-use osmolality. | Do not evaluate only in-bottle or only delivered state; both matter. | Label dilution and make-fresh constraints; commercial readiness depends on validation. |
| Wet core + dry activator | Wet-core shelf/emulsion/preservation plus dry-activator stability and delivered-use instructions. | Do not dissolve dry activator into hydration water unless the intended product mode says so. | Keeps biological potential while preventing wet incompatibilities from dominating shelf/readiness. |

Recommended score mapping for initial implementation:

| Gate family | Primary outputs today | Proposed normalized score/cap |
|---|---|---|
| Osmolality/ORS | `PASS`, `MARGINAL`, `BLOCK`, `complete_ors` | PASS complete ORS: hydration cap 10, score 9; MARGINAL complete ORS: cap 7.5, score 7; BLOCK or no sodium: cap 2.5-4 depending severity, matching existing stats-card behavior. |
| Solubility/TDS | bottlenecks, dissolved fraction, TDS >20%, supersaturation | Full dissolve: 10; unknown solution profile: 4 + low confidence; bottleneck: cap by worst dissolved fraction; salting-out: cap 7; supersaturation: cap 8. |
| pH/buffer | pH window, degradation-vs-pH | In target window: pass/info; outside: warning or blocker depending storage/use; missing buffer capacity: unknown/warning. |
| Arrhenius | pathway projections and ICH warnings | Convert low-Ea/unknown stress-assay gaps into shelf-validation warnings, not false precision. |
| Redox | risk level, drivers, mitigations | Moderate/high ascorbate-metal-O2-light risk penalizes shelf and adds packaging/headspace/metal testing. |
| Water activity | aw class and preservation flag | Wet high-aw products require preservative/challenge-test blocker for commercial shelf claims; make-fresh can be warning/advisory. |
| Stokes | applicable only if undissolved | Settling warning if undissolved fraction exists; N/A info if fully dissolved/dry. |
| Gibbs | backup spontaneity screen | Advisory only unless external reactivity matrix also flags the pair. |

## How this affects formula design decisions

A unified report would make formula-design tradeoffs earlier and less subjective:

1. **Use-case first.** A hydration drink must pass osmolality and Na/glucose/electrolyte logic before focus or ATP ingredients matter. Dry capsules and dry premixes should not be incorrectly penalized by standing-solution osmolality.
2. **Architecture choice becomes explicit.** If a wet bottle scores high biologically but fails shelf or osmolality, the report should point to split SKU, make-fresh drink, or dry activator rather than incremental dose tweaks.
3. **Blockers outrank benefits.** Hypertonic ORS, missing sodium, insoluble actives in the claimed solution phase, or high-aw shelf claims should cap affected stats-card metrics even if ingredient evidence is strong.
4. **Commercial readiness separates from acute efficacy.** A formula can be plausible acutely but not commercially ready if high-aw liquid, wet ribose/amine/vitamin chemistry, oxygen/light exposure, emulsion separation, or preservative challenge remain unvalidated.
5. **Comparison across formulas improves.** The same compatibility/stability/readiness sub-scores can explain why Route A Wet Core scored lower than V3 Hybrid and why the verified dry-stick drink passes as a reconstituted solution.
6. **Unknown constants stop silent optimism.** Missing molar mass, solubility, pKa, ion stoichiometry, redox, or aw data should appear as `INSUFFICIENT_DATA`, lowering confidence until the physical registry/provenance is filled.

## Risks and unknowns

- **False precision risk:** A single 0-10 compatibility number can hide mechanism-specific uncertainty. Keep sub-scores and findings visible; do not rely only on aggregate score.
- **Applicability mistakes:** Applying osmolality to dry capsules or ignoring delivered dilution for concentrates can produce wrong decisions. Product-type/applicability must be first-class.
- **Stats-card double counting:** If stats-card consumes `compat.evaluate_formula(...)`, remove or clearly bypass duplicated private gates to avoid applying the same penalty twice.
- **Validation burden:** Shelf-life/commercial readiness cannot be proven by calculation alone. Stress assays, real-time stability, microbial/challenge testing, and packaging data remain required for label claims.
- **Threshold governance:** Initial thresholds can mirror current code, but changes to ORS bands, TDS caps, aw classes, redox cutoffs, and shelf penalties need versioning and golden fixtures.
- **Schema migration:** Existing JSON/Markdown reports and scripts expect current stats-card shapes. A compatibility adapter may be needed before replacing current helpers.
- **Evidence provenance:** Some constants come from dossier-level references; future work should promote exact DOI/PMID/PubChem/USP/manufacturer IDs per field where practical.
- **Registry reproducibility:** The stats-card script can load runtime physical registry overlays into `compat.data`; a unified report should stamp the registry snapshot/version to avoid invisible drift.
- **Scope promotion risk:** `gibbs`, `stokes`, and `arrhenius` have deliberately narrow applicability; the unified report must not promote them to equal-weight universal gates.

## Validation and audit checklist

For any future implementation of this research recommendation:

- [ ] Add golden fixtures for the known failing `compat_calc.py` drench: hypertonic/no-electrolyte blocker, tyrosine/creatine bottlenecks, and overall no-go.
- [ ] Add golden fixture for `reformulate.py`: about 274 mOsm/L, Na about 74 mmol/L, K about 20 mmol/L, Cl about 65 mmol/L, complete ORS, no bottlenecks.
- [ ] Add golden fixture for `verify_dry_sku.py`: dry capsule/premix osmolality not applicable; reconstituted drink about 291 mOsm/L, complete ORS, no bottlenecks.
- [ ] Add stats-card regression asserting current Route A and V3 scores/caps do not change unless migration intentionally changes rubric version.
- [ ] Validate schema stability: every finding has `id`, `module`, `severity`, `applies`, `message`, evidence, and next action.
- [ ] Validate applicability matrix by product type: hydration drink, acute drench/sublingual, dry capsule, dry premix, wet concentrate, split SKU.
- [ ] Validate unknown constants: missing molar mass/solubility must produce `INSUFFICIENT_DATA` and conservative score/confidence, not silent pass.
- [ ] Validate dry/powder/oil phases still bypass aqueous solubility/osmolality gating unless explicitly labeled `drink`, `make_fresh`, or `solution`.
- [ ] Validate score ledger: every cap/penalty in the normalized score appears in a penalty/cap ledger compatible with stats-card Markdown output.
- [ ] Validate draft/rejected/unreviewed profiles still contribute zero benefit points and appear as unknown/unavailable, matching the current stats-card guardrail.
- [ ] Run provenance audit for any added physical constants/profile overlays.
- [ ] Keep a machine-readable schema version such as `compat-eval-v0.1` and a human-readable Markdown summary generated from the same JSON.

## Affected files if implemented later

Research-only deliverables in this task:

- `artifacts/compat-improvement-research-20260618/topics-01-10-unified-api-scoring.md`
- `omx_wiki/research-compat-improvement-unified-api-scoring-2026-06-18.md`

Likely future implementation touchpoints, not changed here:

- `compat/__init__.py` — export `evaluate_formula` or a report dataclass/schema.
- `compat/evaluator.py` or `compat/report.py` — new unified orchestrator.
- `compat/osmolality.py`, `compat/solubility.py`, `compat/ph_module.py`, `compat/arrhenius.py`, `compat/redox.py`, `compat/activity.py`, `compat/water_activity.py`, `compat/stokes.py`, `compat/gibbs.py` — adapt module outputs into normalized findings.
- `compat_calc.py`, `reformulate.py`, `verify_dry_sku.py` — optionally switch demos to call `evaluate_formula(...)` while preserving current printed educational output.
- `.codex/skills/gamefowl-formula-stats-card/scripts/calculated_stats_card.py` — consume normalized compat report instead of duplicating solubility/osmolality/shelf scoring logic.
- `.codex/skills/gamefowl-formula-stats-card/references/rubric.md` — document how normalized compat scores feed hydration/GI/shelf/commercial-readiness metrics.
- `substances/physical/*.json` and `.codex/skills/gamefowl-formula-stats-card/registry/physical/*.json` — keep physical constants/provenance aligned.
- Future tests, likely under a new `tests/` tree or module-level golden-fixture scripts.

## Evidence references

Repo evidence inspected:

- Context snapshot: `/Users/arsapolm/Documents/my-projects/gaiteva/.omx/context/compat-stability-improvement-team-20260618T071451Z.md`.
- `compat/__init__.py` states public functions are pure and module-scoped; no unified API is exported.
- `compat/osmolality.py` documents the blocking ORS/electrolyte gate and returns `osmolality_report(...)` with `blocking`.
- `compat/solubility.py` returns `additive_report(...)` with TDS, bottlenecks, and supersaturation warnings.
- `compat_calc.py` sequences existing levers but only prints a demo report.
- `reformulate.py` demonstrates a passing ORS design at about 274 mOsm/L with complete electrolytes.
- `verify_dry_sku.py` demonstrates product-state applicability and a passing reconstituted dry-stick drink at about 291 mOsm/L.
- `.codex/skills/gamefowl-formula-stats-card/scripts/calculated_stats_card.py` currently embeds the physical gate-to-score conversion.
- `calculated-stats-card-v3-upgraded.md/json` show current final deliverable scoring, physical gate notes, hydration caps, shelf penalties, and penalty/cap ledger.
- `artifacts/higher-score-20260617/calculated-stats-card-v31-recalc-20260617.md/json` show a later normalized scorecard where dilution and split-SKU handling improve hydration/formulation feasibility.
- `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md` is the prior reference page for the existing calculator.
- `omx_wiki/gamefowl-formula-v31-dilution-hybrid-higher-score-after-stats-v02.md` documents the score/design impact of fixing hydration/osmolality through dilution and dry-activator separation.
- `omx_wiki/stats-card-provenance-registry-upgrade-2026-06-17.md` documents field-level provenance and physical registry overlay expectations.
- `omx_wiki/field-osmolality-900-1000-ph58-65-oral-mucosal-tolerance.md` separates acute oral-mucosal tolerance observations from swallowed hydration/ORS classification; this supports the product-mode decision matrix.

## Subagent findings integrated

- Evidence-map probe (`019ed997-e7ac-7f41-b8fc-d91a703d72fc`) identified exact evidence paths for gate order, product-state applicability, physical registry provenance, V3.1 scorecard artifacts, and stats-card provenance KB.
- Review/risk probe (`019ed997-e376-7a81-b657-df937eb1e5e9`) reinforced contract risks: do not average away blockers, do not false-block dry SKUs, preserve `unknown_molar_mass`/`unknown_physical`, keep `gibbs` backup-only, avoid hidden registry overlay drift, and preserve current stats-card guardrails.
- Architecture/migration probe (`019ed997-e570-7f20-98c3-33a1f40b8c04`) added the implementation-slice framing now reflected above: keep pure module APIs intact, add a separate report-spec layer, add a product-mode decision matrix, preserve raw/potential/final score layers, stamp registry overlay provenance, and avoid route confusion between hydration ORS and acute oral-mucosal tolerance.

## Coordination notes

Coordination protocol: coordinated - task boundary checked against leader assignment, artifact paths, wiki path, stats-card downstream contract, and no-code-change constraint.
