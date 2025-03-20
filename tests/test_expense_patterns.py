import unittest

import numpy as np
import pandas as pd

from utils import expense_patterns as ep


class TestApplyExpenseLabel(unittest.TestCase):

    def test_known_patterns(self) -> None:
        self.assertEqual(
            ep.apply_expense_label("Super Duper Duper Cafe Food"),
            "Restaurant: Super: Good: Super Duper Cafe",
        )
        self.assertEqual(
            ep.apply_expense_label("Temp Big 'ol Kiosk"), "Kiosk: Snacks, Misc"
        )
        self.assertEqual(ep.apply_expense_label("Airbnb"), "Travel: Lodging: Airbnb")

    def test_no_pattern_match(self) -> None:
        self.assertEqual(ep.apply_expense_label("Unknown Vendor"), "")

    def test_empty_description(self) -> None:
        self.assertEqual(ep.apply_expense_label(""), "")


class TestApplyType(unittest.TestCase):

    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "Primary": [
                    "Automotive",
                    "Restaurant",
                    "Transfers",
                    "Shopping",
                    "Mortgage",
                ],
                "Secondary": [
                    "Car Wash",
                    "Coffee",
                    "Venmo Payment",
                    "Groceries",
                    "Home Loan",
                ],
            }
        )

    def test_apply_type(self) -> None:
        ep.apply_type(self.df)

        # Expected types based on 'Primary' and 'Secondary'
        expected_types = ["Lifestyle", "Fun", "Transfers", "Retail", "Lifestyle"]

        # Verify if the 'Type' column is correctly applied
        self.assertListEqual(self.df["Type"].tolist(), expected_types)

    def test_no_empty_types(self) -> None:
        # Ensure no empty types in the result
        ep.apply_type(self.df)
        self.assertFalse(self.df["Type"].isnull().any())
