"""Use-case-specific compatibility gate profiles.

This module keeps the existing hydration osmolality calculator intact while
adding a thin routing layer for product formats whose risk surfaces differ:
hydration drinks, acute oral-mucosal/sublingual boluses, dry products, and wet
concentrates.  The goal is to prevent a single ORS gate from creating false
blocks (dry products) or false passes (wet concentrates marketed as hydration).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from compat.osmolality import HYPERTONIC_GATE, osmolality_report
from compat.solubility import additive_report

UseCase = Literal[
    "hydration_drink",
    "acute_sublingual",
    "dry_capsule",
    "dry_premix",
    "wet_concentrate",
    "wet_core_diluted",
]

_ALLOWED_CLAIMS = {
    "hydration_drink": ["hydration"],
    "acute_sublingual": ["oral_mucosal_tolerance_only"],
    "dry_capsule": ["dry_preload_only"],
    "dry_premix": ["dry_preload_only"],
    "wet_concentrate": ["hydration_only_at_labeled_dilution", "stored_liquid_requires_validation"],
    "wet_core_diluted": ["hydration_only_at_labeled_dilution", "stored_liquid_requires_validation"],
}

_DRY_CHECKS = [
    "water_activity_or_moisture_spec",
    "hygroscopicity_caking_control",
    "dose_uniformity_or_blend_uniformity",
    "oxygen_light_packaging_control",
]

_WET_STORAGE_CHECKS = [
    "preservative_or_make_fresh_protocol",
    "microbial_challenge_or_short_shelf_limit",
    "maillard_reducing_sugar_amine_review",
    "redox_light_oxygen_packaging_review",
    "emulsion_or_phase_stability_if_oil_present",
]


@dataclass(frozen=True)
class UseCaseProfile:
    """Declarative summary of a product/use-case gate profile."""

    use_case: UseCase
    required_inputs: list[str]
    blocking_gates: list[str]
    advisory_gates: list[str]
    allowed_claims: list[str]
    notes: str


def get_use_case_profile(use_case: UseCase) -> UseCaseProfile:
    """Return the configured gate profile for a use case."""
    if use_case == "hydration_drink":
        return UseCaseProfile(
            use_case=use_case,
            required_inputs=["components", "final_delivered_volume_ml"],
            blocking_gates=["delivered_osmolality", "sodium_present_for_ors_claim"],
            advisory_gates=["glucose_to_sodium_ratio", "same_day_reconstitution_or_preservation"],
            allowed_claims=_ALLOWED_CLAIMS[use_case],
            notes="Swallowed hydration claims use the delivered-volume ORS gate.",
        )
    if use_case == "acute_sublingual":
        return UseCaseProfile(
            use_case=use_case,
            required_inputs=["components", "bolus_or_contact_volume_ml", "pH", "contact_time"],
            blocking_gates=["irritant_pH_or_excipient_failure"],
            advisory_gates=["bolus_osmolality", "repeat_use_tolerance", "hydration_claim_not_allowed"],
            allowed_claims=_ALLOWED_CLAIMS[use_case],
            notes="Short-contact oral-mucosal use is not automatically blocked by the ORS hypertonic gate.",
        )
    if use_case in {"dry_capsule", "dry_premix"}:
        return UseCaseProfile(
            use_case=use_case,
            required_inputs=["components", "no_standing_liquid_claim"],
            blocking_gates=["standing_liquid_claim_requires_hydration_gate"],
            advisory_gates=_DRY_CHECKS,
            allowed_claims=_ALLOWED_CLAIMS[use_case],
            notes="Dry products are exempt from solution osmolality only when no label dissolution claim exists.",
        )
    if use_case in {"wet_concentrate", "wet_core_diluted"}:
        return UseCaseProfile(
            use_case=use_case,
            required_inputs=["concentrate_components", "concentrate_volume_ml", "final_components", "final_delivered_volume_ml"],
            blocking_gates=["final_delivered_osmolality_if_hydration_claim", "neat_use_hydration_claim"],
            advisory_gates=["concentrate_solubility_tds", *_WET_STORAGE_CHECKS],
            allowed_claims=_ALLOWED_CLAIMS[use_case],
            notes="Evaluate both the stored concentrate risk and the labeled final dilution.",
        )
    raise ValueError(f"unknown use_case: {use_case}")


def _liquid_gate(components: list[tuple[str, float]], water_ml: float) -> dict:
    report = osmolality_report(components, water_ml=water_ml)
    gate = report["ors_gate"]
    return {
        "water_ml": water_ml,
        "total_mosm_per_l": gate["total_mosm_per_l"],
        "verdict": gate["verdict"],
        "hydration_blocking": report["blocking"],
        "electrolyte_balance": report["electrolyte_balance"],
        "unknown_molar_mass": report["osmolarity"]["unknown_molar_mass"],
        "source_report": report,
    }


def use_case_gate_report(
    components: list[tuple[str, float]],
    *,
    use_case: UseCase,
    water_ml: float | None = None,
    standing_liquid_claim: bool = False,
    hydration_claim: bool = False,
    ph: float | None = None,
    concentrate_components: list[tuple[str, float]] | None = None,
    concentrate_water_ml: float | None = None,
) -> dict:
    """Evaluate components through a product/use-case-specific gate profile.

    Parameters intentionally stay small and explicit.  For wet concentrates,
    `components`/`water_ml` represent the final labeled dilution; optional
    `concentrate_components`/`concentrate_water_ml` represent stored bottle
    strength for solubility/TDS advisory checks.
    """
    profile = get_use_case_profile(use_case)
    result: dict = {
        "use_case": use_case,
        "profile": {
            "required_inputs": profile.required_inputs,
            "blocking_gates": profile.blocking_gates,
            "advisory_gates": profile.advisory_gates,
            "allowed_claims": profile.allowed_claims,
            "notes": profile.notes,
        },
        "label_claim_allowed": profile.allowed_claims[0],
        "hydration_blocking": False,
        "osmolality_exempt": False,
        "advisories": [],
        "blocking_reasons": [],
    }

    if use_case == "hydration_drink":
        if water_ml is None:
            result["hydration_blocking"] = True
            result["blocking_reasons"].append("final_delivered_volume_ml required for hydration gate")
            return result
        liquid = _liquid_gate(components, water_ml)
        result["liquid_gate"] = liquid
        result["hydration_blocking"] = liquid["hydration_blocking"]
        if liquid["hydration_blocking"]:
            result["blocking_reasons"].append("delivered hydration ORS gate failed")
        return result

    if use_case == "acute_sublingual":
        if water_ml is not None:
            liquid = _liquid_gate(components, water_ml)
            result["liquid_gate"] = liquid
            mosm = liquid["total_mosm_per_l"]
            if mosm <= 1000 and (ph is None or 5.8 <= ph <= 6.5):
                result["mucosal_tolerance_advisory"] = "conditional_pass"
            elif mosm <= HYPERTONIC_GATE:
                result["mucosal_tolerance_advisory"] = "low_osmotic_caution"
            else:
                result["mucosal_tolerance_advisory"] = "caution"
            result["advisories"].append("ORS osmolality is advisory for short-contact oral-mucosal use, not a hydration PASS")
        else:
            result["advisories"].append("bolus volume not supplied; mucosal osmolality not computed")
        if hydration_claim:
            result["hydration_blocking"] = True
            result["blocking_reasons"].append("acute sublingual profile cannot carry hydration claim without separate swallowed-volume ORS pass")
        return result

    if use_case in {"dry_capsule", "dry_premix"}:
        if not standing_liquid_claim and water_ml is None:
            result["osmolality_exempt"] = True
            result["dry_state_advisory"] = _DRY_CHECKS
            result["advisories"].append("no standing liquid exists; use dry-state controls instead of solution osmolality")
            return result
        if water_ml is None:
            result["hydration_blocking"] = True
            result["blocking_reasons"].append("standing liquid/dissolution claim requires a labeled water volume")
            return result
        liquid = _liquid_gate(components, water_ml)
        result["liquid_gate"] = liquid
        result["hydration_blocking"] = liquid["hydration_blocking"]
        if liquid["hydration_blocking"]:
            result["blocking_reasons"].append("dissolved dry product failed hydration gate at labeled volume")
        return result

    if use_case in {"wet_concentrate", "wet_core_diluted"}:
        if water_ml is None:
            result["hydration_blocking"] = True
            result["blocking_reasons"].append("final_delivered_volume_ml required for concentrate dilution gate")
            return result
        final_gate = _liquid_gate(components, water_ml)
        result["final_dilution_gate"] = final_gate
        if hydration_claim and final_gate["hydration_blocking"]:
            result["hydration_blocking"] = True
            result["blocking_reasons"].append("labeled final dilution failed hydration ORS gate")
        if concentrate_components is not None and concentrate_water_ml is not None:
            conc_sol = additive_report(concentrate_components, water_ml=concentrate_water_ml)
            result["concentrate_solubility_advisory"] = {
                "water_ml": concentrate_water_ml,
                "tds_w_v_pct": conc_sol["tds"]["w_v_pct"],
                "bottleneck_count": len(conc_sol["bottlenecks"]),
                "salting_out_flag": conc_sol["tds"]["salting_out_flag"],
            }
        else:
            result["advisories"].append("stored-concentrate solubility/TDS not computed; provide concentrate strength inputs")
        result["storage_stability_advisory"] = _WET_STORAGE_CHECKS
        result["advisories"].append("PASS can apply only to labeled final dilution; stored concentrate still needs stability validation")
        return result

    raise ValueError(f"unknown use_case: {use_case}")
