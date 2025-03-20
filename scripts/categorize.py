import click
import pandas as pd
import pyexcel_ods3 as ods

from utils import expense_patterns as ep
from utils import file_settings as fs
from utils import utils


def organized_concat_df(credit_df: pd.DataFrame, bank_df: pd.DataFrame) -> pd.DataFrame:
    """Combine the credit and bank dataframes"""
    credit_df.rename(columns={"Post Date": "Date"}, inplace=True)
    credit_df = credit_df.drop(["Transaction Date", "Memo"], axis=1)
    bank_df.rename(columns={"Posting Date": "Date"}, inplace=True)
    bank_df = bank_df.drop(["Details", "Balance"], axis=1)

    order = ["Date", "Type", "Description", "Amount", "Category", "data_source_note"]
    credit_df = credit_df.reindex(columns=order)
    bank_df = bank_df.reindex(columns=order)

    df = pd.concat([credit_df, bank_df], ignore_index=True)
    df[["Amount"]] = df[["Amount"]].fillna(value=0)
    df[["Category"]] = df[["Category"]].fillna(value="")
    return df


def find_and_print_unlabeled_rows(df: pd.DataFrame) -> None:
    unlabeled_rows = df[df["Label"] == ""]["Grouping"].drop_duplicates()
    if not unlabeled_rows.empty:
        utils.print_status(f"\n\nUnlabeled rows found\n{unlabeled_rows}\n\n")


def adjust_for_inflation(row) -> None:
    import cpi

    cpi.update()
    try:
        return cpi.inflate(row["Amount"], row["Date"])
    except cpi.errors.CPIObjectDoesNotExist:
        return row["Amount"]


@click.command()
def categorize() -> None:
    book = ods.get_data(fs.decrypted_file_name())

    credit_df = utils.get_sheet_df(book, fs.activity_page_credit(), fs.credit_dtype())
    bank_df = utils.get_sheet_df(book, fs.activity_page_bank(), fs.bank_dtype())

    # raw
    df_raw = organized_concat_df(credit_df, bank_df)
    df_raw["Grouping"] = (
        df_raw["Description"].astype(str) + " " + df_raw["Category"].astype(str)
    )
    df_raw = df_raw.sort_values(by=["Grouping", "Date"])
    df_raw["Label"] = df_raw["Grouping"].apply(ep.apply_expense_label)
    df_raw = df_raw.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    find_and_print_unlabeled_rows(df_raw)

    # adjust for inflation
    df_raw["Date"] = pd.to_datetime(df_raw["Date"])
    df_raw["Historical"] = df_raw["Amount"]
    df_raw["Amount"] = df_raw.apply(adjust_for_inflation, axis=1)
    df_raw["Date"] = df_raw["Date"].dt.strftime("%Y-%m-%d")
    df_raw["Amount"] = df_raw["Amount"].round(2)

    # Type	Description	Category	Grouping	Label
    df_raw = df_raw[
        [
            "data_source_note",
            "Date",
            "Historical",
            "Amount",
            "Type",
            "Category",
            "Description",
            "Grouping",
            "Label",
        ]
    ]

    book[fs.expenses_raw_page()] = [df_raw.columns.tolist()] + df_raw.values.tolist()
    ods.save_data(fs.decrypted_file_name(), book)

    # simplified
    df_simple = df_raw["Label"].str.split(":", expand=True)
    df_simple.columns = ["Primary", "Secondary", "Terciary"]
    df_simple = pd.concat(
        [df_raw[["Date", "data_source_note", "Amount", "Description"]], df_simple],
        axis=1,
    )
    df_simple = df_simple.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_simple.fillna("", inplace=True)

    df_simple = df_simple[
        [
            "data_source_note",
            "Date",
            "Amount",
            "Description",
            "Primary",
            "Secondary",
            "Terciary",
        ]
    ]
    ep.apply_type(df_simple)
    df_simple.sort_values(
        ["data_source_note", "Primary", "Secondary", "Terciary", "Description"],
        ascending=[True, True, True, True, True],
        inplace=True,
    )

    book[fs.expenses_page()] = [df_simple.columns.tolist()] + df_simple.values.tolist()
    ods.save_data(fs.decrypted_file_name(), book)

    utils.open(fs.decrypted_file_name())
    utils.print_status("Categorization complete")
