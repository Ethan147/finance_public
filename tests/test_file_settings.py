import unittest

from utils import file_settings as fs


class TestFunctions(unittest.TestCase):

    def test_decrypted_file_name(self) -> None:
        result = fs.decrypted_file_name()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "finance.ods")

    def test_encrypted_file_name(self) -> None:
        result = fs.encrypted_file_name()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "finance_encrypted.ods")

    def test_activity_page_bank(self) -> None:
        result = fs.activity_page_bank()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "activity_bank")

    def test_activity_page_credit(self) -> None:
        result = fs.activity_page_credit()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "activity_credit")

    def test_bank_dtype(self) -> None:
        result = fs.bank_dtype()
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["Details"], str)
        self.assertIsInstance(result["Amount"], type(float))

    def test_credit_dtype(self) -> None:
        result = fs.credit_dtype()
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["Transaction Date"], str)
        self.assertIsInstance(result["Amount"], type(float))

    def test_asset_dtype(self) -> None:
        result = fs.asset_dtype()
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["Date"], str)
        self.assertIsInstance(result["Loan Total"], str)

    def test_expenses_raw_page(self) -> None:
        result = fs.expenses_raw_page()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "expenses_raw")

    def test_expenses_page(self) -> None:
        result = fs.expenses_page()
        self.assertIsInstance(result, str)
        self.assertEqual(result, "expenses")
