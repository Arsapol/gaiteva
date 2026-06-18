---
title: "Research: Compat improvement topics 4+8 — physical registry cleanup + golden tests"
tags: ["compat-calculator", "physical-registry", "golden-fixtures", "pytest", "formula-design", "research", "gamefowl"]
created: 2026-06-18T07:18:00Z
updated: 2026-06-18T07:18:00Z
category: reference
confidence: medium
schemaVersion: 1
links:
  - "stats-card-provenance-registry-upgrade-2026-06-17.md"
  - "formulation-compatibility-stability-calculator-compat-osmolality.md"
---

# Research: Compat improvement topics 4+8 — physical registry cleanup + golden tests

This wiki-ready page summarizes the task artifact at `artifacts/compat-improvement-research-20260618/topics-04-08-registry-tests.md`.

## Recommendation

Make `substances/physical/*.json` the canonical source for physical constants used by `compat/`, harden the loader/audit contract, and add pytest golden fixtures for the three known calculator outcomes:

- original liquid drench: `1542 mOsm/L -> BLOCK`;
- reformulated liquid ORS: `274 mOsm/L -> PASS`;
- fight-day drink in 1 L: `291 mOsm/L -> PASS`.

## Current repo state

- `compat/data.py` still carries hardcoded `SUBSTANCES`, `MOLAR_MASS_G_PER_MOL`, `OSMOTIC_N`, `ELECTROLYTE_IONS`, and Arrhenius constants.
- `compat/data.py` also imports `substances/physical/*.json` overlays at import time using current working directory lookup; this can change results by launch directory if not hardened.
- `substances/physical/default-compat-physical.json` already contains richer provenance-backed records and should become the source of truth.
- Adjacent scripts `concentrate.py` and `prep_sheet.py` should be covered by fixture-backed recipe/report tests where they depend on compatibility math.
- No `tests/` or golden fixture suite exists yet.

## How the improvement works

Define a canonical physical-record schema for `substances/physical/*.json`, load reviewed/verified records through an explicit repo-root-aware loader, audit drift against the legacy `compat/data.py` constants during migration, and protect known calculator outcomes with pytest golden fixtures. The fixtures should assert osmolality, ORS verdict, Na/K/Cl mmol/L, bottleneck counts, registry-status handling, hydrate/salt identity, and dry-vs-wet use-case behavior.

## Formula-design impact

Golden tests protect the decisions that matter most: hydration products must remain osmolality/ORS gated, dry products must not be falsely blocked by standing-solution osmolality, and salt/hydrate substitutions such as dextrose monohydrate vs anhydrous dextrose must be caught before formula recommendations change.

## Risks / unknowns

- `osmotic_n` is a screening approximation, not measured osmolality.
- Matrix solubility can differ from single-substance ceilings.
- Registry overlays can hide defaults if duplicate keys are not audited.
- Missing molar mass/ion data can undercount osmoles; MgCl2 prior artifacts already flagged this class of failure.
- `complete_ors` is currently heuristic; Na-only/glucose-only/WHO-like fixtures should prevent overclaiming hydration.
- Draft records are useful for research but should not silently enter production scoring.

## Validation checklist

- Add schema validation for physical records.
- Add drift audit between legacy constants and registry values.
- Add pytest fixtures for `1542 BLOCK`, `274 PASS`, and `291 PASS`.
- Add negative fixture for dextrose monohydrate swapped to anhydrous dextrose.
- Add negative fixtures for unknown MW/ions, MgCl2 hydrate identity, Na-only and glucose-only pseudo-ORS formulas.
- Add loader tests for rejected/blocked/draft records, duplicate compat keys, and CWD-independent registry loading.

## Affected files

- `compat/data.py`
- `compat/osmolality.py`
- `compat/solubility.py`
- `compat/ph_module.py`
- `compat/stokes.py`
- `compat_calc.py`
- `reformulate.py`
- `verify_dry_sku.py`
- `concentrate.py`
- `prep_sheet.py`
- `substances/physical/*.json`
- future `tests/test_compat_registry.py`, `tests/test_compat_golden_fixtures.py`, and `fixtures/compat/*.json`

## Evidence references

- Research artifact: `artifacts/compat-improvement-research-20260618/topics-04-08-registry-tests.md`
- Context snapshot: `.omx/context/compat-stability-improvement-team-20260618T071451Z.md`
- Prior KB: `.omc/wiki/formulation-compatibility-stability-calculator-compat-osmolality.md`
- Provenance precedent: `omx_wiki/stats-card-provenance-registry-upgrade-2026-06-17.md`

Coordination protocol: coordinated - task boundaries checked; this page is limited to topics 4+8 and defers unified API/scoring, ORS use-case thresholds, pairwise/redox rules, and pH/Arrhenius modeling to peer task pages.
