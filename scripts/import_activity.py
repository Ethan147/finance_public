import os
from typing import Any, Dict, List

import click
import pandas as pd
import pyexcel_ods3 as ods

from utils import file_settings as fs
from utils import utils


def _get_csv_df_bank(csv_file: str) -> pd.DataFrame:
    columns_to_import = [
        "Details",
        "Posting Date",
        "Description",
        "Amount",
        "Type",
        "Balance",
    ]
    dtype_mapping = fs.bank_dtype()
    df = pd.read_csv(
        csv_file,
        usecols=columns_to_import,
        dtype=dtype_mapping,
        header=0,
        index_col=False,
    )
    df[["Amount"]] = df[["Amount"]].fillna(value=0)
    na_str_cols = ["Details", "Posting Date", "Description", "Type", "Balance"]
    df[na_str_cols] = df[na_str_cols].fillna(value="")
    return df


def _get_csv_df_credit(csv_file: str) -> pd.DataFrame:
    columns_to_import = [
        "Transaction Date",
        "Post Date",
        "Description",
        "Category",
        "Type",
        "Amount",
        "Memo",
    ]
    dtype_mapping = fs.credit_dtype()
    df = pd.read_csv(
        csv_file,
        usecols=columns_to_import,
        dtype=dtype_mapping,
        header=0,
        index_col=False,
    )
    df[["Amount"]] = df[["Amount"]].fillna(value=0)
    na_str_cols = [
        "Transaction Date",
        "Post Date",
        "Description",
        "Category",
        "Type",
        "Memo",
    ]
    df[na_str_cols] = df[na_str_cols].fillna(value="")
    return df


@click.command()
@click.argument("csv_file", type=str)
@click.argument("data_type", type=str)
@click.argument("data_source_note", type=str)
def import_activity(csv_file: str, data_type: str, data_source_note: str) -> None:
    """
    Import CSV financial activity data into a sheet for later analysis, ignoring duplicate entries.

    :param csv_file: Path to the CSV file containing the transaction history.
    :param data_type: "credit" or "bank" (column names differ)
    :param data_source_note: A user-specified data source for the supplied data.
    """
    book = ods.get_data(fs.decrypted_file_name())

    sheet_name, dtypes = {
        "bank": (fs.activity_page_bank(), fs.bank_dtype()),
        "credit": (fs.activity_page_credit(), fs.credit_dtype()),
    }[data_type]

    sheet_df = utils.get_sheet_df(book, sheet_name, dtypes)

    if data_type == "bank":
        df = _get_csv_df_bank(csv_file)
    else:
        df = _get_csv_df_credit(csv_file)

    df["data_source_note"] = data_source_note
    combined_df = pd.concat([df, sheet_df]).drop_duplicates().reset_index(drop=True)

    book[sheet_name] = [combined_df.columns.tolist()] + combined_df.values.tolist()
    ods.save_data(fs.decrypted_file_name(), book)

    utils.open(fs.decrypted_file_name())
    utils.print_status(
        f"Data from {csv_file} has been imported into {fs.decrypted_file_name()}, ignoring duplicates."
    )
