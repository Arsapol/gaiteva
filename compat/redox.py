"""
Gamefowl supplement stability — Tier-0 redox mechanism ledger.

Model
-----
This module is a QUALITATIVE SCREENING tool only, not a kinetic predictor.
It returns risk flags, explicit risk factors, validation assays, mitigation
priorities, and the threshold assumptions used by the screen — not rate
constants or shelf-life claims.

The original ascorbate metal/O2/light screen is preserved and now feeds a
small mechanism ledger covering:

- ascorbate oxidation;
- thiol oxidation for NAC/cysteine-like antioxidants;
- oil/peroxide risk in wet emulsions;
- ribose + ascorbate co-loss/advisory interactions;
- transition-metal catalysis assumptions from added metals or CoA ppm fields.

Chelation caveat: adequacy at a ratio ≥ 3 still does NOT guarantee redox
inactivity — many metal-chelate complexes remain partially redox-active.

All public functions are pure and return new dicts (no mutation).
Run from project root: ``python3 -m compat.redox``
"""

from __future__ import annotations

from typing import Optional

from compat.data import MOLAR_MASS_G_PER_MOL


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
    "amber": 0,
    "clear": 1,
}

_STORAGE_CONTEXTS: set[str] = {"dry", "make_fresh", "wet_stored", "concentrate", "oil_emulsion"}

_RISK_ORDER: dict[str, int] = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "SEVERE": 3}

_THRESHOLDS = {
    "risk_score": {
        "LOW": "0 effective points",
        "MODERATE": "1-2 effective points, or trace-metal floor with sealed/headspace O2",
        "HIGH": "3-4 effective points",
        "SEVERE": ">=5 effective points",
    },
    "chelator_to_metal_ratio": {
        "insufficient": "<1:1 molar chelator:metal",
        "partial": "1:1 to <3:1 molar chelator:metal",
        "adequate_but_not_redox_proof": ">=3:1 molar chelator:metal",
    },
    "context_downgrade": {
        "dry": "wet redox mechanisms are storage-N/A; evaluate packaging/dose uniformity instead",
        "make_fresh": "same-day discard may downgrade one risk tier if hold time is explicit",
        "wet_stored": "standing liquid; no shelf-life claim without assays",
    },
}

_EA_NOTE = (
    "The metal-catalysed ascorbate oxidation pathway operates at LOW Ea "
    "(~40-50 kJ/mol).  Accelerated-aging studies (ICH Q1A, 40 °C/75 % RH) "
    "will UNDER-PREDICT real-time loss at ambient temperature because the "
    "reaction is relatively insensitive to temperature.  ICH real-time data "
    "(25 °C/60 % RH, ≥12 months) is mandatory before assigning shelf life."
)

_ASSAY_BY_MECHANISM: dict[str, list[str]] = {
    "ascorbate_oxidation": [
        "HPLC ascorbic acid + dehydroascorbic acid (DHAA)",
        "colorimetry/browning trend",
        "real-time and stress stability in final packaging",
    ],
    "thiol_oxidation": [
        "HPLC/LC-MS NAC or cysteine plus disulfide dimer",
        "free-thiol assay",
        "metal CoA review (Cu/Fe ppm) and oxygen challenge",
    ],
    "oil_peroxide": [
        "peroxide value",
        "anisidine/TOTOX where relevant",
        "sensory/odor plus emulsion stability observation",
    ],
    "ribose_ascorbate_coloss": [
        "HPLC ascorbate/DHAA",
        "colorimetry/browning",
        "ribose assay if shelf claim depends on potency",
    ],
    "transition_metal_catalysis": [
        "supplier CoA Cu/Fe/Mn ppm limits",
        "ICP-MS or equivalent metals panel on incoming lots",
    ],
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def _component_keys(components: list[tuple[str, float]]) -> list[str]:
    return [_norm(k) for k, _ in components]


def _any_match(keys: list[str], patterns: list[str]) -> bool:
    return any(p in k for k in keys for p in patterns)


def _highest_risk(levels: list[str]) -> str:
    if not levels:
        return "LOW"
    return max(levels, key=lambda level: _RISK_ORDER[level])


def _downgrade(level: str) -> str:
    order = ["LOW", "MODERATE", "HIGH", "SEVERE"]
    return order[max(0, order.index(level) - 1)]


def _is_wet_context(storage_context: str) -> bool:
    return storage_context in {"wet_stored", "concentrate", "oil_emulsion", "make_fresh"}


def _estimate_chelator_to_metal_molar_ratio(components: list[tuple[str, float]]) -> float | None:
    chelator_mol = 0.0
    metal_mol = 0.0
    for raw_name, grams in components:
        name = _norm(raw_name)
        mw = MOLAR_MASS_G_PER_MOL.get(name)
        if not mw or grams <= 0:
            continue
        mol = grams / mw
        if any(p in name for p in ["citrate", "citric_acid", "edta"]):
            chelator_mol += mol
        if any(p in name for p in ["copper", "cu_", "_cu", "iron", "fe_", "_fe", "ferr", "manganese", "mn_", "_mn"]):
            metal_mol += mol
    if chelator_mol > 0 and metal_mol > 0:
        return chelator_mol / metal_mol
    return None


def _metal_presence(keys: list[str], metal_ppm: Optional[dict[str, float]] = None) -> dict:
    """Return added/CoA metal flags without pretending ppm is kinetic input."""
    metal_ppm = metal_ppm or {}
    has_copper = _any_match(keys, ["copper", "cu_", "_cu", "cu("]) or metal_ppm.get("cu", 0) > 0
    has_iron = _any_match(keys, ["iron", "fe_", "_fe", "ferr"]) or metal_ppm.get("fe", 0) > 0
    has_manganese = _any_match(keys, ["manganese", "mn_", "_mn"]) or metal_ppm.get("mn", 0) > 0
    ppm_flags = {k: v for k, v in metal_ppm.items() if v and v > 0}
    return {
        "copper": has_copper,
        "iron": has_iron,
        "manganese": has_manganese,
        "supplier_coa_ppm": ppm_flags,
        "metal_score": (2 if has_copper else 0) + (1 if has_iron else 0) + (1 if has_manganese else 0),
    }


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

    Returns legacy keys (``risk_level``, ``drivers``, ``mitigations``,
    ``ea_note``) plus score/threshold/reporting fields for auditability.
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
    if risk_level == "LOW" and metal_score > 0 and oxygen_exposure != "open":
        risk_level = "MODERATE"

    return {
        "risk_level": risk_level,
        "drivers": drivers,
        "mitigations": mitigations,
        "ea_note": _EA_NOTE,
        "risk_score": {
            "metal": metal_score,
            "oxygen": o2_score,
            "light": light_score,
            "chelation_reduction": chelation_reduction,
            "base": base_score,
            "effective": effective_score,
        },
        "thresholds": _THRESHOLDS,
        "validation_assays": _ASSAY_BY_MECHANISM["ascorbate_oxidation"],
        "data_reporting": {
            "oxygen_exposure": oxygen_exposure,
            "light_exposure": light_exposure,
            "has_copper": has_copper,
            "has_iron": has_iron,
            "chelator_present": chelator_present,
            "chelation": chelation,
        },
    }


# ---------------------------------------------------------------------------
# 3. redox_mechanism_ledger
# ---------------------------------------------------------------------------

def redox_mechanism_ledger(
    components: list[tuple[str, float]],
    oxygen_exposure: str = "headspace",
    light_exposure: str = "clear",
    storage_context: str = "wet_stored",
    chelator_to_metal_molar_ratio: Optional[float] = None,
    metal_ppm: Optional[dict[str, float]] = None,
    hold_time_hours: Optional[float] = None,
    packaging: Optional[dict[str, object]] = None,
) -> dict:
    """Return a qualitative redox mechanism ledger for formula components.

    ``storage_context`` must be ``dry``, ``make_fresh``, ``wet_stored``,
    ``concentrate``, or ``oil_emulsion``.  Same-day make-fresh can downgrade
    risk only when ``hold_time_hours`` is provided and <= 24.
    """
    if oxygen_exposure not in _OXYGEN_LEVELS:
        raise ValueError(
            f"oxygen_exposure must be one of {list(_OXYGEN_LEVELS)}; got {oxygen_exposure!r}"
        )
    if light_exposure not in _LIGHT_LEVELS:
        raise ValueError(
            f"light_exposure must be one of {list(_LIGHT_LEVELS)}; got {light_exposure!r}"
        )
    if storage_context not in _STORAGE_CONTEXTS:
        raise ValueError(
            f"storage_context must be one of {sorted(_STORAGE_CONTEXTS)}; got {storage_context!r}"
        )

    keys = _component_keys(components)
    packaging = packaging or {}
    metals = _metal_presence(keys, metal_ppm)

    has_ascorbate = _any_match(keys, ["ascorbic_acid", "ascorbate", "vitamin_c"])
    has_thiol = _any_match(keys, ["nac", "n_acetylcysteine", "acetylcysteine", "cysteine", "glutathione"])
    has_ribose = _any_match(keys, ["ribose", "d_ribose"])
    has_oil = _any_match(keys, ["oil", "mct", "tocopherol", "coq10", "ubiquinone", "lecithin"])
    has_chelator = _any_match(keys, ["citrate", "citric_acid", "edta", "ethylenediamine"])
    if chelator_to_metal_molar_ratio is None and metals["metal_score"] > 0 and has_chelator:
        chelator_to_metal_molar_ratio = _estimate_chelator_to_metal_molar_ratio(components)

    mechanisms: list[dict] = []
    common_assumptions = []
    if packaging.get("nitrogen_purged") is True:
        common_assumptions.append("Nitrogen purge declared; residual oxygen still requires verification")
    if packaging.get("low_otr") is True:
        common_assumptions.append("Low-OTR packaging declared; report retains assay requirement")
    if packaging.get("opaque") is True:
        common_assumptions.append("Opaque/UV-blocking packaging declared")

    if has_ascorbate:
        a = ascorbate_redox_risk(
            has_copper=metals["copper"],
            has_iron=metals["iron"],
            oxygen_exposure=oxygen_exposure,
            light_exposure="opaque" if packaging.get("opaque") is True else light_exposure,
            chelator_present=has_chelator,
            chelator_to_metal_molar_ratio=chelator_to_metal_molar_ratio,
        )
        mechanisms.append({
            "mechanism": "ascorbate_oxidation",
            "risk_level": a["risk_level"],
            "drivers": a["drivers"],
            "mitigations": a["mitigations"],
            "risk_score": a["risk_score"],
            "validation_assays": a["validation_assays"],
        })

    if has_thiol:
        if storage_context == "dry":
            thiol_level = "LOW"
            thiol_drivers = ["Thiol/NAC present, but dry-separated from wet oxygen during storage"]
            thiol_mitigations = ["Keep thiol dry until same-day use; protect from humidity and metal contamination"]
        else:
            score = (2 if _is_wet_context(storage_context) else 0) + _OXYGEN_LEVELS[oxygen_exposure] + min(2, metals["metal_score"])
            thiol_level = "MODERATE" if score <= 2 else "HIGH" if score <= 4 else "SEVERE"
            if storage_context == "make_fresh" and hold_time_hours is not None and hold_time_hours <= 24:
                thiol_level = _downgrade(thiol_level)
            thiol_drivers = ["Thiol/NAC class can oxidize to disulfides in wet oxygenated matrices"]
            if metals["metal_score"]:
                thiol_drivers.append("Transition-metal catalysis present or declared by CoA ppm")
            if oxygen_exposure != "sealed":
                thiol_drivers.append(f"{oxygen_exposure} oxygen exposure")
            if storage_context == "make_fresh" and hold_time_hours is None:
                thiol_drivers.append("Make-fresh hold time not specified; cannot safely downgrade")
            thiol_mitigations = [
                "Dry-separate NAC/thiols from wet stored liquid",
                "Use same-day discard if reconstituted; state maximum hold time",
                "Limit Cu/Fe impurities by supplier CoA and/or add chelator with assay confirmation",
            ]
        mechanisms.append({
            "mechanism": "thiol_oxidation",
            "risk_level": thiol_level,
            "drivers": thiol_drivers,
            "mitigations": thiol_mitigations,
            "risk_score": {"qualitative_points": _RISK_ORDER[thiol_level]},
            "validation_assays": _ASSAY_BY_MECHANISM["thiol_oxidation"],
        })

    if has_oil and _is_wet_context(storage_context):
        oil_level = "HIGH" if oxygen_exposure != "sealed" or light_exposure == "clear" else "MODERATE"
        if storage_context == "make_fresh" and hold_time_hours is not None and hold_time_hours <= 24:
            oil_level = _downgrade(oil_level)
        mechanisms.append({
            "mechanism": "oil_peroxide",
            "risk_level": oil_level,
            "drivers": [
                "Oil/emulsion active present in wet matrix",
                f"oxygen_exposure={oxygen_exposure}",
                f"light_exposure={light_exposure}",
            ],
            "mitigations": [
                "Use opaque low-O2 packaging or dry/oil split where feasible",
                "Measure peroxide value; do not infer peroxide stability from ascorbate data",
            ],
            "risk_score": {"qualitative_points": _RISK_ORDER[oil_level]},
            "validation_assays": _ASSAY_BY_MECHANISM["oil_peroxide"],
        })

    if has_ribose and has_ascorbate and _is_wet_context(storage_context):
        coloss_level = "MODERATE" if storage_context == "make_fresh" else "HIGH"
        mechanisms.append({
            "mechanism": "ribose_ascorbate_coloss",
            "risk_level": coloss_level,
            "drivers": ["Ribose + ascorbate co-present in wet matrix; redox/browning potency loss needs assay"],
            "mitigations": ["Dry-separate ribose/ascorbate for shelf storage or restrict to same-day use"],
            "risk_score": {"qualitative_points": _RISK_ORDER[coloss_level]},
            "validation_assays": _ASSAY_BY_MECHANISM["ribose_ascorbate_coloss"],
        })

    if metals["supplier_coa_ppm"]:
        mechanisms.append({
            "mechanism": "transition_metal_catalysis",
            "risk_level": "MODERATE" if storage_context in {"dry", "make_fresh"} else "HIGH",
            "drivers": [f"Supplier CoA metal ppm declared: {metals['supplier_coa_ppm']}", "ppm fields are audit inputs, not kinetic proof"],
            "mitigations": ["Set Cu/Fe/Mn acceptance specs; verify lots before wet shelf claims"],
            "risk_score": {"metal_score": metals["metal_score"]},
            "validation_assays": _ASSAY_BY_MECHANISM["transition_metal_catalysis"],
        })

    overall = _highest_risk([m["risk_level"] for m in mechanisms])
    shelf_claim_gate = (
        "BLOCK_SHELF_CLAIM_PENDING_ASSAYS"
        if storage_context in {"wet_stored", "concentrate", "oil_emulsion"} and overall in {"HIGH", "SEVERE"}
        else "ASSAY_REQUIRED_FOR_6_12_MONTH_CLAIM"
        if mechanisms
        else "NO_REDOX_MECHANISM_DETECTED"
    )

    validation_assays: list[str] = []
    for mech in mechanisms:
        for assay in mech["validation_assays"]:
            if assay not in validation_assays:
                validation_assays.append(assay)

    return {
        "applicable": bool(mechanisms),
        "overall_risk": overall if mechanisms else "LOW",
        "shelf_claim_gate": shelf_claim_gate,
        "mechanisms": mechanisms,
        "thresholds": _THRESHOLDS,
        "detected": {
            "ascorbate": has_ascorbate,
            "thiol": has_thiol,
            "ribose": has_ribose,
            "oil_or_emulsion_active": has_oil,
            "chelator": has_chelator,
            "metals": metals,
        },
        "data_reporting": {
            "oxygen_exposure": oxygen_exposure,
            "light_exposure": light_exposure,
            "storage_context": storage_context,
            "hold_time_hours": hold_time_hours,
            "packaging": packaging,
            "assumptions": common_assumptions,
        },
        "validation_assays": validation_assays,
        "ea_note": _EA_NOTE if has_ascorbate else "Temperature acceleration remains mechanism-specific; real-time/product-specific assay data required for shelf claims.",
    }


# ---------------------------------------------------------------------------
# 4. flag_from_components
# ---------------------------------------------------------------------------

def flag_from_components(
    components: list[tuple[str, float]],
    oxygen_exposure: str = "headspace",
    light_exposure: str = "clear",
    storage_context: str | None = None,
) -> dict:
    """Detect redox-active components and return the leading redox flag.

    Legacy ascorbate callers still receive ``risk_level``, ``drivers``,
    ``mitigations``, and ``ea_note`` at the top level. If ``storage_context`` is
    omitted, this wrapper stays ascorbate-only to avoid assuming every formula is
    a wet stored liquid. Pass an explicit storage_context to opt into the broader
    mechanism ledger.
    """
    keys = _component_keys(components)
    if storage_context is None and not _any_match(keys, ["ascorbic_acid", "ascorbate", "vitamin_c"]):
        return {"applicable": False, "reason": "legacy wrapper only applies to ascorbate unless storage_context is explicit"}
    ledger = redox_mechanism_ledger(
        components,
        oxygen_exposure=oxygen_exposure,
        light_exposure=light_exposure,
        storage_context=storage_context or "wet_stored",
    )
    if not ledger["applicable"]:
        return {"applicable": False, "mechanism_ledger": ledger}

    mechanisms = ledger["mechanisms"]
    primary = next((m for m in mechanisms if m["mechanism"] == "ascorbate_oxidation"), mechanisms[0])

    detected = {
        "ascorbate": ledger["detected"]["ascorbate"],
        "copper": ledger["detected"]["metals"]["copper"],
        "iron": ledger["detected"]["metals"]["iron"],
        "chelator": ledger["detected"]["chelator"],
        "thiol": ledger["detected"]["thiol"],
        "oil_or_emulsion_active": ledger["detected"]["oil_or_emulsion_active"],
        "chelator_to_metal_ratio_estimate": _estimate_chelator_to_metal_molar_ratio(components),
    }

    return {
        "applicable": True,
        "detected": detected,
        "risk_level": primary["risk_level"],
        "drivers": primary["drivers"],
        "mitigations": primary["mitigations"],
        "ea_note": ledger["ea_note"],
        "risk_score": primary.get("risk_score"),
        "thresholds": ledger["thresholds"],
        "validation_assays": ledger["validation_assays"],
        "shelf_claim_gate": ledger["shelf_claim_gate"],
        "mechanism_ledger": ledger,
    }


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
    print("CASE 3 — Wet NAC + Cu/O2 vs dry-separated NAC")
    print("=" * 60)
    nac_components = [("n_acetylcysteine", 1.0), ("copper_tbcc", 0.01)]
    print(json.dumps(redox_mechanism_ledger(nac_components, oxygen_exposure="headspace", storage_context="wet_stored"), indent=2))
    print(json.dumps(redox_mechanism_ledger(nac_components, oxygen_exposure="headspace", storage_context="dry"), indent=2))

    print()
    print("=" * 60)
    print("CASE 4 — chelation_adequacy edge cases")
    print("=" * 60)
    for ratio in [None, 0.5, 2.0, 5.0]:
        ca = chelation_adequacy(ratio)
        print(f"  ratio={ratio!r:>5}  =>  tier={ca['tier']!r}")
