import unittest

from compat.redox import flag_from_components, redox_mechanism_ledger


class RedoxUpgradeTests(unittest.TestCase):
    def test_reformulate_ascorbate_case_stays_moderate(self):
        components = [
            ("dextrose", 14.0),
            ("sodium_chloride", 2.6),
            ("potassium_chloride", 1.5),
            ("trisodium_citrate", 2.9),
            ("ascorbic_acid", 0.5),
            ("beta_alanine", 1.0),
            ("d_ribose", 2.0),
        ]
        result = flag_from_components(components, oxygen_exposure="headspace", light_exposure="clear")
        self.assertTrue(result["applicable"])
        self.assertEqual(result["risk_level"], "MODERATE")
        self.assertIn("risk_score", result)
        self.assertIn("thresholds", result)
        self.assertIn("HPLC ascorbic acid + dehydroascorbic acid (DHAA)", result["validation_assays"])

    def test_wet_nac_metal_o2_flags_thiol_oxidation(self):
        result = redox_mechanism_ledger(
            [("n_acetylcysteine", 1.0), ("copper_tbcc", 0.01)],
            oxygen_exposure="headspace",
            light_exposure="clear",
            storage_context="wet_stored",
        )
        thiol = [m for m in result["mechanisms"] if m["mechanism"] == "thiol_oxidation"]
        self.assertEqual(len(thiol), 1)
        self.assertIn(thiol[0]["risk_level"], {"HIGH", "SEVERE"})
        self.assertEqual(result["shelf_claim_gate"], "BLOCK_SHELF_CLAIM_PENDING_ASSAYS")
        self.assertIn("HPLC/LC-MS NAC or cysteine plus disulfide dimer", result["validation_assays"])

    def test_dry_nac_is_not_wet_shelf_block(self):
        result = redox_mechanism_ledger(
            [("n_acetylcysteine", 1.0), ("copper_tbcc", 0.01)],
            oxygen_exposure="headspace",
            storage_context="dry",
        )
        self.assertEqual(result["overall_risk"], "LOW")
        self.assertNotEqual(result["shelf_claim_gate"], "BLOCK_SHELF_CLAIM_PENDING_ASSAYS")
        self.assertIn("dry-separated", result["mechanisms"][0]["drivers"][0])

    def test_supplier_metal_ppm_is_reported_not_silent(self):
        result = redox_mechanism_ledger(
            [("ascorbic_acid", 0.5)],
            oxygen_exposure="sealed",
            light_exposure="opaque",
            storage_context="wet_stored",
            metal_ppm={"cu": 2.0, "fe": 5.0},
        )
        self.assertTrue(result["detected"]["metals"]["copper"])
        self.assertIn("transition_metal_catalysis", {m["mechanism"] for m in result["mechanisms"]})
        self.assertIn("supplier CoA Cu/Fe/Mn ppm limits", " | ".join(result["validation_assays"]))


if __name__ == "__main__":
    unittest.main()
