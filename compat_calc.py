"""
compat_calc.py — liquid-drench compatibility & stability demo.

Thin orchestrator that drives the compat package modules.  Run from the
project root:

    python3 compat_calc.py

APPLICABILITY HEADER (read before interpreting any output)
----------------------------------------------------------
  Gibbs       : BACKUP ONLY — thermodynamic spontaneity screen; kinetics
                govern actual rate, use formula-safety-check skill as PRIMARY.
  Hansen (Ra) : REMOVED — not valid for ionic salts, amino acids, or
                sugars dissolved in water; van-der-Waals model inapplicable
                to ionic/polar aqueous solutions.
  Stokes      : UNDISSOLVED-FRACTION ONLY — meaningful only for particles
                that remain solid in solution.  Fully dissolved actives
                produce no settling.
  HLB         : REMOVED — only relevant when an oil phase is present;
                this formula has no oil phase.
  Arrhenius   : PRIMARY per-pathway shelf-life projection.  Three registered
                pathways: ascorbate_oxidation, maillard_browning,
                creatine_cyclization.

THREE REAL LEVERS
-----------------
  1. ADDITIVE SOLUBILITY — identify undissolved bottlenecks and TDS
  2. pH 3.0–4.0 — citric acid buffering window for stability
  3. PER-PATHWAY ARRHENIUS — stress-study compression & ICH warnings
"""

from compat.solubility import additive_report
from compat.arrhenius import all_pathways
from compat.ph_module import ph_window_check, degradation_vs_ph
from compat.stokes import settling_report
from compat.gibbs import screen_pair
from compat.osmolality import osmolality_report

# ---------------------------------------------------------------------------
# Demo scenario: liquid drench for gamefowl
# Components include l_tyrosine and creatine_monohydrate so bottleneck
# warnings fire; the remaining substances are realistic carrier/actives.
# ---------------------------------------------------------------------------

WATER_ML: float = 150.0  # mL — one-day drench volume

COMPONENTS: list[tuple[str, float]] = [
    ("l_tyrosine",          0.5),   # ceiling 0.045 g/100 mL  → BOTTLENECK
    ("creatine_monohydrate", 5.0),  # ceiling 1.40 g/100 mL   → BOTTLENECK
    ("dextrose",           12.0),   # ceiling 91 g/100 mL     → fine
    ("ascorbic_acid",       2.0),   # ceiling 33 g/100 mL     → fine
    ("citric_acid",         1.5),   # ceiling 147 g/100 mL    → fine
    ("beta_alanine",        2.0),   # ceiling 55 g/100 mL     → fine
    ("glycerin",           10.0),   # miscible                → always fine
]

TARGET_PH: float = 3.5
# Tyrosine settling analysis — 50 µm crystal in water-like fluid
TYROSINE_PARTICLE_RADIUS_M: float = 50e-6   # 50 µm = aggressive fine grind
ETA_PA_S: float = 0.001                     # ≈ pure water; glycerin raises this


def _section(title: str) -> None:
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def _sub(label: str) -> None:
    print(f"\n--- {label} ---")


def run_demo() -> None:
    # ------------------------------------------------------------------
    # APPLICABILITY header
    # ------------------------------------------------------------------
    print("=" * 70)
    print("APPLICABILITY HEADER")
    print("-" * 70)
    print("  Gibbs    : BACKUP screen — dG<0 ≠ fast or dangerous in practice")
    print("  Hansen   : REMOVED — ionic/aqueous solutions out of scope")
    print("  Stokes   : UNDISSOLVED-FRACTION ONLY — not for dissolved actives")
    print("  HLB      : REMOVED — no oil phase in this formula")
    print("  Arrhenius: PRIMARY — per-pathway shelf-life from Ea data")
    print("-" * 70)
    print("GATE 0 (BLOCKING, biological): osmolality + Na/K/Cl balance")
    print("CHEM LEVERS: (1) additive solubility  (2) pH 3.0–4.0  (3) Arrhenius")
    print("=" * 70)

    # ------------------------------------------------------------------
    # LEVER 0 — BIOLOGICAL GATE: osmolality + electrolyte balance
    # Runs FIRST: for an oral-hydration product this is the first gate.
    # A hyperosmolar / electrolyte-incomplete drench fails as hydration even
    # if every chemistry check below passes.
    # ------------------------------------------------------------------
    _section("LEVER 0 — OSMOLALITY & ELECTROLYTE GATE  (biological, BLOCKING)")
    osmo = osmolality_report(COMPONENTS, water_ml=WATER_ML)
    gate = osmo["ors_gate"]
    electro = osmo["electrolyte_balance"]
    print(f"\n  Osmolarity : {gate['total_mosm_per_l']:.0f} mOsm/L  ->  {gate['verdict']}")
    print(f"  Reference  : WHO ORS ~{gate['who_ors_ref']:.0f}; avian isotonic "
          f"{gate['avian_isotonic_ref'][0]:.0f}-{gate['avian_isotonic_ref'][1]:.0f} mOsm/L")
    print(f"  Note       : {gate['note']}")
    print(f"\n  Electrolytes (mmol/L): Na {electro['na_mmol_per_l']:.1f}  "
          f"K {electro['k_mmol_per_l']:.1f}  Cl {electro['cl_mmol_per_l']:.1f}")
    glucose_ratio = electro['glucose_to_na_ratio']
    glucose_ratio_s = f"{glucose_ratio:.2f}" if glucose_ratio is not None else "N/A"
    print(f"  Glucose     (mmol/L): {electro['glucose_mmol_per_l']:.1f}  "
          f"glucose:Na {glucose_ratio_s}")
    print(f"  Electrolyte: complete ORS? {'YES' if electro['complete_ors'] else 'NO'}")
    print(f"  Reason     : {electro['reason']}")
    print("\n  Top osmotic contributors (dissolved fraction):")
    ranked = sorted(
        (c for c in osmo["osmolarity"]["contributions"] if c["mosm_per_l"] is not None),
        key=lambda c: c["mosm_per_l"],
        reverse=True,
    )
    for c in ranked[:4]:
        print(f"    {c['name']:<24} {c['mosm_per_l']:7.0f} mOsm/L")
    if osmo["blocking"]:
        print("\n  [BLOCK] Biological gate FAILED — fix osmolality/electrolytes "
              "before the chemistry levers matter.")

    # ------------------------------------------------------------------
    # LEVER 1 — Additive solubility / TDS
    # ------------------------------------------------------------------
    _section("LEVER 1 — ADDITIVE SOLUBILITY & TDS")
    report = additive_report(COMPONENTS, water_ml=WATER_ML)

    print(f"\nWater volume : {report['water_ml']:.0f} mL")
    print(f"TDS dissolved: {report['tds']['total_dissolved_g']:.2f} g")
    print(f"TDS %w/v     : {report['tds']['w_v_pct']:.2f} %")
    print(f"Salting-out? : {'YES — >20 % w/v' if report['tds']['salting_out_flag'] else 'no'}")

    _sub("Per-substance solubility")
    for s in report["substances"]:
        ceiling_str = (
            f"  ceiling {s['ceiling']} g/100 mL"
            if s["ceiling"] is not None
            else "  miscible"
        )
        status = "OK" if s["dissolved"] else f"BOTTLENECK ({s['undissolved_g']:.4f} g undissolved)"
        print(f"  {s['name']:<24} conc {s['conc_g_per_100ml']:8.4f} g/100mL"
              f"{ceiling_str:<30}  {status}")

    if report["bottlenecks"]:
        _sub("Bottlenecks (exceed solubility ceiling)")
        for b in report["bottlenecks"]:
            print(f"  [!] {b}")
    else:
        print("\n  No bottlenecks — all substances within solubility ceiling.")

    if report["supersaturation_warnings"]:
        _sub("Supersaturation-on-cooling risks")
        for w in report["supersaturation_warnings"]:
            print(f"  [!] {w}")

    # ------------------------------------------------------------------
    # LEVER 2 — pH window + degradation profile
    # ------------------------------------------------------------------
    _section(f"LEVER 2 — pH WINDOW & STABILITY  (target pH {TARGET_PH})")

    window = ph_window_check(TARGET_PH)
    print(f"\n  In window [{window['low']}, {window['high']}]: "
          f"{'YES' if window['in_window'] else 'NO'}")
    print(f"  Reason: {window['reason']}")

    degr = degradation_vs_ph(TARGET_PH)
    _sub(f"Degradation profile at pH {TARGET_PH}")
    print(f"  Ascorbate oxidation : {degr['ascorbate_oxidation']}")
    print(f"  Maillard browning   : {degr['maillard_browning']}")
    print(f"  Combined            : {degr['combined_recommendation']}")

    # ------------------------------------------------------------------
    # LEVER 3 — Arrhenius per-pathway projections (40 °C stress / 25 °C store)
    # ------------------------------------------------------------------
    _section("LEVER 3 — ARRHENIUS PER-PATHWAY PROJECTIONS  (40 °C stress / 25 °C store)")

    pathways = all_pathways(T_stress_C=40.0, T_store_C=25.0)
    for key, proj in pathways.items():
        print(f"\n  [{key}]")
        q_lo, q_typ, q_hi = proj["Q10_range"]
        a_lo, a_typ, a_hi = proj["AF_range"]
        print(f"    Q10      : {q_lo:.2f} – {q_typ:.2f} – {q_hi:.2f}  (low / typical / high Ea)")
        print(f"    AF       : {a_lo:.1f} – {a_typ:.1f} – {a_hi:.1f}x  (40 °C vs 25 °C)")
        print(f"    Stress wk for 24-mo equiv: {proj['weeks_stress_for_24mo_typical']:.1f} wk (typical Ea)")
        print(f"    ICH note : {proj['ich_warning']}")

    # ------------------------------------------------------------------
    # Stokes settling — tyrosine undissolved fraction
    # ------------------------------------------------------------------
    _section("STOKES SETTLING — L-Tyrosine (undissolved fraction)")
    # Retrieve tyrosine dose from COMPONENTS
    tyrosine_g = next(g for n, g in COMPONENTS if n == "l_tyrosine")
    stk = settling_report(
        name="l_tyrosine",
        dose_g=tyrosine_g,
        water_ml=WATER_ML,
        particle_radius_m=TYROSINE_PARTICLE_RADIUS_M,
        eta_pa_s=ETA_PA_S,
        bottle_height_m=0.10,
    )
    print(f"\n  Applicable : {stk['applicable']}")
    print(f"  Reason     : {stk['reason']}")
    if stk["applicable"]:
        v_um_s = stk["v"] * 1e6
        t_s = stk["settle_time_s"]
        t_h = t_s / 3600.0
        print(f"  Undissolved: {stk['undissolved_g']:.4f} g")
        print(f"  Velocity   : {v_um_s:.3f} µm/s")
        print(f"  Settle 10cm: {t_h:.2f} h  ({t_s:.0f} s)")
        print(f"  Lever: {stk['reduce_radius_effect']}")
        print(f"  Lever: {stk['raise_viscosity_effect']}")

    # ------------------------------------------------------------------
    # Gibbs backup screen — illustrative pair
    # ------------------------------------------------------------------
    _section("GIBBS BACKUP SCREEN — illustrative pair (ascorbic acid + creatine in acid)")
    # Illustrative: acid-catalysed creatine cyclisation is exothermic
    # dH ~ -5 kJ/mol (rough estimate for intramolecular ring-closure enthalpy)
    # dS ~ -20 J/(mol·K) (loss of rotational freedom on cyclisation)
    g_result = screen_pair(
        name_a="creatine_monohydrate",
        name_b="acidic_pH_environment",
        dH_J=-5_000,
        dS_J_per_K=-20.0,
    )
    print(f"\n  Pair   : {g_result['pair']}")
    print(f"  dG_kJ  : {g_result['gibbs_result']['dG_kJ']:.2f} kJ/mol")
    print(f"  Verdict: {g_result['gibbs_result']['verdict']}")
    print(f"  Caveat : {g_result['caveat']}")

    # ------------------------------------------------------------------
    # OVERALL VERDICT — biological gate dominates
    # ------------------------------------------------------------------
    _section("OVERALL VERDICT")
    if osmo["blocking"]:
        print("\n  NO-GO as a hydration drench at this concentration.")
        print("  Biological gate (LEVER 0) blocks: hypertonic and/or no Na/K/Cl.")
        print("  Chemistry levers (solubility/pH/Arrhenius) are moot until LEVER 0 passes.")
        print("  Fixes: dilute to ~245-320 mOsm/L, add Na/K/Cl premix, drop osmotic")
        print("         load (glycerin + dextrose dominate), move tyrosine/creatine to dry SKU.")
    else:
        print("\n  Biological gate PASSED — proceed on chemistry levers above.")

    print()
    print("=" * 70)
    print("  Demo complete — see compat/ package for all calculation details.")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
