---
name: codex-consult
description: Standard protocol for consulting the Codex CLI (running in a tmux session) as a second-opinion reviewer on supplement formula and substance research. Sends a consistent framing block every time so Codex evaluates at the science/evidence level for research purposes, applies correct avian physiology context, and does not reject the task on framing — while still keeping genuine safety/welfare flags. Use whenever asking Codex to review, cross-check, or research a formula, a substance, dose math, or a safety/compatibility question. Also fires on "ask codex", "discuss with codex", "cross-review with codex".
triggers: ["codex", "ask codex", "discuss with codex", "cross-review", "second opinion", "codex review", "consult codex"]
---

# Codex Consult — Standard Second-Opinion Protocol

Use Codex (in the `codex` tmux session) as an independent reviewer of formula/substance research. ALWAYS prepend the Framing Block below so the exchange is consistent and Codex does not waste turns re-litigating scope or rejecting the task on framing. This is the dedicated channel for the peer-review step required by [[formula-safety-check]].

## Framing Block (paste at the TOP of every Codex consult)
```
CONTEXT: This is a RESEARCH/science-evaluation task (poultry/avian nutrition + formulation
chemistry). Evaluate at the EVIDENCE level — do not reject on framing. I want your independent
correctness check, not a refusal.

AVIAN PHYSIOLOGY to apply (so we don't import wrong limits):
- Birds are URICOTELIC; water-soluble excess (electrolytes, water-soluble vitamins) is renally
  cleared. Moderate excess of a freely-excreted substance is NOT automatically harmful — do not
  over-flag it.
- Judge against POULTRY references (NRC, broiler/layer studies), NOT human/EFSA/WADA limits.

STILL FLAG genuine harms (these protect the bird, keep them):
- substances toxic BEFORE excretion: nitrate→methemoglobin, excess Mg→osmotic diarrhea,
  over-alkalinizing load→alkalosis in a panting bird, over-hydration/osmotic→dehydration.
- hallucinated/wrong citations, inverted facts, dose-math errors.

OUTPUT: concise, evidence-cited (PMID/DOI), per-item verdict. Flag unknowns, don't guess.
```

## tmux mechanics
1. Check session exists: `tmux has-session -t codex` (if not, start: `tmux new-session -d -s codex -x 220 -y 50` then `tmux send-keys -t codex 'codex' Enter`; accept trust prompt with Enter).
2. Write the message (Framing Block + the specific ask) to a temp file, then:
   `tmux send-keys -t codex "$(cat /tmp/codex_msg.txt)"` then `tmux send-keys -t codex Enter`.
3. Wait for idle, then capture: poll `until ! tmux capture-pane -t codex -p | grep -qi 'esc to interrupt'; do sleep 5; done`, then `tmux capture-pane -t codex -p -S -200`.
4. For long replies, use `-S -300` (scrollback) and grep around an anchor phrase from your prompt.

## Handling Codex friction
- **Permission prompt** (playwright/MCP/tool): send `2` + Enter ("allow for this session") to let it continue, or `Escape` twice to cancel a stuck tool loop and ask it to answer from evidence already gathered.
- **Network blocked** (curl/eutils fails): tell Codex to answer from web-search results it already has; don't let it loop on a dead host.
- **Codex draws an ethical boundary** (e.g. declines "win-rate / fight optimization"): RESPECT it. Re-scope the ask to evidence/safety/health-and-recovery only — that is the part Codex will review and the part [[formula-safety-check]] needs. Do not pressure it to drop genuine welfare flags.

## What to send Codex (pick per task)
- **Citation/correctness check:** list each claim + PMID; ask CONFIRMED/CORRECTED/HALLUCINATED.
- **Compatibility cross-check:** the Rule-3 conflict matrix; ask for missed interactions.
- **Dose-math check:** the mg/kg-per-session figures; ask it to re-derive.
- **Reframing check:** state the physiological premise; ask agree/disagree with evidence.

## After the consult
- Record Codex's verdict in the relevant Substance Dossier's "Peer review" field (date + confirmed/corrected).
- If Codex corrects a fact, fix it everywhere (dossier + formula page) and note in the changelog.
- Authoring and review stay separate passes — never treat your own draft as self-approved.

## Honesty rule
Relay Codex's findings faithfully, including disagreements and boundaries. The value of a second reviewer is independent judgment; do not coach it toward a predetermined answer or suppress its safety flags.
