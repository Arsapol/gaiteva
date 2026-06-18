---
title: Stats-card provenance registry upgrade 2026-06-17
category: implementation
tags: [stats-card, provenance, registry, source-refs, formula-calculator]
date: 2026-06-17
---

# Stats-card provenance registry upgrade — 2026-06-17

## Decision
All reviewed/verified stats-card records must carry field-level provenance, not only a general wiki dossier link.

## Implemented files
- `.codex/skills/gamefowl-formula-stats-card/scripts/audit_provenance.py`
- `.codex/skills/gamefowl-formula-stats-card/references/substance-profile-template.json`
- `.codex/skills/gamefowl-formula-stats-card/references/physical-profile-template.json`
- `.codex/skills/gamefowl-formula-stats-card/scripts/onboard_substances.py`
- `.codex/skills/gamefowl-formula-stats-card/registry/effects/default-effects.json`
- `.codex/skills/gamefowl-formula-stats-card/registry/physical/default-physical.json`
- `substances/physical/default-compat-physical.json`
- `substances/physical/magnesium_chloride_hexahydrate.json`

## Schema rule
Effect records now use:
- `sources[]` — source IDs and paths/URLs
- `source_refs.ref`
- `source_refs.evidence`
- `source_refs.effects.<metric>` for each non-zero metric
- `source_refs.chronic_only`
- `source_refs.wet_reactive_class` when present
- `source_refs.notes`

Physical records now use:
- `sources[]`
- `source_refs.formula`
- `source_refs.molar_mass_g_per_mol`
- `source_refs.osmotic_n`
- `source_refs.solubility_g_per_100ml_25c`
- `source_refs.density_kg_m3` / `source_refs.pka` when present
- `source_refs.ions_mmol_per_g.<ion>`
- `source_refs.note`

## Source-id meanings
- `wiki:substance-*` = cited project dossier under `omx_wiki/`
- `rubric:stats-card-v0.2` = expert scoring/rubric judgement, not a published constant
- `osmotic-model:screening-v0.2` = ideal dissociation particle-count assumption for osmolality screening
- `calc:ion-stoichiometry-from-mw` = ion mmol/g calculated from molecular weight and stoichiometry
- `compat:data.py:2026-06-17` = legacy compat constant copied into data-driven registry for audit coverage

## Validation evidence
Command:

```bash
python .codex/skills/gamefowl-formula-stats-card/scripts/audit_provenance.py --project-root .
```

Result:

```text
PROVENANCE AUDIT PASS: 17 effect records, 23 physical records, 22 compat keys covered
```

Calculator regression check on built-in presets:
- Route A Wet Core: score 5.12, osmolality 2646.3 mOsm/L, BLOCK
- V3 Hybrid Core Emulsion + Dry Activator: score 6.96, osmolality 1477.2 mOsm/L, BLOCK

## Remaining limitation
The provenance refs now point beside each field, but many fields still point to dossier-level refs instead of exact DOI/PMID per property. Next refinement: promote exact DOI/PMID/PubChem/USP/manufacturer IDs from each dossier into the `sources[]` list for every property where practical.

## Project-scope correction
2026-06-17: Moved formula-specific skills from user/global scope into this repository:

- `.codex/skills/gamefowl-formula-stats-card/`
- `.codex/skills/formula-safety-check/`
- `.codex/skills/formula-redesign/`

Archived old global copies under `~/.codex/skills-archive/gaiteva-project-scoped-20260617/` so they no longer appear as global reusable skills.
