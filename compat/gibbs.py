"""
gibbs.py — BACKUP-ONLY thermodynamic spontaneity screen.

PURPOSE: Flag reactions where dG < 0 (thermodynamically spontaneous).
WARNING: Thermodynamics ≠ kinetics. A negative dG means a reaction CAN
         occur, NOT that it will occur quickly or at all under conditions.
PRIMARY safety tool is the reactivity matrix in formula-safety-check skill.
This module is a SECONDARY backup screen only — never use it as sole safety
authority.
"""

from __future__ import annotations

_BACKUP_CAVEAT = (
    "BACKUP SCREEN ONLY — spontaneous (dG<0) does NOT mean fast or dangerous "
    "in practice; kinetics govern actual reaction rate. The reactivity matrix "
    "in formula-safety-check is the PRIMARY safety tool."
)


def gibbs(dH_J: float, dS_J_per_K: float, T_K: float = 298.15) -> dict:
    """Return Gibbs free energy analysis at temperature T_K.

    Args:
        dH_J: Enthalpy change in Joules.
        dS_J_per_K: Entropy change in J/K.
        T_K: Temperature in Kelvin (default 298.15 K = 25 °C).

    Returns:
        Immutable-style dict with keys:
            dG_J (float), dG_kJ (float),
            spontaneous (bool), verdict (str).
    """
    dG_J = dH_J - T_K * dS_J_per_K
    dG_kJ = dG_J / 1000.0
    spontaneous = dG_J < 0.0
    verdict = (
        f"dG = {dG_kJ:.2f} kJ/mol — "
        + ("SPONTANEOUS (thermodynamically favoured)" if spontaneous
           else "NON-SPONTANEOUS (thermodynamically unfavoured)")
    )
    return {
        "dG_J": dG_J,
        "dG_kJ": dG_kJ,
        "spontaneous": spontaneous,
        "verdict": verdict,
    }


def screen_pair(
    name_a: str,
    name_b: str,
    dH_J: float,
    dS_J_per_K: float,
    T_K: float = 298.15,
) -> dict:
    """Screen a substance pair for thermodynamic spontaneity.

    Wraps gibbs() and attaches a loud backup-role caveat.

    Args:
        name_a: Name of first substance.
        name_b: Name of second substance.
        dH_J: Enthalpy change in Joules.
        dS_J_per_K: Entropy change in J/K.
        T_K: Temperature in Kelvin (default 298.15 K).

    Returns:
        Dict with keys: pair (str), gibbs_result (dict), caveat (str).
    """
    result = gibbs(dH_J, dS_J_per_K, T_K)
    return {
        "pair": f"{name_a} + {name_b}",
        "gibbs_result": result,
        "caveat": _BACKUP_CAVEAT,
    }


if __name__ == "__main__":
    # Smoke test: strong acid–base neutralization (illustrative)
    # HCl(aq) + NaOH(aq) -> NaCl(aq) + H2O
    # Approx values: dH ~ -57000 J/mol, dS ~ +80 J/(mol·K)
    out = screen_pair(
        name_a="HCl (strong acid)",
        name_b="NaOH (strong base)",
        dH_J=-57000,
        dS_J_per_K=80,
    )
    print("=== gibbs.py smoke test ===")
    print(f"Pair   : {out['pair']}")
    print(f"dG_J   : {out['gibbs_result']['dG_J']:.2f} J/mol")
    print(f"dG_kJ  : {out['gibbs_result']['dG_kJ']:.2f} kJ/mol")
    print(f"Spont  : {out['gibbs_result']['spontaneous']}")
    print(f"Verdict: {out['gibbs_result']['verdict']}")
    print(f"Caveat : {out['caveat']}")
