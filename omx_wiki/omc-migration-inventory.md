# OMC to OMX Migration Inventory

Category: reference  
Tags: omc, omx, migration, project-memory, gamefowl, formula-vnext2

## Migration date

2026-06-16

## What was migrated into OMX wiki

The old OMC wiki knowledge pages from `.omc/wiki/*.md` were copied into `omx_wiki/`, excluding OMC runtime/generated index/log/session-log files.

Migrated content includes:

- Gamefowl supplement avian-grounded evaluation pages
- vNext / vNext2 gamefowl formula redesign decision pages
- Competitor product notes
- Standardized vNext2 formulas
- Substance dossiers for amino acids, electrolytes, vitamins, sugars, preservatives, and related ingredients

The OMX wiki index was refreshed after migration.

## What was preserved as artifacts, not wiki pages

Detailed OMC non-wiki artifacts were copied to:

`./.omx/artifacts/omc-migration-2026-06-16/`

Included:

- `formula-vnext2/` — detailed vNext2 deliverables, gate table, open items, blocking gaps, dossiers, JSON scoring/metadata
- `ask/` — old external advisor / Codex consult artifact(s)

These are preserved for retrieval, but not promoted wholesale into curated wiki pages.

## What was not migrated

The following OMC runtime files were intentionally left in `.omc/` only:

- `.omc/state/`
- `.omc/sessions/`
- `.omc/state/checkpoints/`
- `.omc/state/skill-sessions.json`
- HUD/cache/session replay files

Reason: these are Claude/OMC runtime state, not directly useful to OMX. Keep them only as backup unless a specific old transcript/checkpoint is needed.

## Current recommendation

- Use `omx_wiki/` as the active project knowledge base.
- Keep `.omc/` temporarily as an archive.
- Do not commit `.omc/state`, `.omc/sessions`, or other runtime files.
- If cleaning later, archive `.omc/` outside the repo after confirming the migrated wiki and `.omx/artifacts/omc-migration-2026-06-16/` are enough.

## Known migration health notes

`omx wiki_lint` reports many broken wiki links because old OMC pages used shorter alias-style links such as `substance-dextrose.md`, while actual migrated filenames are longer slug names such as `substance-dextrose-d-glucose.md`.

This does not mean content is missing; it means link aliases need a cleanup pass if perfect wiki navigation is required.
