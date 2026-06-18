# Compat physical constants registry

`substances/physical/*.json` is the canonical transition registry for physical constants consumed by `compat.data`.

Loader contract:

- Resolve the registry relative to the repo/module root, not `Path.cwd()`.
- Load `verified` and `reviewed` records by default; `draft` requires explicit research mode; `blocked`/`rejected` never load.
- Validate active records for calculator-critical fields: `compat_key`, `key`, `name`, `molar_mass_g_per_mol`, `osmotic_n`, `review_status`, `sources`, and `source_refs`.
- Keep salt-as-weighed identity explicit with `key` (weighed form) and `compat_key` (calculator key); e.g. magnesium chloride hexahydrate maps to `magnesium_chloride`.
- Preserve deterministic load order by sorted file name and record key; duplicate `compat_key` values must declare `overrides` or produce a warning.

`compat.registry.load_physical_registry()` returns diagnostics and a report suitable for future generated drift artifacts. `compat.data` applies the validated registry to legacy dictionaries so existing smoke outputs stay stable during migration.
