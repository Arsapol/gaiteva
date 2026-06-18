"""
Bench prep sheets — grams per 100 mL (+ scaled batch columns).

Prints each PASSING recipe as g/100 mL plus the weigh-out mass for common test
volumes (100 / 250 / 500 / 1000 mL). Both recipes pass LEVER 0 (osmolality +
electrolyte). See compat/ for the gate math; reformulate.py / verify_dry_sku.py
for the gate runs.

WEIGHING NOTE: several actives are <0.1 g per 100 mL. A 100 mL test batch needs
a 0.001 g (1 mg) scale for those. If you only have a 0.01-0.1 g scale, weigh the
1 L batch (or a 10x master powder) and dilute — do NOT try to weigh 0.03 g
directly. Make fresh, offer same day, discard (no preservative).
"""

# (name, grams per 1 L)  — canonical vNext2 fight-day drink (the production stick)
FIGHT_DAY_DRINK_PER_L: list[tuple[str, float]] = [
    ("Dextrose monohydrate", 22.0),
    ("D-Ribose",              5.0),
    ("Sodium chloride (NaCl)", 2.9),
    ("Potassium chloride (KCl)", 1.1),
    ("L-Citrulline (free)",   1.15),
    ("Citric acid (anhydrous)", 0.7),
    ("DMG",                   0.4),
    ("Trisodium citrate dihydrate", 0.3),
]

# (name, grams per 1 L)  — reformulated WHO-style liquid ORS (rederived this session)
REFORMULATED_ORS_PER_L: list[tuple[str, float]] = [
    ("Dextrose",             14.0),
    ("Sodium chloride (NaCl)", 2.6),
    ("Potassium chloride (KCl)", 1.5),
    ("Trisodium citrate dihydrate", 2.9),
    ("Ascorbic acid (vit C)", 0.5),
    ("Beta-alanine",          1.0),
    ("D-Ribose",              2.0),
]

VOLUMES_ML: list[float] = [100.0, 250.0, 500.0, 1000.0]


def print_sheet(title: str, per_l: list[tuple[str, float]], summary: str) -> None:
    print("=" * 78)
    print(f"  {title}")
    print("=" * 78)
    header = f"  {'Ingredient':<32}{'g/100mL':>10}"
    for v in VOLUMES_ML:
        header += f"{int(v):>9}mL"
    print(header)
    print("  " + "-" * 74)

    total_per_l = 0.0
    for name, g_per_l in per_l:
        g_100 = g_per_l / 10.0
        row = f"  {name:<32}{g_100:>10.3f}"
        for v in VOLUMES_ML:
            row += f"{g_per_l * v / 1000.0:>11.3f}"
        print(row)
        total_per_l += g_per_l

    total_row = f"  {'TOTAL solids':<32}{total_per_l / 10.0:>10.3f}"
    for v in VOLUMES_ML:
        total_row += f"{total_per_l * v / 1000.0:>11.3f}"
    print("  " + "-" * 74)
    print(total_row)
    print(f"\n  {summary}")
    print("  Method: dissolve in COOL water, stir ~30 s until clear, offer fresh, discard same day.\n")


def main() -> None:
    print_sheet(
        "FIGHT-DAY DRINK (canonical vNext2 stick) — PASS 291 mOsm/L",
        FIGHT_DAY_DRINK_PER_L,
        "3.355 g/100 mL total. Complete ORS (Na 53 / K 15 / Cl 64 mM). "
        "Use dextrose MONOHYDRATE (anhydrous tips over the 300 mOsm cap).",
    )
    print_sheet(
        "REFORMULATED LIQUID ORS (session) — PASS 274 mOsm/L",
        REFORMULATED_ORS_PER_L,
        "2.45 g/100 mL total. Complete ORS (Na 74 / K 20 / Cl 65 mM, WHO-style).",
    )


if __name__ == "__main__":
    main()
