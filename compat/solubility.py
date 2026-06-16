"""
Gamefowl supplement compatibility — solubility & TDS checks.

All functions are pure and immutable: they never mutate their arguments
and always return new dicts.  Import SUBSTANCES from compat.data for the
physical-chemistry constants used in every calculation.

Typical usage
-------------
>>> from compat.solubility import additive_report
>>> report = additive_report(
...     [("creatine_monohydrate", 5), ("l_tyrosine", 0.5)],
...     water_ml=200,
... )
>>> report["bottlenecks"]
['creatine_monohydrate: 5 g undissolved (ceiling 1.4 g/100 mL)',
 'l_tyrosine: 0.495 g undissolved (ceiling 0.045 g/100 mL)']
"""

from __future__ import annotations

from typing import NamedTuple

from compat.data import SUBSTANCES

# ---------------------------------------------------------------------------
# Supersaturation-on-cooling flag candidates
# ---------------------------------------------------------------------------
_SUPERSATURATION_CANDIDATES: frozenset[str] = frozenset({"dextrose", "citric_acid"})

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ceiling(name: str) -> float | None:
    """Return solubility ceiling (g/100 mL) or None if miscible."""
    entry = SUBSTANCES.get(name)
    if entry is None:
        return None
    return entry["solubility_g_per_100ml_25c"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_substance(name: str, grams: float, water_ml: float) -> dict:
    """
    Compare dissolved concentration to a substance's solubility ceiling.

    Parameters
    ----------
    name : str
        Lowercase substance key matching SUBSTANCES (e.g. "creatine_monohydrate").
    grams : float
        Mass of the substance added, in grams.
    water_ml : float
        Volume of water used as solvent, in mL.

    Returns
    -------
    dict with keys:
        name               – str
        conc_g_per_100ml   – float  (actual concentration if fully dissolved)
        ceiling            – float | None  (None = miscible)
        headroom_pct       – float | None  (None when miscible or ceiling is 0)
        dissolved          – bool
        undissolved_g      – float  (0.0 when fully dissolved)
    """
    ceiling = _ceiling(name)
    conc = (grams / water_ml) * 100.0 if water_ml > 0 else 0.0

    if ceiling is None:
        # Miscible substance (e.g. glycerin) — always fully dissolved
        return {
            "name": name,
            "conc_g_per_100ml": conc,
            "ceiling": None,
            "headroom_pct": None,
            "dissolved": True,
            "undissolved_g": 0.0,
        }

    dissolved = conc <= ceiling
    undissolved_g = 0.0 if dissolved else (conc - ceiling) * water_ml / 100.0
    headroom_pct = ((ceiling - conc) / ceiling * 100.0) if ceiling > 0 else None

    return {
        "name": name,
        "conc_g_per_100ml": round(conc, 6),
        "ceiling": ceiling,
        "headroom_pct": round(headroom_pct, 2) if headroom_pct is not None else None,
        "dissolved": dissolved,
        "undissolved_g": round(undissolved_g, 4),
    }


def total_dissolved_solids(
    components: list[tuple[str, float]],
    water_ml: float,
) -> dict:
    """
    Compute total dissolved solids (TDS) for a multi-substance solution.

    Only counts grams that actually dissolve (capped at each substance's
    ceiling); miscible substances contribute their full mass.

    Parameters
    ----------
    components : list of (name, grams) tuples
    water_ml   : float

    Returns
    -------
    dict with keys:
        total_dissolved_g   – float
        w_v_pct             – float  (g dissolved / 100 mL water)
        salting_out_flag    – bool   (True when %w/v > 20)
    """
    dissolved_g = 0.0
    for name, grams in components:
        ceiling = _ceiling(name)
        if ceiling is None:
            # Miscible: full mass dissolves
            dissolved_g += grams
        else:
            max_g = ceiling * water_ml / 100.0
            dissolved_g += min(grams, max_g)

    w_v = (dissolved_g / water_ml * 100.0) if water_ml > 0 else 0.0

    return {
        "total_dissolved_g": round(dissolved_g, 4),
        "w_v_pct": round(w_v, 4),
        "salting_out_flag": w_v > 20.0,
    }


def additive_report(
    components: list[tuple[str, float]],
    water_ml: float,
) -> dict:
    """
    Aggregate per-substance solubility checks, TDS, and explicit warnings.

    Parameters
    ----------
    components : list of (name, grams) tuples
    water_ml   : float

    Returns
    -------
    dict with keys:
        water_ml            – float
        substances          – list[dict]  (one check_substance result per item)
        tds                 – dict        (total_dissolved_solids result)
        bottlenecks         – list[str]   (substances over their ceiling)
        supersaturation_warnings – list[str]  (near-ceiling cooling risk)
    """
    substance_checks = [
        check_substance(name, grams, water_ml) for name, grams in components
    ]

    tds = total_dissolved_solids(components, water_ml)

    bottlenecks: list[str] = []
    supersaturation_warnings: list[str] = []

    for check in substance_checks:
        name = check["name"]
        ceiling = check["ceiling"]

        if not check["dissolved"]:
            bottlenecks.append(
                f"{name}: {check['undissolved_g']} g undissolved "
                f"(ceiling {ceiling} g/100 mL)"
            )

        # Near-ceiling supersaturation-on-cooling risk for dextrose / citric_acid
        if (
            name in _SUPERSATURATION_CANDIDATES
            and ceiling is not None
            and ceiling > 0
            and check["conc_g_per_100ml"] >= ceiling * 0.75
        ):
            supersaturation_warnings.append(
                f"{name}: concentration {check['conc_g_per_100ml']:.3f} g/100 mL "
                f"is ≥75 % of ceiling ({ceiling} g/100 mL) — "
                "risk of supersaturation / crystallisation on cooling"
            )

    return {
        "water_ml": water_ml,
        "substances": substance_checks,
        "tds": tds,
        "bottlenecks": bottlenecks,
        "supersaturation_warnings": supersaturation_warnings,
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # Typical gamefowl drench: two known weak-link substances
    example_components: list[tuple[str, float]] = [
        ("creatine_monohydrate", 5.0),   # ceiling ~1.4 g/100 mL → will precipitate
        ("l_tyrosine", 0.5),             # ceiling ~0.045 g/100 mL → will precipitate
        ("beta_alanine", 2.0),           # ceiling 55 g/100 mL → fine
        ("glycerin", 10.0),              # miscible → always fine
        ("dextrose", 15.0),              # ceiling 91 g/100 mL; test near-ceiling path
    ]
    WATER_ML = 200.0

    report = additive_report(example_components, WATER_ML)
    print(json.dumps(report, indent=2))

    assert report["tds"]["salting_out_flag"] is False, "unexpected salting-out flag"
    assert len(report["bottlenecks"]) == 2, (
        f"expected 2 bottlenecks, got {report['bottlenecks']}"
    )
    print("\nSmoke test PASSED")
