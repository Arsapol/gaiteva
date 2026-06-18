"""
compat — gamefowl supplement compatibility & stability calculator package.

Modules
-------
data        : SUBSTANCES dict and DEGRADATION_EA_J_PER_MOL constants
solubility  : additive solubility check, TDS, bottleneck report
arrhenius   : Arrhenius kinetics and per-pathway shelf-life projections
ph_module   : Henderson-Hasselbalch, citrate buffer speciation, pH window check
stokes      : Stokes settling velocity for undissolved fractions
gibbs       : backup Gibbs free energy spontaneity screen
redox       : Tier-0 ascorbate metal/O2-catalysed oxidation risk screener
pairwise    : machine-readable pairwise incompatibility rule evaluator

All public functions are pure and return new dicts (no mutation).
Run from the project root so that absolute imports (from compat.X import …)
resolve correctly.
"""

from compat.report import evaluate_formula, render_markdown

__all__ = ["evaluate_formula", "render_markdown"]
