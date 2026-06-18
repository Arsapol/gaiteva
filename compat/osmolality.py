"""
Osmolality / tonicity + electrolyte-balance gate for a water-based avian
oral-hydration product.

WHY THIS IS A BLOCKING LEVER (not advisory)
-------------------------------------------
For an oral rehydration product the FIRST biological gate is the osmotic and
electrolyte load at the actual bolus concentration — not chemical stability.
A hyperosmolar drench pulls water INTO the crop/gut lumen, slows transit, and
worsens fluid loss, so it can fail as a hydration aid even when every chemistry
check passes. Water uptake in the gut is driven by Na+/glucose cotransport
(SGLT1); without sodium, glucose alone does not pull water across the mucosa.

Reference ranges
----------------
  WHO low-osmolarity ORS : ~245 mOsm/L  (target band for rehydration)
  Avian isotonic plasma  : ~300-320 mOsm/L
  Practical drench gate  : <= ~330 mOsm/L isotonic-ish; > ~350 hypertonic risk

Only the DISSOLVED fraction of each solute contributes osmoles. Solutes over
their solubility ceiling (e.g. tyrosine, creatine at drench dose) contribute
only up to the ceiling — the undissolved crystals are not osmotically active.

All functions are pure and return new objects (no mutation).
"""

from __future__ import annotations

from compat.data import (
    SUBSTANCES,
    MOLAR_MASS_G_PER_MOL,
    OSMOTIC_N,
    ELECTROLYTE_IONS,
)

# Reference osmolarity constants (mOsm/L).
WHO_ORS_OSMOLARITY: float = 245.0
AVIAN_ISOTONIC_LOW: float = 300.0
AVIAN_ISOTONIC_HIGH: float = 320.0
HYPERTONIC_GATE: float = 350.0

# Minimal screening targets for a hydration/ORS claim. These are intentionally
# broad project gates, not species-specific clinical limits. They prevent the
# old trace-sodium false PASS while keeping the existing golden fixtures valid.
MIN_NA_MMOL_PER_L: float = 45.0
MIN_K_MMOL_PER_L: float = 10.0
MIN_CL_MMOL_PER_L: float = 30.0
MIN_GLUCOSE_MMOL_PER_L: float = 30.0
GLUCOSE_NA_RATIO_MIN: float = 0.5
GLUCOSE_NA_RATIO_MAX: float = 2.5
GLUCOSE_SOURCES: frozenset[str] = frozenset({"dextrose", "dextrose_monohydrate"})


def _dissolved_grams(name: str, grams: float, water_ml: float) -> float:
    """Grams of `name` actually in solution (capped at its solubility ceiling).

    Miscible solutes (ceiling None, e.g. glycerin) are fully dissolved.
    Unknown solutes (not in SUBSTANCES) are treated as fully dissolved.
    """
    entry = SUBSTANCES.get(name)
    if entry is None:
        return grams
    ceiling = entry.get("solubility_g_per_100ml_25c")
    if ceiling is None:  # miscible
        return grams
    max_dissolved = ceiling * (water_ml / 100.0)
    return min(grams, max_dissolved)


def solute_osmoles(name: str, grams: float, water_ml: float) -> dict:
    """Osmolarity contribution (mOsm/L) of one solute's dissolved fraction.

    Returns a dict; mosm_per_l is None when molar mass is unknown (cannot
    convert) so the caller can surface the gap rather than silently drop it.
    """
    dissolved_g = _dissolved_grams(name, grams, water_ml)
    mw = MOLAR_MASS_G_PER_MOL.get(name)
    n = OSMOTIC_N.get(name, 1.0)
    if mw is None or water_ml <= 0:
        return {
            "name": name,
            "dissolved_g": dissolved_g,
            "mosm_per_l": None,
            "reason": "molar mass unknown — cannot convert to osmoles",
        }
    liters = water_ml / 1000.0
    mol = dissolved_g / mw
    mosm = (mol * n / liters) * 1000.0
    return {
        "name": name,
        "dissolved_g": dissolved_g,
        "osmotic_n": n,
        "mosm_per_l": mosm,
    }


def estimate_osmolarity(components: list[tuple[str, float]], water_ml: float) -> dict:
    """Total osmolarity (mOsm/L) from the dissolved fraction of all components."""
    contributions = [solute_osmoles(n, g, water_ml) for n, g in components]
    total = sum(c["mosm_per_l"] for c in contributions if c["mosm_per_l"] is not None)
    unknown = [c["name"] for c in contributions if c["mosm_per_l"] is None]
    return {
        "total_mosm_per_l": total,
        "contributions": contributions,
        "unknown_molar_mass": unknown,
    }


def electrolyte_balance(components: list[tuple[str, float]], water_ml: float | None = None) -> dict:
    """Na/K/Cl and glucose load with optional volume-aware ORS screening.

    Historical callers only received absolute millimoles. When ``water_ml`` is
    supplied, the report also exposes mmol/L fields and uses those
    concentrations plus glucose:Na ratio for the ORS completeness gate.
    """
    na = k = cl = glucose = 0.0
    sources: list[str] = []
    glucose_sources: list[str] = []
    unknown_glucose_sources: list[str] = []

    for name, grams in components:
        ions = ELECTROLYTE_IONS.get(name)
        if ions:
            sources.append(name)
            na += ions.get("na_mmol_per_g", 0.0) * grams
            k += ions.get("k_mmol_per_g", 0.0) * grams
            cl += ions.get("cl_mmol_per_g", 0.0) * grams

        if name in GLUCOSE_SOURCES:
            glucose_sources.append(name)
            mw = MOLAR_MASS_G_PER_MOL.get(name)
            if mw is None:
                unknown_glucose_sources.append(name)
            else:
                glucose += (grams / mw) * 1000.0

    liters = water_ml / 1000.0 if water_ml and water_ml > 0 else None

    def per_l(mmol: float) -> float | None:
        return mmol / liters if liters else None

    na_l = per_l(na)
    k_l = per_l(k)
    cl_l = per_l(cl)
    glucose_l = per_l(glucose)
    glucose_to_na = (glucose / na) if na > 0.0 and glucose > 0.0 else None

    completeness_warnings: list[str] = []
    if unknown_glucose_sources:
        completeness_warnings.append(
            "glucose source molar mass unknown: " + ", ".join(unknown_glucose_sources)
        )

    if liters is None:
        complete = False
        completeness_warnings.append("water_ml required for volume-aware ORS completeness gate")
        if na <= 0.0:
            completeness_warnings.append("no sodium source present")
        reason = (
            "INSUFFICIENT_DATA — water_ml required to evaluate Na/K/Cl mmol/L and glucose:Na ORS gate. "
            "Trace sodium alone is not a complete ORS pass."
        )
    else:
        checks = [
            (na_l is not None and na_l >= MIN_NA_MMOL_PER_L,
             f"Na {na_l:.1f} mmol/L below {MIN_NA_MMOL_PER_L:.0f}" if na_l is not None else "Na mmol/L unavailable"),
            (k_l is not None and k_l >= MIN_K_MMOL_PER_L,
             f"K {k_l:.1f} mmol/L below {MIN_K_MMOL_PER_L:.0f}" if k_l is not None else "K mmol/L unavailable"),
            (cl_l is not None and cl_l >= MIN_CL_MMOL_PER_L,
             f"Cl {cl_l:.1f} mmol/L below {MIN_CL_MMOL_PER_L:.0f}" if cl_l is not None else "Cl mmol/L unavailable"),
            (glucose_l is not None and glucose_l >= MIN_GLUCOSE_MMOL_PER_L,
             f"glucose {glucose_l:.1f} mmol/L below {MIN_GLUCOSE_MMOL_PER_L:.0f}" if glucose_l is not None else "glucose mmol/L unavailable"),
            (glucose_to_na is not None and GLUCOSE_NA_RATIO_MIN <= glucose_to_na <= GLUCOSE_NA_RATIO_MAX,
             (f"glucose:Na ratio {glucose_to_na:.2f} outside "
              f"{GLUCOSE_NA_RATIO_MIN:.1f}-{GLUCOSE_NA_RATIO_MAX:.1f}")
             if glucose_to_na is not None else "glucose:Na ratio unavailable"),
        ]
        completeness_warnings.extend(message for ok, message in checks if not ok)
        complete = not completeness_warnings
        reason = (
            "OK — Na/K/Cl, glucose, and glucose:Na ratio support an ORS hydration claim"
            if complete
            else "BLOCKING — incomplete ORS hydration profile: " + "; ".join(completeness_warnings)
        )

    return {
        # Historical absolute totals (mmol per recipe/dose).
        "na_mmol": na,
        "k_mmol": k,
        "cl_mmol": cl,
        "glucose_mmol": glucose,
        # Volume-aware delivered concentrations.
        "na_mmol_per_l": na_l,
        "k_mmol_per_l": k_l,
        "cl_mmol_per_l": cl_l,
        "glucose_mmol_per_l": glucose_l,
        "glucose_to_na_ratio": glucose_to_na,
        "electrolyte_sources": sources,
        "glucose_sources": glucose_sources,
        "completeness_warnings": completeness_warnings,
        "complete_ors": complete,
        "ors_targets": {
            "na_min_mmol_per_l": MIN_NA_MMOL_PER_L,
            "k_min_mmol_per_l": MIN_K_MMOL_PER_L,
            "cl_min_mmol_per_l": MIN_CL_MMOL_PER_L,
            "glucose_min_mmol_per_l": MIN_GLUCOSE_MMOL_PER_L,
            "glucose_to_na_ratio_range": [GLUCOSE_NA_RATIO_MIN, GLUCOSE_NA_RATIO_MAX],
        },
        "reason": reason,
    }


def ors_gate(total_mosm_per_l: float) -> dict:
    """Classify osmolarity against ORS / avian isotonic bands. BLOCKING verdict."""
    if total_mosm_per_l <= AVIAN_ISOTONIC_HIGH:
        verdict = "PASS"
        note = f"<= {AVIAN_ISOTONIC_HIGH:.0f} mOsm/L — within isotonic-ish hydration band"
    elif total_mosm_per_l <= HYPERTONIC_GATE:
        verdict = "MARGINAL"
        note = (
            f"{AVIAN_ISOTONIC_HIGH:.0f}-{HYPERTONIC_GATE:.0f} mOsm/L — above isotonic; "
            "dilute or reduce solute load"
        )
    else:
        verdict = "BLOCK"
        note = (
            f"> {HYPERTONIC_GATE:.0f} mOsm/L — HYPERTONIC. Pulls water into gut lumen, "
            "worsens dehydration. Must dilute / cut dose before use as hydration aid."
        )
    return {
        "total_mosm_per_l": total_mosm_per_l,
        "verdict": verdict,
        "note": note,
        "who_ors_ref": WHO_ORS_OSMOLARITY,
        "avian_isotonic_ref": [AVIAN_ISOTONIC_LOW, AVIAN_ISOTONIC_HIGH],
    }


def osmolality_report(components: list[tuple[str, float]], water_ml: float) -> dict:
    """Full blocking gate: osmolarity + ORS classification + electrolyte balance."""
    osm = estimate_osmolarity(components, water_ml)
    gate = ors_gate(osm["total_mosm_per_l"])
    electro = electrolyte_balance(components, water_ml=water_ml)
    blocking = gate["verdict"] == "BLOCK" or not electro["complete_ors"]
    return {
        "water_ml": water_ml,
        "osmolarity": osm,
        "ors_gate": gate,
        "electrolyte_balance": electro,
        "blocking": blocking,
    }


if __name__ == "__main__":
    demo_components = [
        ("l_tyrosine", 0.5),
        ("creatine_monohydrate", 5.0),
        ("dextrose", 12.0),
        ("ascorbic_acid", 2.0),
        ("citric_acid", 1.5),
        ("beta_alanine", 2.0),
        ("glycerin", 10.0),
    ]
    report = osmolality_report(demo_components, water_ml=150.0)
    print("BLOCKING:", report["blocking"])
    print(f"Osmolarity: {report['ors_gate']['total_mosm_per_l']:.0f} mOsm/L "
          f"-> {report['ors_gate']['verdict']}")
    print("Note      :", report["ors_gate"]["note"])
    print("Electrolyte:", report["electrolyte_balance"]["reason"])
    print("\nPer-solute osmolarity (dissolved fraction only):")
    for c in report["osmolarity"]["contributions"]:
        if c["mosm_per_l"] is not None:
            print(f"  {c['name']:<24} {c['dissolved_g']:6.3f} g  ->  {c['mosm_per_l']:7.1f} mOsm/L")
        else:
            print(f"  {c['name']:<24} {c['reason']}")
