# Pairwise compatibility registry

`pairwise-rules.json` is the minimal machine-readable rule registry for topic 03.
It supports exact-key and class-based rules, context-specific severity downgrades,
mitigations, validation assays, and source references.

Use `compat.pairwise.evaluate_pairwise(components, phase_context)` to produce a
normalized ledger. Unknown substance classes and unmodeled pairs are emitted as
explicit `unknown` evidence rather than treated as safe.

Gibbs thermodynamics remains backup-only explanatory evidence. Practical gates
come from this pairwise registry, redox mechanisms, pH/osmolality/solubility, and
validated stability data.
