"""
Reformulated LIQUID drench — tuned to PASS the LEVER 0 biological gate.

Design moves vs the failing 1542 mOsm/L demo:
  - REMOVED glycerin (724 mOsm/L, a cosolvent — the single biggest offender).
  - DROPPED dextrose from 80 g/L to a WHO-ORS cotransport level (~14 g/L).
  - ADDED a Na/K/Cl premix (NaCl + KCl + trisodium citrate) so sodium can
    drive SGLT1 glucose-Na water uptake — turns it into a complete ORS.
  - MOVED creatine, tyrosine, betaine, carnitine, arginine, glutamine, etc.
    to the DRY/CAPSULE SKU (insoluble at dose and/or high osmotic cost; they
    are not hydration agents and do not belong in a standing ORS solution).
  - KEPT only low-osmotic-cost water-soluble actives: ascorbate, a little
    beta-alanine and D-ribose.

Concentrations are expressed per 1 L (osmolarity is concentration-based, so
the same recipe holds at any drench volume).
"""

from compat.osmolality import osmolality_report
from compat.solubility import additive_report
from compat.redox import flag_from_components
from compat.activity import ionic_strength
from compat.water_activity import aw_report

WATER_ML: float = 1000.0  # express per litre

# (name, grams per litre)
LIQUID_ORS: list[tuple[str, float]] = [
    ("dextrose",            14.0),  # ~75 mmol/L glucose — SGLT1 cotransport level
    ("sodium_chloride",      2.6),  # Na ~44.5, Cl ~44.5 mmol/L
    ("potassium_chloride",   1.5),  # K ~20.1 mmol/L
    ("trisodium_citrate",    2.9),  # Na ~29.6 mmol/L + citrate buffer/base
    ("ascorbic_acid",        0.5),  # vitamin C, low osmotic cost
    ("beta_alanine",         1.0),  # small carnosine-precursor dose
    ("d_ribose",             2.0),  # small energy-substrate dose
]

# WHO low-osmolarity ORS reference (mmol/L) for comparison.
WHO_ORS = {"na": 75, "k": 20, "cl": 65, "glucose": 75, "osmolarity": 245}


def main() -> None:
    print("=" * 70)
    print("  REFORMULATED LIQUID DRENCH (per 1 L) — LEVER 0 re-check")
    print("=" * 70)

    osmo = osmolality_report(LIQUID_ORS, water_ml=WATER_ML)
    gate = osmo["ors_gate"]
    electro = osmo["electrolyte_balance"]

    print(f"\n  Osmolarity : {gate['total_mosm_per_l']:.0f} mOsm/L  ->  {gate['verdict']}")
    print(f"  Reference  : WHO ORS ~{gate['who_ors_ref']:.0f}; avian isotonic "
          f"{gate['avian_isotonic_ref'][0]:.0f}-{gate['avian_isotonic_ref'][1]:.0f}")
    print(f"  Note       : {gate['note']}")

    print(f"\n  Electrolytes (mmol/L):  Na {electro['na_mmol_per_l']:.1f}  "
          f"K {electro['k_mmol_per_l']:.1f}  Cl {electro['cl_mmol_per_l']:.1f}")
    print(f"  Glucose     (mmol/L):  {electro['glucose_mmol_per_l']:.1f}  "
          f"glucose:Na {electro['glucose_to_na_ratio']:.2f}")
    print(f"  WHO ORS ref :           Na {WHO_ORS['na']}  K {WHO_ORS['k']}  Cl {WHO_ORS['cl']}  "
          f"glucose {WHO_ORS['glucose']}")
    print(f"  Complete ORS? {'YES' if electro['complete_ors'] else 'NO'} — {electro['reason']}")
    if electro['completeness_warnings']:
        print(f"  ORS warnings: {'; '.join(electro['completeness_warnings'])}")

    print("\n  Osmotic contributions (mOsm/L):")
    for c in sorted(
        (x for x in osmo["osmolarity"]["contributions"] if x["mosm_per_l"] is not None),
        key=lambda x: x["mosm_per_l"], reverse=True,
    ):
        print(f"    {c['name']:<22} {c['mosm_per_l']:7.1f}")

    # Solubility sanity — everything must dissolve at these low concentrations.
    sol = additive_report(LIQUID_ORS, water_ml=WATER_ML)
    print(f"\n  TDS: {sol['tds']['total_dissolved_g']:.1f} g/L "
          f"({sol['tds']['w_v_pct']:.2f} %w/v)  bottlenecks: "
          f"{len(sol['bottlenecks'])}")

    print("\n" + "=" * 70)
    verdict = "PASS — within isotonic band + complete ORS" if not osmo["blocking"] else "STILL BLOCKING"
    print(f"  LEVER 0 VERDICT: {verdict}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # TIER-0 ADVISORY FLAGS (Codex-list): redox, ionic strength, water activity
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  TIER-0 ADVISORY FLAGS")
    print("=" * 70)

    # Redox: ascorbate metal/O2 risk. Citrate present (chelator), no copper here.
    redox = flag_from_components(LIQUID_ORS, oxygen_exposure="headspace", light_exposure="clear")
    if redox.get("applicable", True):
        print(f"\n  Ascorbate redox risk : {redox['risk_level']}")
        print(f"    drivers   : {', '.join(redox['drivers']) or 'none'}")
        print(f"    mitigations: {'; '.join(redox['mitigations'])}")
        print(f"    Ea note   : {redox['ea_note']}")

    # Ionic strength (Davies validity + salting context)
    ionic = ionic_strength(LIQUID_ORS, water_ml=WATER_ML)
    print(f"\n  Ionic strength : {ionic['I_mol_per_l']:.3f} mol/L  ({ionic['note']})")

    # Water activity / microbial
    aw = aw_report(LIQUID_ORS, water_ml=WATER_ML)
    print(f"\n  Water activity : {aw['aw_raoult']:.4f}  ->  {aw['microbial_class']}")
    print(f"    {aw['threshold_note']}")
    print(f"    {aw['preservation_flag']}")


if __name__ == "__main__":
    main()
