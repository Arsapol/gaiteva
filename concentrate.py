"""
5x liquid CONCENTRATE of the fight-day drink: dose 1 cc concentrate + 4 cc water
(1:5 total -> concentrate is 5x final strength).

Checks the two things that change when you go from a make-fresh DRY stick to a
STORED LIQUID concentrate:
  1. Solubility at 5x strength (does everything still dissolve in the concentrate?)
  2. Final osmolality after 1:4 dilution (what the bird actually drinks).

It also surfaces the STABILITY REGRESSION: a standing liquid reintroduces the
Maillard + microbial problems the dry design removed. That is a real cost, not a
formatting detail — see the warning block.
"""

from compat.solubility import additive_report
from compat.osmolality import osmolality_report

DILUTION = 5.0  # 1 part concentrate + 4 parts water = 5x concentrate
CONCENTRATE_BATCH_ML = 100.0

# Final drink, per 1 L (canonical vNext2 fight-day drink).
FINAL_PER_L: list[tuple[str, float]] = [
    ("dextrose_monohydrate", 22.0),
    ("d_ribose",              5.0),
    ("sodium_chloride",       2.9),
    ("potassium_chloride",    1.1),
    ("l_citrulline",          1.15),
    ("citric_acid",           0.7),
    ("dmg",                   0.4),
    ("trisodium_citrate",     0.3),
]

# Maillard partners present in a stored liquid: reducing sugars + free amines.
REDUCING_SUGARS = {"d_ribose", "dextrose_monohydrate", "dextrose"}
FREE_AMINES = {"l_citrulline", "l_arginine", "l_glutamine", "beta_alanine"}


def concentrate_per_l() -> list[tuple[str, float]]:
    """Concentrate g/L = final g/L * dilution factor."""
    return [(n, g * DILUTION) for n, g in FINAL_PER_L]


def main() -> None:
    conc = concentrate_per_l()

    print("=" * 74)
    print("  5x LIQUID CONCENTRATE  (dose: 1 cc concentrate + 4 cc water = 5 cc)")
    print("=" * 74)

    # --- Concentrate prep sheet ---
    print(f"\n  CONCENTRATE prep (per {int(CONCENTRATE_BATCH_ML)} mL bottle, and per 1 L):")
    print(f"  {'Ingredient':<26}{'g/100mL':>10}{'g/1L':>10}")
    print("  " + "-" * 44)
    total = 0.0
    for n, g_per_l in conc:
        print(f"  {n:<26}{g_per_l/10:>10.3f}{g_per_l:>10.2f}")
        total += g_per_l
    print("  " + "-" * 44)
    print(f"  {'TOTAL solids':<26}{total/10:>10.3f}{total:>10.2f}")

    # --- 1. Solubility at concentrate strength ---
    print("\n  [1] SOLUBILITY at 5x strength (must all dissolve in the concentrate):")
    sol = additive_report(conc, water_ml=1000.0)
    print(f"      TDS {sol['tds']['w_v_pct']:.1f} %w/v   bottlenecks: {len(sol['bottlenecks'])}")
    for s in sol["substances"]:
        if not s["dissolved"]:
            print(f"      [!] {s['name']} undissolved {s['undissolved_g']:.2f} g")
    if not sol["bottlenecks"]:
        print("      OK — all freely soluble even at 5x (highest user = DMG, small).")
    if sol["tds"]["salting_out_flag"]:
        print("      [!] TDS > 20 %w/v — salting-out / crystallization-on-cooling risk in the bottle.")

    # --- 2. Final osmolality after 1:4 dilution ---
    print("\n  [2] FINAL after 1:4 dilution (what the bird drinks):")
    osmo = osmolality_report(FINAL_PER_L, water_ml=1000.0)
    g = osmo["ors_gate"]
    e = osmo["electrolyte_balance"]
    print(f"      {g['total_mosm_per_l']:.0f} mOsm/L -> {g['verdict']}   "
          f"Na {e['na_mmol_per_l']:.0f} / K {e['k_mmol_per_l']:.0f} / "
          f"Cl {e['cl_mmol_per_l']:.0f} mmol/L  "
          f"glucose {e['glucose_mmol_per_l']:.0f} mmol/L  "
          f"glucose:Na {e['glucose_to_na_ratio']:.2f}  "
          f"complete ORS: {'YES' if e['complete_ors'] else 'NO'}")
    print("      (dilution does not change the FINAL concentration -> same 291 mOsm/L PASS)")

    # --- 3. Stability regression warning ---
    names = {n for n, _ in conc}
    sugars = sorted(names & REDUCING_SUGARS)
    amines = sorted(names & FREE_AMINES)
    print("\n  [3] STABILITY REGRESSION (liquid concentrate undoes the dry design):")
    print(f"      Maillard partners present: sugars {sugars} + amines {amines}")
    print("      -> reducing sugar + free amine in a STORED liquid = browning over time.")
    print("         D-ribose is the MOST Maillard-reactive sugar; this is the main risk.")
    print(f"      Microbial: high water activity (~0.97 at {total/10:.0f} g/100mL) -> needs a")
    print("         preservative system OR refrigeration OR short shelf (make weekly).")
    print("      Mitigations, best first:")
    print("        a) keep ribose + citrulline DRY; liquid-concentrate only the stable")
    print("           electrolyte/acid/dextrose fraction (loses single-bottle convenience).")
    print("        b) acidify hard (citric, pH <3.5), refrigerate, opaque bottle, 2-4 wk shelf.")
    print("        c) validated preservative + accelerated-stability (Tier 2) before any claim.")
    print("      NOTE: low pH suppresses Maillard (<pH4) but does NOT stop ribose browning")
    print("            or yeast/mold fully; bench stability data is required for a real shelf life.")

    print("\n" + "=" * 74)
    verdict = "SOLUBLE + dilutes to a PASS drink" if not sol["bottlenecks"] and not osmo["blocking"] else "CHECK FLAGS"
    print(f"  VERDICT: {verdict}; STABILITY = the open question (see [3]).")
    print("=" * 74)


if __name__ == "__main__":
    main()
