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


def electrolyte_balance(components: list[tuple[str, float]]) -> dict:
    """Na/K/Cl load (mmol/L not computed without volume) + completeness flag.

    A recovery/hydration product needs sodium for SGLT1-driven water uptake.
    With no Na/K/Cl source among the components this returns complete_ors=False
    and an explicit blocking reason.
    """
    na = k = cl = 0.0
    sources: list[str] = []
    for name, grams in components:
        ions = ELECTROLYTE_IONS.get(name)
        if not ions:
            continue
        sources.append(name)
        na += ions.get("na_mmol_per_g", 0.0) * grams
        k += ions.get("k_mmol_per_g", 0.0) * grams
        cl += ions.get("cl_mmol_per_g", 0.0) * grams
    complete = na > 0.0
    return {
        "na_mmol": na,
        "k_mmol": k,
        "cl_mmol": cl,
        "electrolyte_sources": sources,
        "complete_ors": complete,
        "reason": (
            "OK — sodium present; SGLT1 glucose-Na cotransport can drive water uptake"
            if complete
            else "BLOCKING — no added Na/K/Cl. Glucose without sodium does NOT pull "
            "water across gut mucosa (SGLT1 needs Na+). Not a complete ORS; add a "
            "Na/K/Cl premix (e.g. NaCl + KCl + Na-citrate) before claiming hydration."
        ),
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
    electro = electrolyte_balance(components)
    blocking = gate["verdict"] == "BLOCK" or not electro["complete_ors"]
    return {
        "water_ml": water_ml,
        "osmolarity": osm,
        "ors_gate": gate,
        "electrolyte_balance": electro,
        "blocking": blocking,
    }


if __name__ == "__main__":
    import pprint

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
