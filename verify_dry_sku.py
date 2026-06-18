"""
Verify the DRY-SKU set (vNext2, wiki) against the calculator gates.

Three dry products exist:
  1. ACUTE FOCUS BLEND (capsule)  — eaten DRY
  2. DRY PRELOAD PREMIX (top-dress) — eaten DRY
  3. FIGHT-DAY DRINK (dry stick -> 1 L water) — RECONSTITUTED

Only product 3 forms a standing solution, so only it sees the LEVER 0
osmolality gate. Products 1 & 2 are ingested dry: the relevant checks are
water activity / hygroscopicity / caking of the powder, not solution
osmolarity. We assert that here and run the osmolality gate on the drink only.

Drink composition reconstituted (33.55 g stick -> 1 L), per the standardized
per-100g page. Dextrose is the MONOHYDRATE form the formula specifies (matters
for the osmolarity margin vs the 300 mOsm/L cap).
"""

from compat.osmolality import osmolality_report
from compat.solubility import additive_report
from compat.redox import flag_from_components
from compat.activity import ionic_strength
from compat.water_activity import aw_report

WATER_ML: float = 1000.0

# Fight-day drink, reconstituted (g per 1 L).
FIGHT_DAY_DRINK: list[tuple[str, float]] = [
    ("dextrose_monohydrate", 22.0),
    ("d_ribose",              5.0),   # operator field-retained, separated from amino product
    ("sodium_chloride",       2.9),
    ("potassium_chloride",    1.1),
    ("l_citrulline",          1.15),
    ("citric_acid",           0.7),
    ("dmg",                   0.4),
    ("trisodium_citrate",     0.3),
]

WIKI_CLAIM = {"osmolarity": 291, "na": 53, "k": 15, "cl": 64}


def main() -> None:
    print("=" * 70)
    print("  DRY SKU GATE CHECK")
    print("=" * 70)
    print("\n  Products 1 (focus capsule) & 2 (preload premix): eaten DRY.")
    print("  -> No standing-solution osmolality gate. Governing checks are")
    print("     water-activity ~0 (dry), hygroscopicity, caking, dose uniformity.")
    print("     (betaine, DMG, trehalose dihydrate hygroscopic -> foil + desiccant.)")

    print("\n" + "=" * 70)
    print("  PRODUCT 3 — FIGHT-DAY DRINK (33.55 g stick -> 1 L) — LEVER 0")
    print("=" * 70)

    osmo = osmolality_report(FIGHT_DAY_DRINK, water_ml=WATER_ML)
    gate = osmo["ors_gate"]
    electro = osmo["electrolyte_balance"]

    print(f"\n  Osmolarity : {gate['total_mosm_per_l']:.0f} mOsm/L  ->  {gate['verdict']}"
          f"   (wiki claim ~{WIKI_CLAIM['osmolarity']})")
    print(f"  Note       : {gate['note']}")
    print(f"\n  Electrolytes (mmol/L): Na {electro['na_mmol_per_l']:.1f} (wiki ~{WIKI_CLAIM['na']})  "
          f"K {electro['k_mmol_per_l']:.1f} (wiki ~{WIKI_CLAIM['k']})  "
          f"Cl {electro['cl_mmol_per_l']:.1f} (wiki ~{WIKI_CLAIM['cl']})")
    print(f"  Glucose     (mmol/L): {electro['glucose_mmol_per_l']:.1f}  "
          f"glucose:Na {electro['glucose_to_na_ratio']:.2f}")
    print(f"  Complete ORS? {'YES' if electro['complete_ors'] else 'NO'} — {electro['reason']}")
    if electro['completeness_warnings']:
        print(f"  ORS warnings: {'; '.join(electro['completeness_warnings'])}")

    print("\n  Osmotic contributions (mOsm/L):")
    for c in sorted(
        (x for x in osmo["osmolarity"]["contributions"] if x["mosm_per_l"] is not None),
        key=lambda x: x["mosm_per_l"], reverse=True,
    ):
        print(f"    {c['name']:<24} {c['mosm_per_l']:7.1f}")

    sol = additive_report(FIGHT_DAY_DRINK, water_ml=WATER_ML)
    print(f"\n  TDS: {sol['tds']['total_dissolved_g']:.1f} g/L "
          f"({sol['tds']['w_v_pct']:.2f} %w/v)  bottlenecks: {len(sol['bottlenecks'])}")

    # Tier-0 flags (no ascorbate in this drink -> redox N/A).
    redox = flag_from_components(FIGHT_DAY_DRINK)
    print(f"\n  Redox (ascorbate): {'N/A — no ascorbate in drink' if not redox.get('applicable', True) else redox['risk_level']}")
    ionic = ionic_strength(FIGHT_DAY_DRINK, water_ml=WATER_ML)
    print(f"  Ionic strength : {ionic['I_mol_per_l']:.3f} mol/L")
    aw = aw_report(FIGHT_DAY_DRINK, water_ml=WATER_ML)
    print(f"  Water activity : {aw['aw_raoult']:.4f} -> {aw['microbial_class']} "
          f"(make-fresh/discard-same-day covers the brief wet window)")

    print("\n" + "=" * 70)
    margin = 300.0 - gate["total_mosm_per_l"]
    verdict = "PASS" if not osmo["blocking"] else "BLOCK"
    print(f"  DRINK VERDICT: {verdict}  (margin to 300 cap: {margin:+.0f} mOsm/L)")
    if gate["total_mosm_per_l"] > 300:
        print("  [!] over 300 cap — using ANHYDROUS dextrose instead of monohydrate")
        print("      would push it here; the formula's monohydrate spec is load-bearing.")
    print("=" * 70)


if __name__ == "__main__":
    main()
