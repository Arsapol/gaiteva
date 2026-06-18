"""Golden validation harness for compatibility demo scenarios.

These tests intentionally exercise pure calculator APIs with the same inputs
used by the user-facing demo scripts, so normal output wording can change
without hiding changes to gate decisions or formula-critical values.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path
from unittest import TestCase, main

from compat.osmolality import osmolality_report
from compat.solubility import additive_report

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = Path(__file__).resolve().parent / "golden"
OSM_TOLERANCE = 0.75
ION_TOLERANCE = 0.15

def fixture_names() -> list[str]:
    """Discover every golden fixture so new JSON files cannot be silently ignored."""
    return sorted(path.name for path in FIXTURE_DIR.glob("*.json"))


FIXTURES = fixture_names()


def load_fixture(name: str) -> dict:
    with (FIXTURE_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def scenario_from_fixture(fixture: dict) -> tuple[list[tuple[str, float]], float]:
    module = importlib.import_module(Path(fixture["source"]).stem)
    components = getattr(module, fixture["components_symbol"])
    water_ml = getattr(module, fixture["water_ml_symbol"])
    return components, water_ml


class GoldenValidationHarnessTests(TestCase):
    def test_fixture_schema_is_minimal_and_explicit(self) -> None:
        required_expected = {
            "total_mosm_per_l",
            "rounded_mosm_per_l",
            "verdict",
            "blocking",
            "complete_ors",
            "na_mmol",
            "k_mmol",
            "cl_mmol",
            "bottleneck_count",
            "bottleneck_names",
        }
        for fixture_name in FIXTURES:
            with self.subTest(fixture=fixture_name):
                fixture = load_fixture(fixture_name)
                self.assertIn("source", fixture)
                self.assertIn("components_symbol", fixture)
                self.assertIn("water_ml_symbol", fixture)
                self.assertEqual(required_expected, set(fixture["expected"]))

    def test_golden_compatibility_outputs_match_current_gate_decisions(self) -> None:
        for fixture_name in FIXTURES:
            with self.subTest(fixture=fixture_name):
                fixture = load_fixture(fixture_name)
                expected = fixture["expected"]
                components, water_ml = scenario_from_fixture(fixture)

                osmo = osmolality_report(components, water_ml=water_ml)
                sol = additive_report(components, water_ml=water_ml)
                gate = osmo["ors_gate"]
                electrolyte = osmo["electrolyte_balance"]

                self.assertAlmostEqual(
                    expected["total_mosm_per_l"],
                    gate["total_mosm_per_l"],
                    delta=OSM_TOLERANCE,
                )
                self.assertEqual(expected["rounded_mosm_per_l"], round(gate["total_mosm_per_l"]))
                self.assertEqual(expected["verdict"], gate["verdict"])
                self.assertIs(expected["blocking"], osmo["blocking"])
                self.assertIs(expected["complete_ors"], electrolyte["complete_ors"])
                self.assertAlmostEqual(expected["na_mmol"], electrolyte["na_mmol"], delta=ION_TOLERANCE)
                self.assertAlmostEqual(expected["k_mmol"], electrolyte["k_mmol"], delta=ION_TOLERANCE)
                self.assertAlmostEqual(expected["cl_mmol"], electrolyte["cl_mmol"], delta=ION_TOLERANCE)
                self.assertEqual(expected["bottleneck_count"], len(sol["bottlenecks"]))
                for name in expected["bottleneck_names"]:
                    self.assertTrue(
                        any(item.startswith(f"{name}:") for item in sol["bottlenecks"]),
                        sol["bottlenecks"],
                    )

    def test_cli_smokes_preserve_user_visible_golden_summaries(self) -> None:
        expectations = {
            "compat_calc.py": ["Osmolarity : 1542 mOsm/L  ->  BLOCK", "[BLOCK] Biological gate FAILED"],
            "reformulate.py": ["Osmolarity : 274 mOsm/L  ->  PASS", "LEVER 0 VERDICT: PASS"],
            "verify_dry_sku.py": ["Osmolarity : 291 mOsm/L  ->  PASS", "DRINK VERDICT: PASS"],
        }
        for script, snippets in expectations.items():
            with self.subTest(script=script):
                proc = subprocess.run(
                    [sys.executable, script],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=True,
                )
                for snippet in snippets:
                    self.assertIn(snippet, proc.stdout)


if __name__ == "__main__":
    main()
