---
title: "Worker-2 Independent Verifier Synthesis — Higher-Score Formula Outputs"
tags: ["gamefowl", "formula-v31", "formula-v4", "verification", "stats-card-v0.2", "worker-2"]
created: 2026-06-17 Asia/Bangkok
category: research
confidence: medium
---

# Worker-2 Independent Verifier Synthesis — Higher-Score Formula Outputs

## Scope

Independent verifier/synthesis after worker-1 completed the main higher-score formula. I compared:

1. **worker-1 V3.1 Dilution-Labeled Hybrid** from commit `be7f030`.
2. **worker-2 V4 Make-Fresh SGLT1 ORS Hybrid** from task-3.
3. **worker-3 Candidate A dry preload + make-fresh ORS stick** from worker-3 artifacts.

No shared wiki files were edited in this verifier pass; all outputs are under `task-5-artifacts/`.

## Verification summary

| Candidate | Final deliverable | Biological potential | Formulation feasibility | Hydration score | Osmolality | Verdict |
|---|---:|---:|---:|---:|---:|---|
| V3 benchmark | 6.96 | 7.36 | 6.80 | 2.50 | 1309 mOsm/L BLOCK | baseline |
| **worker-1 V3.1 dilution-labeled hybrid** | **7.36** | 7.36 | 8.43 | 6.89 | 114.5 mOsm/L PASS | ✅ verified winner among integrated outputs |
| **worker-2 V4 make-fresh SGLT1 ORS hybrid** | **7.51** | 7.55 | 8.43 | 8.29 | 93.8 mOsm/L PASS | ⚠️ promising but needs external dextrose-profile peer review |
| **worker-3 Candidate A dry preload + ORS stick** | **7.10** | 6.79 | 9.00 | 7.07 | 182.5 mOsm/L PASS | ✅ conservative architecture, lower biological score |

## Main finding

The team conclusion is internally consistent: the first reliable way to beat V3 is fixing the **hydration/osmolality cap**, not claiming a new acute biological effect.

- V3 direct-dose wet core is hypertonic in the calculator and cannot honestly be called a hydration aid when used neat.
- V3.1’s required instruction — **5 mL wet core into at least 40 mL water; dry activator separate unless recalculated** — is the key validated change.
- Worker-3 independently converged on the same principle via dry preload + make-fresh ORS.
- My task-3 V4 adds a make-fresh dextrose/SGLT1 ORS component and scores higher, but because it uses an external calculator profile for dextrose, it should be treated as a **next-candidate probe**, not the already-integrated decision unless another verifier reviews that profile and dose math.

## Recommended leader integration stance

### 1. Publish/keep worker-1 V3.1 as the current integrated decision

Reason: it is the cleanest deterministic winner with existing built-in stats-card profiles and minimal formula disruption.

Required language:

- **GO-CONDITIONAL** for prototype.
- **NO-GO** for neat/direct-dose hydration claims.
- **NO-GO** for stored wet all-in-one ribose/glucose + amines/B6/ascorbate/NAC.
- State explicitly that the score gain is **formulation feasibility / osmolality**, not a new efficacy proof.

### 2. Keep worker-2 V4 as next-candidate / v4 probe

Reason: V4 is numerically strongest (**7.51/10**) and physiologically plausible because dextrose is the SGLT1 hydration carrier, but it adds an external dextrose scoring profile. Before promoting it to the decision page:

- peer-review the dextrose profile;
- fix MgCl2 molar mass/osmolality data in the calculator;
- recalculate the full make-fresh drink if any dry activator is actually dissolved into the same 50 mL water;
- confirm palatability/intake.

### 3. Keep worker-3 Candidate A as conservative fallback architecture

Reason: it has best feasibility (**9.00**) and avoids oil/emulsion risk, but lower biological potential (**6.79**) means it scores below V3.1/V4. It is a strong “commercially simpler / shelf-stable” alternative if the oil emulsion or MCT GI burden fails validation.

## Safety / claim wording verification

Pain-tolerance search across worker-1, worker-2, and worker-3 artifacts found only negated/cautionary wording:

- “No pain-tolerance claim is made.”
- “Do not market as pain tolerance.”
- “Do not claim pain tolerance.”

No positive pain-tolerance claim was found in the reviewed artifacts.

## Formula-safety observations

| Gate issue | Verified status | Integration note |
|---|---|---|
| Osmolality/hydration | V3.1, V4, worker-3 Candidate A all PASS when diluted/make-fresh | Must be label/protocol-enforced; do not hide dry solutes outside calculation |
| Shelf-life | Still conditional | 6 mo plausible after validation; 12 mo unconfirmed |
| Wet all-in-one risk | Still NO-GO | Avoid stored sugar + amines/vitamins/ascorbate/NAC |
| Oil/emulsion | V3.1/V4 retain moderate oil burden | Require emulsion, rancidity/peroxide, viscosity, potency/distribution tests |
| Dry preload/ORS | Worker-3 strongest feasibility | Lower biological score but simpler shelf path |
| MgCl2 osmolality | Calculator undercounts due missing molar mass | Blocking cleanup before final numeric claim precision |

## Verification commands / evidence

Commands run from worker-2 worktree:

```bash
# Extract worker-1 completed artifacts from commit be7f030
git show be7f030:artifacts/calculated-stats-card-higher-score-candidates.json > task-5-artifacts/worker1-calculated.json
git show be7f030:artifacts/higher-score-candidates.json > task-5-artifacts/worker1-candidates.json
git show be7f030:omx_wiki/gamefowl-formula-v31-dilution-hybrid-higher-score-after-stats-v02.md > task-5-artifacts/worker1-v31-wiki.md

# Copy worker-3 completed artifacts
cp ../worker-3/worker-3-low-osmolality-support-findings.md task-5-artifacts/worker3-findings.md
cp ../worker-3/worker-3-candidate-a-calculated-card.json task-5-artifacts/worker3-candidate-a.json

# Assertions: scores beat V3, osmolality gates pass, pain-tolerance wording only negated/cautionary
python - <<'PY'
import json, re, pathlib
w1=json.load(open('task-5-artifacts/worker1-calculated.json'))
w2=json.load(open('task-3-artifacts/v4-ors-card.json'))
w3=json.load(open('task-5-artifacts/worker3-candidate-a.json'))
assert w1[0]['overall']==6.96
for label, r in [('worker1 V3.1', w1[1]), ('worker2 V4', w2[1]), ('worker3 Candidate A', w3[1])]:
    assert r['overall'] > 6.96, (label, r['overall'])
    assert r['physical']['osmolality']['ors_gate']['verdict'] == 'PASS', label
for p in ['task-5-artifacts/worker1-v31-wiki.md','task-3-artifacts/worker-2-low-osmolality-formula-probe.md','task-5-artifacts/worker3-findings.md']:
    text=pathlib.Path(p).read_text().lower()
    for m in re.finditer(r'.{0,70}pain[- ]tolerance.{0,70}', text):
        s=m.group(0)
        assert any(x in s for x in ['no ', 'not ', 'do not', 'without']), (p, s)
print('ASSERTIONS_OK')
PY
```

Observed output:

```text
ASSERTIONS_OK
('worker1 V3.1', 7.36, 7.36, 8.43, 6.89, 114.50035102920853, 'PASS')
('worker2 V4', 7.51, 7.55, 8.43, 8.29, 93.82008582599391, 'PASS')
('worker3 Candidate A', 7.1, 6.79, 9.0, 7.07, 182.5005347834409, 'PASS')
```

## Final verifier verdict

**CONFIRMED with caveats:** worker-1 V3.1 legitimately beats V3 under stats-card v0.2 by correcting delivery/osmolality while preserving shelf architecture. It is the right integrated answer today.

**CORRECTIVE NOTE:** if the dry activator is ever mixed into the same hydration water, the osmolality must be recalculated; current V3.1 score assumes the dry activator remains separate.

**NEXT BEST UPGRADE:** worker-2 V4 make-fresh dextrose/SGLT1 ORS hybrid is worth a follow-up verifier pass because it scores **7.51/10**, but do not promote it without peer-reviewing the external dextrose profile and fixing MgCl2 osmolality data.
