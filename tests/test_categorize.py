import unittest
from unittest.mock import patch

import pandas as pd

from scripts import categorize as ct


class TestOrganizedConcatDF(unittest.TestCase):

    def setUp(self) -> None:
        self.credit_df = pd.DataFrame(
            {
                "Post Date": ["2023-01-01", "2023-02-01"],
                "Transaction Date": ["2023-01-01", "2023-02-01"],
                "Memo": ["memo1", "memo2"],
                "Type": ["credit", "credit"],
                "Description": ["payment", "purchase"],
                "Amount": [100, 200],
                "Category": ["food", ""],
                "data_source_note": ["note1", "note2"],
            }
        )

        self.bank_df = pd.DataFrame(
            {
                "Posting Date": ["2023-01-01", "2023-02-01"],
                "Details": ["details1", "details2"],
                "Balance": [1000, 900],
                "Type": ["debit", "debit"],
                "Description": ["withdrawal", "deposit"],
                "Amount": [150, -50],
                "Category": ["", "rent"],
                "data_source_note": ["note3", "note4"],
            }
        )

    def test_columns_renamed_and_dropped(self) -> None:
        result = ct.organized_concat_df(self.credit_df, self.bank_df)

        self.assertIn("Date", result.columns)
        self.assertNotIn("Post Date", result.columns)
        self.assertNotIn("Transaction Date", result.columns)

    def test_concatenation_and_filling(self) -> None:
        result = ct.organized_concat_df(self.credit_df, self.bank_df)

        self.assertTrue(result["Amount"].isnull().sum() == 0)
        self.assertTrue(result["Category"].isnull().sum() == 0)

        self.assertEqual(len(result), 4)


class TestFindAndPrintUnlabeledRows(unittest.TestCase):

    @patch("scripts.categorize.utils.print_status")
    def test_unlabeled_rows_found(self, mock_print_status) -> None:
        df = pd.DataFrame(
            {"Label": ["", "", "labeled"], "Grouping": ["group1", "group2", "group3"]}
        )
        ct.find_and_print_unlabeled_rows(df)
        mock_print_status.assert_called_once()

    @patch("scripts.categorize.utils.print_status")
    def test_no_unlabeled_rows(self, mock_print_status) -> None:
        df = pd.DataFrame(
            {
                "Label": ["labeled1", "labeled2", "labeled3"],
                "Grouping": ["group1", "group2", "group3"],
            }
        )
        ct.find_and_print_unlabeled_rows(df)
        mock_print_status.assert_not_called()
