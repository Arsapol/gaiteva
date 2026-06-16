"""
Gamefowl supplement stability — Tier-0 ascorbate redox-risk screener.

Model
-----
Ascorbate aerobic oxidation is catalysed by trace transition metals
(Cu(II), Fe(III/II)).  Rate is roughly first-order in [ascorbate], [O2],
and [free metal].  Copper is ~80x more catalytic than iron per mole.
The metal-catalysed pathway operates at LOW activation energy (Ea), so
refrigeration does NOT rescue an incompatible formulation; only removing
the catalyst (chelation) or the co-substrate (O2 exclusion) helps.

This module is a QUALITATIVE SCREENING tool only, not a kinetic predictor.
It returns risk flags and mitigation priorities — not rate constants.

Key inputs modelled
-------------------
- Presence of catalytic metals (copper, iron)
- Oxygen exposure (sealed / headspace / open)
- Light exposure (opaque / clear packaging)
- Chelator presence and chelator:metal molar ratio

Chelation caveat: adequacy at a ratio ≥ 3 still does NOT guarantee redox
inactivity — many metal-chelate complexes remain partially redox-active.

All public functions are pure and return new dicts (no mutation).
Run from project root: ``python3 -m compat.redox``
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# Internal constants
# ---------------------------------------------------------------------------

_OXYGEN_LEVELS: dict[str, int] = {
    "sealed": 0,
    "headspace": 1,
    "open": 2,
}

_LIGHT_LEVELS: dict[str, int] = {
    "opaque": 0,
    "clear": 1,
}

_EA_NOTE = (
    "The metal-catalysed ascorbate oxidation pathway operates at LOW Ea "
    "(~40-50 kJ/mol).  Accelerated-aging studies (ICH Q1A, 40 °C/75 % RH) "
    "will UNDER-PREDICT real-time loss at ambient temperature because the "
    "reaction is relatively insensitive to temperature.  ICH real-time data "
    "(25 °C/60 % RH, ≥12 months) is mandatory before assigning shelf life."
)


# ---------------------------------------------------------------------------
# 1. chelation_adequacy
# ---------------------------------------------------------------------------

def chelation_adequacy(chelator_to_metal_molar_ratio: Optional[float]) -> dict:
    """Classify chelator:metal molar ratio and return adequacy tier + caveat.

    Parameters
    ----------
    chelator_to_metal_molar_ratio:
        Moles of chelating ligand per mole of catalytic metal.
        Pass ``None`` if unknown or not applicable.

    Returns
    -------
    dict with keys:
        tier (str): 'unknown' | 'insufficient' | 'partial' | 'adequate-but-not-redox-proof'
        ratio (float | None): echo of input
        caveat (str): human-readable interpretation
    """
    ratio = chelator_to_metal_molar_ratio

    if ratio is None:
        return {
            "tier": "unknown",
            "ratio": None,
            "caveat": (
                "No chelator:metal ratio provided.  Cannot assess chelation "
                "adequacy; assume worst-case (no effective chelation)."
            ),
        }
    if ratio < 1.0:
        return {
            "tier": "insufficient",
            "ratio": ratio,
            "caveat": (
                f"Ratio {ratio:.2f} < 1 — more catalytic metal than chelator; "
                "significant free metal expected.  Strong ascorbate oxidation risk."
            ),
        }
    if ratio < 3.0:
        return {
            "tier": "partial",
            "ratio": ratio,
            "caveat": (
                f"Ratio {ratio:.2f} in 1–3 range — stoichiometric chelation but "
                "incomplete binding likely due to competing equilibria.  Free "
                "metal fraction still catalytically relevant."
            ),
        }
    return {
        "tier": "adequate-but-not-redox-proof",
        "ratio": ratio,
        "caveat": (
            f"Ratio {ratio:.2f} ≥ 3 — thermodynamically favourable chelation, "
            "but many metal-chelate complexes (e.g. Cu-citrate) retain partial "
            "redox activity.  Chelation reduces, but does not eliminate, catalysis."
        ),
    }


# ---------------------------------------------------------------------------
# 2. ascorbate_redox_risk
# ---------------------------------------------------------------------------

def ascorbate_redox_risk(
    has_copper: bool,
    has_iron: bool,
    oxygen_exposure: str,
    light_exposure: str,
    chelator_present: bool,
    chelator_to_metal_molar_ratio: Optional[float],
) -> dict:
    """Qualitative ascorbate oxidation risk from metal/O2/light inputs.

    Parameters
    ----------
    has_copper:
        Any copper salt present in formulation (e.g. copper TBCC).
    has_iron:
        Any iron salt present.
    oxygen_exposure:
        'sealed' | 'headspace' | 'open'
    light_exposure:
        'opaque' | 'clear'
    chelator_present:
        True if a chelating agent (citrate, EDTA, etc.) is in formula.
    chelator_to_metal_molar_ratio:
        Moles chelator per mole metal; None if unknown.

    Returns
    -------
    dict with keys:
        risk_level (str): 'LOW' | 'MODERATE' | 'HIGH' | 'SEVERE'
        drivers (list[str]): risk-elevating factors present
        mitigations (list[str]): recommended mitigations in priority order
        ea_note (str): kinetics caveat on Ea and accelerated aging
    """
    if oxygen_exposure not in _OXYGEN_LEVELS:
        raise ValueError(
            f"oxygen_exposure must be one of {list(_OXYGEN_LEVELS)}; got {oxygen_exposure!r}"
        )
    if light_exposure not in _LIGHT_LEVELS:
        raise ValueError(
            f"light_exposure must be one of {list(_LIGHT_LEVELS)}; got {light_exposure!r}"
        )

    o2_score = _OXYGEN_LEVELS[oxygen_exposure]
    light_score = _LIGHT_LEVELS[light_exposure]
    chelation = chelation_adequacy(chelator_to_metal_molar_ratio)

    drivers: list[str] = []
    mitigations: list[str] = []

    # --- Metal scoring ---
    metal_score = 0
    if has_copper:
        metal_score += 2  # Cu ~80x more catalytic than Fe per mole
        drivers.append("Copper present (~80x more catalytic than Fe per mole)")
    if has_iron:
        metal_score += 1
        drivers.append("Iron present (moderate catalytic activity)")

    # --- Oxygen ---
    if o2_score == 2:
        drivers.append("Open container — maximal O2 exposure")
    elif o2_score == 1:
        drivers.append("Headspace O2 present — residual catalysis possible")

    # --- Light ---
    if light_score == 1:
        drivers.append("Clear packaging — light accelerates free-radical oxidation")

    # --- Chelation (only relevant when catalytic metals are present) ---
    if chelator_present and metal_score > 0:
        if chelation["tier"] == "adequate-but-not-redox-proof":
            mitigations.append(
                "Chelator present at adequate ratio (≥3:1) — reduces free metal; "
                "verify redox inactivity of chelate complex experimentally"
            )
        elif chelation["tier"] == "partial":
            drivers.append(
                f"Chelator present but ratio {chelation['ratio']:.2f} only partial — "
                "free metal fraction still catalytically active"
            )
            mitigations.append("Increase chelator:metal ratio to ≥3:1")
        elif chelation["tier"] == "insufficient":
            drivers.append(
                f"Chelator insufficient (ratio {chelation['ratio']:.2f} < 1) — "
                "excess free metal"
            )
            mitigations.append("Add chelator to achieve ≥3:1 molar ratio vs total metal")
        else:  # unknown
            drivers.append("Chelation status unknown — assuming no effective chelation")
            mitigations.append("Quantify chelator:metal molar ratio; target ≥3:1")
    elif metal_score > 0:
        drivers.append("No chelator present — all metal potentially free/exchangeable")
        mitigations.append(
            "Add chelating agent (EDTA or citrate); target molar ratio ≥3:1 vs metal"
        )

    # --- Oxygen mitigations ---
    if o2_score > 0:
        mitigations.append(
            "Reduce O2 exposure: headspace inert-gas purge, low-O2-permeability "
            "packaging, or reduce hold time after reconstitution"
        )

    # --- Light mitigations ---
    if light_score > 0:
        mitigations.append("Switch to opaque/UV-blocking packaging")

    # --- Sacrificial antioxidant as last resort ---
    if metal_score > 0:
        mitigations.append(
            "Consider sacrificial antioxidant (e.g. additional ascorbate buffer "
            "or sodium metabisulfite) — lowest-priority mitigation"
        )

    # --- Risk level computation ---
    # Score: metal (0-3) + oxygen (0-2) + light (0-1) = 0-6
    # Chelation can reduce effective score by up to 2
    base_score = metal_score + o2_score + light_score
    chelation_reduction = 0
    if chelator_present:
        if chelation["tier"] == "adequate-but-not-redox-proof":
            chelation_reduction = 2
        elif chelation["tier"] == "partial":
            chelation_reduction = 1
    effective_score = max(0, base_score - chelation_reduction)

    if effective_score == 0:
        risk_level = "LOW"
    elif effective_score <= 2:
        risk_level = "MODERATE"
    elif effective_score <= 4:
        risk_level = "HIGH"
    else:
        risk_level = "SEVERE"

    # Sealed + chelated ceiling: even best case is MODERATE (trace metal + residual O2)
    if (
        risk_level == "LOW"
        and metal_score > 0
        and oxygen_exposure != "open"
    ):
        risk_level = "MODERATE"

    return {
        "risk_level": risk_level,
        "drivers": drivers,
        "mitigations": mitigations,
        "ea_note": _EA_NOTE,
    }


# ---------------------------------------------------------------------------
# 3. flag_from_components
# ---------------------------------------------------------------------------

def flag_from_components(
    components: list[tuple[str, float]],
    oxygen_exposure: str = "headspace",
    light_exposure: str = "clear",
) -> dict:
    """Detect ascorbate + metals + chelators in a component list and return risk flag.

    Parameters
    ----------
    components:
        List of (ingredient_key, amount) tuples.  Keys are lower-cased and
        stripped before matching.
    oxygen_exposure:
        Forwarded to ``ascorbate_redox_risk``.
    light_exposure:
        Forwarded to ``ascorbate_redox_risk``.

    Returns
    -------
    If ascorbic_acid not detected: ``{'applicable': False}``
    Otherwise: result of ``ascorbate_redox_risk`` plus ``{'applicable': True,
    'detected': dict}`` describing what was found.
    """
    keys = [k.strip().lower() for k, _ in components]

    def _any_match(patterns: list[str]) -> bool:
        return any(p in k for k in keys for p in patterns)

    has_ascorbate = _any_match(["ascorbic_acid", "ascorbate", "vitamin_c"])
    if not has_ascorbate:
        return {"applicable": False}

    has_copper = _any_match(["copper", "cu_", "_cu", "cu("])
    has_iron = _any_match(["iron", "fe_", "_fe", "ferr"])
    has_chelator = _any_match(["citrate", "citric_acid", "edta", "ethylenediamine"])

    # Rough ratio: count chelator mass proxies vs metal entries (qualitative)
    chelator_ratio: Optional[float] = None
    metal_count = sum(1 for k in keys if any(p in k for p in ["copper", "cu_", "_cu", "cu(", "iron", "fe_", "_fe", "ferr"]))
    chelator_count = sum(1 for k in keys if any(p in k for p in ["citrate", "citric_acid", "edta"]))
    if metal_count > 0 and chelator_count > 0:
        # Use 1:1 molar proxy when amounts unknown (conservative; flags partial)
        chelator_ratio = chelator_count / metal_count

    detected = {
        "ascorbate": has_ascorbate,
        "copper": has_copper,
        "iron": has_iron,
        "chelator": has_chelator,
        "chelator_to_metal_ratio_estimate": chelator_ratio,
    }

    result = ascorbate_redox_risk(
        has_copper=has_copper,
        has_iron=has_iron,
        oxygen_exposure=oxygen_exposure,
        light_exposure=light_exposure,
        chelator_present=has_chelator,
        chelator_to_metal_molar_ratio=chelator_ratio,
    )

    return {"applicable": True, "detected": detected, **result}


# ---------------------------------------------------------------------------
# __main__ smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("CASE 1 — ORS reformulation (citrate present, no copper/iron)")
    print("=" * 60)
    ors_components = [
        ("dextrose", 14),
        ("sodium_chloride", 2.6),
        ("trisodium_citrate", 2.9),
        ("ascorbic_acid", 0.5),
    ]
    r1 = flag_from_components(ors_components, oxygen_exposure="headspace", light_exposure="clear")
    print(json.dumps(r1, indent=2))

    print()
    print("=" * 60)
    print("CASE 2 — Worst case (copper + ascorbate, open container, clear)")
    print("=" * 60)
    worst_components = [
        ("copper_tbcc", 0.1),
        ("ascorbic_acid", 0.5),
        ("dextrose", 14.0),
    ]
    r2 = flag_from_components(worst_components, oxygen_exposure="open", light_exposure="clear")
    print(json.dumps(r2, indent=2))

    print()
    print("=" * 60)
    print("CASE 3 — chelation_adequacy edge cases")
    print("=" * 60)
    for ratio in [None, 0.5, 2.0, 5.0]:
        ca = chelation_adequacy(ratio)
        print(f"  ratio={ratio!r:>5}  =>  tier={ca['tier']!r}")
