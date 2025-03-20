""" Centralized, configurable location for LibreOffice Calc file/sheet/etc names """

from typing import Any, Dict


def decrypted_file_name() -> str:
    return "finance.ods"


def encrypted_file_name() -> str:
    return "finance_encrypted.ods"


def activity_page_bank() -> str:
    return "activity_bank"


def activity_page_credit() -> str:
    return "activity_credit"


def bank_dtype() -> Dict[str, Any]:
    return {
        "Details": "str",
        "Posting Date": "str",
        "Description": "str",
        "Amount": float,
        "Type": "str",
        "Balance": "str",
    }


def credit_dtype() -> Dict[str, Any]:
    return {
        "Transaction Date": "str",
        "Post Date": "str",
        "Description": "str",
        "Category": "str",
        "Type": "str",
        "Amount": float,
        "Memo": "str",
    }


def asset_dtype() -> Dict[str, Any]:
    return {
        "Action": "str",
        "Date": "str",
        "Asset": "str",
        "Ethan": "str",
        "Ioulia": "str",
        "Type": "str",
        "Subtype": "str",
        "Valuation": "str",
        "Loan Total": "str",
        "Down": "str",
        "Fixed Rate": "str",
        "Monthly Recurring Income": "str",
        "Monthly Recurring Expense": "str",
        "PMI": "str",
        "PMI End": "str",
        "Note": "str",
    }


def expenses_raw_page() -> str:
    return "expenses_raw"


def expenses_page() -> str:
    return "expenses"
