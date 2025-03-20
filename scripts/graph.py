import os
import warnings
from typing import Dict, List, Optional

import click
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyexcel_ods3 as ods
import seaborn as sns

from utils import expense_patterns as ep
from utils import file_settings as fs
from utils import utils

warnings.filterwarnings(
    "ignore", message="The palette list has more values .* than needed .*"
)


FIGSIZE = (6, 3)
FIGSIZE_LARGE = (6, 4)
FONTSIZE = 9


def _palette() -> List[str]:
    return [
        "#DC143C",  # Crimson Red
        "#0047AB",  # Cobalt Blue
        "#50C878",  # Emerald Green
        "#FFBF00",  # Amber
        "#800080",  # Deep Purple
        "#008080",  # Teal
        "#FF7F50",  # Coral
        "#0F52BA",  # Sapphire
        "#808000",  # Olive Green
        "#FF00FF",  # Magenta
        "#40E0D0",  # Turquoise
        "#FD5E53",  # Sunset Orange
    ]


def _sample(sample: str) -> str:
    return {"month": "ME", "year": "YE"}[sample]


def df_base(df_arg: pd.DataFrame) -> pd.DataFrame:
    """Simplify df"""
    df = df_arg[["Date", "Amount", "Primary", "Secondary", "Terciary", "Type"]].copy()
    df.Date = pd.to_datetime(df.Date)
    df.sort_values("Date", inplace=True)

    return df


def df_income(df_arg: pd.DataFrame, sample: Optional[str] = None) -> pd.DataFrame:
    """Income only df"""
    df = df_arg[df_arg.Primary == "Income"][["Date", "Amount", "Terciary"]].copy()
    df = df.rename(columns={"Terciary": "Source"})
    df = df.set_index("Date")

    # pandas is confused about the variable pass in, this is following recommendations
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        if sample:
            df = df.groupby("Source").resample(_sample(sample)).agg({"Amount": "sum"})

    return df


def df_income_simple(
    df_arg: pd.DataFrame, sample: Optional[str] = None
) -> pd.DataFrame:
    """Income only df"""
    df = df_arg[df_arg.Primary == "Income"][["Date", "Amount"]].copy()
    df = df.set_index("Date")

    # pandas is confused about the variable pass in, this is following recommendations
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        if sample:
            df = df.resample(_sample(sample)).sum()

    return df


def df_expenses(df_arg: pd.DataFrame, sample: Optional[str] = None) -> pd.DataFrame:
    """For analysis of expenses"""
    df = df_arg[~df_arg.Type.isin(["Income", "Transfers"])][
        ["Date", "Amount", "Type"]
    ].copy()
    df = df.set_index("Date")
    df.Amount = df.Amount.abs()

    # pandas is confused about the variable pass in, this is following recommendations
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        if sample:
            df = df.groupby("Type").resample(_sample(sample)).agg({"Amount": "sum"})

    return df


def df_lifestyle(df_arg: pd.DataFrame, sample: Optional[str] = None) -> pd.DataFrame:
    """For analysis of lifestyle"""
    df = df_arg[df_arg.Type == "Lifestyle"].copy()
    df.Amount = df.Amount.abs()
    df = df.set_index("Date")

    return df


def apply_stand_dev(
    df: pd.DataFrame,
    num_stand_devs: int,
) -> pd.DataFrame:
    """Apply standard deviation filtering, once for income & once for expenses"""

    mean_income = df[df.Amount > 0].Amount.mean()
    std_income = df[df.Amount > 0].Amount.std()
    cut_off_income = std_income * num_stand_devs
    lower_income, upper_income = (
        mean_income - cut_off_income,
        mean_income + cut_off_income,
    )

    mean_expense = df[df.Amount < 0].Amount.mean()
    std_expense = df[df.Amount < 0].Amount.std()
    cut_off_expense = std_expense * num_stand_devs
    lower_expense, upper_expense = (
        mean_expense - cut_off_expense,
        mean_expense + cut_off_expense,
    )

    return df[
        ((df.Amount > 0) & (df.Amount >= lower_income) & (df.Amount <= upper_income))
        | (
            (df.Amount < 0)
            & (df.Amount >= lower_expense)
            & (df.Amount <= upper_expense)
        )
    ].copy()


def graph_income_expenses_cumsum(
    df_arg: pd.DataFrame, title_disclaimer: str = ""
) -> None:
    """Basic graph of overall ingress & egress"""
    df = df_arg.copy()
    df["Sum"] = df.Amount.cumsum()
    df["Category"] = np.where(df.Amount > 0, "Income", "Expense")

    fig, ax = plt.subplots(figsize=FIGSIZE, tight_layout=True)

    sns.lineplot(
        data=df,
        x="Date",
        y="Amount",
        hue="Category",
        palette={"Income": "black", "Expense": "red"},
        ax=ax,
    )
    sns.lineplot(data=df, x="Date", y="Sum", color="blue", label="Sum", ax=ax)

    title = f"Income, Expenses, and Sum\nIgnoring Vacation Savings.{title_disclaimer}"
    ax.set_title(title, fontsize=FONTSIZE)
    ax.set_xlabel("Date", fontsize=FONTSIZE)
    ax.set_ylabel("Amount ($)", fontsize=FONTSIZE)
    ax.legend(title="Category", fontsize=FONTSIZE)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True)


def graph_income(df_arg: pd.DataFrame, sample: str) -> None:
    """Graph basic ingress by type"""
    df = df_income(df_arg, sample)
    income_pivot = (
        df.pivot_table(values="Amount", index="Date", columns="Source", fill_value=0)
        .resample(_sample(sample))
        .sum()
    )

    fig, ax = plt.subplots(figsize=FIGSIZE, tight_layout=True)
    income_pivot.plot.area(
        stacked=True,
        color=_palette(),
        ax=ax,
    )
    ax.set_title(f"Income, sample {sample}", fontsize=FONTSIZE)
    ax.set_xlabel("Date", fontsize=FONTSIZE)
    ax.set_ylabel("Income", fontsize=FONTSIZE)
    ax.legend(title="Income Source", fontsize=FONTSIZE)
    ax.grid(True)


def graph_expenses(df_arg: pd.DataFrame, sample: str, disclaimer: str = "") -> None:
    """Graph egress by type"""

    df_exp = df_expenses(df_arg)
    expenses_pivot = (
        df_exp.pivot_table(values="Amount", index="Date", columns="Type", fill_value=0)
        .resample(_sample(sample))
        .sum()
    )

    fig, ax = plt.subplots(figsize=FIGSIZE, tight_layout=True)
    expenses_pivot.plot.area(
        stacked=True,
        color=_palette(),
        ax=ax,
    )
    ax.set_title(f"Expenses, sample {sample}{disclaimer}", fontsize=FONTSIZE)
    ax.set_xlabel("Date", fontsize=FONTSIZE)
    ax.set_ylabel("Expense", fontsize=FONTSIZE)
    ax.legend(title="Expense Type", fontsize=FONTSIZE)
    ax.grid(True)


def graph_expense_type_area(
    df_arg: pd.DataFrame, sample: str, disclaimer: str = ""
) -> None:
    """Display egress in total percentages"""
    df = df_expenses(df_arg)
    expenses_pivot = df.pivot_table(
        values="Amount", index="Date", columns="Type", fill_value=0
    )
    smoothed_expenses = expenses_pivot.resample(_sample(sample)).sum()

    # Normalize the data by row to sum up to 1 (100%)
    percentage_expenses = smoothed_expenses.divide(
        smoothed_expenses.sum(axis=1), axis=0
    )

    fig, ax = plt.subplots(figsize=FIGSIZE, tight_layout=True)
    percentage_expenses.plot.area(
        stacked=True,
        color=_palette(),
        ax=ax,
    )
    ax.set_title(f"Expense Percentages, sample {sample}{disclaimer}", fontsize=FONTSIZE)
    ax.set_xlabel("Date", fontsize=FONTSIZE)
    ax.set_ylabel("Percentage of Expenses", fontsize=FONTSIZE)
    ax.legend(title="Expense Type", fontsize=FONTSIZE)
    ax.grid(True)


def graph_expense_type_area_perc_of_income(
    df_arg: pd.DataFrame, sample: str, disclaimer: str = ""
) -> None:
    """Display expense in percentage of income"""
    # expenses
    df_exp = df_expenses(df_arg)

    expenses_pivot = (
        df_exp.pivot_table(values="Amount", index="Date", columns="Type", fill_value=0)
        .resample(_sample(sample))
        .sum()
    )

    # income
    df_inc = df_income_simple(df_arg, sample)

    # as percentage
    percentage_expenses = expenses_pivot.div(df_inc.Amount, axis=0) * 100

    fig, ax = plt.subplots(figsize=FIGSIZE, tight_layout=True)
    percentage_expenses.plot.area(
        stacked=True,
        color=_palette(),
        ax=ax,
    )
    ax.set_title(
        f"Expense as perc of income, sample {sample}{disclaimer}", fontsize=FONTSIZE
    )
    ax.set_xlabel("Date", fontsize=FONTSIZE)
    ax.set_ylabel("Percentage of Expenses", fontsize=FONTSIZE)
    ax.legend(title="Expense Type", fontsize=FONTSIZE)
    ax.grid(True)


def graph_lifestyle_type_area(
    df_arg: pd.DataFrame, sample: str, disclaimer: str = ""
) -> None:
    """Display lifestyle in total percentages"""
    df = df_lifestyle(df_arg)

    expenses_pivot = df.pivot_table(
        values="Amount", index="Date", columns="Primary", fill_value=0
    )
    smoothed_expenses = expenses_pivot.resample(_sample(sample)).sum()

    # Normalize the data by row to sum up to 1 (100%)
    percentage_expenses = smoothed_expenses.divide(
        smoothed_expenses.sum(axis=1), axis=0
    )

    fig, ax = plt.subplots(figsize=FIGSIZE_LARGE, tight_layout=True)
    percentage_expenses.plot.area(
        stacked=True,
        color=_palette(),
        ax=ax,
    )
    ax.set_title(
        f"Lifestyle Percentages, sample {sample}{disclaimer}", fontsize=FONTSIZE
    )
    ax.set_xlabel("Date", fontsize=FONTSIZE)
    ax.set_ylabel("Percentage of Expenses", fontsize=FONTSIZE)
    ax.legend(title="Expense Type", fontsize=FONTSIZE)
    ax.grid(True)


@click.command()
@click.argument("variant", type=str, default="all")
def graph(variant: str) -> None:
    """
    Graph may be of the following variants

    - all\n
    - household\n
    - property\n
    """
    utils.print_status("Begin graph")
    book = ods.get_data(fs.decrypted_file_name())

    if variant in ("all", "household"):
        df_expenses = utils.get_sheet_df(book, fs.expenses_page(), fs.credit_dtype())
        df = df_base(df_expenses)

        # Vacation transfers are not relevant
        df = df[~((df.Primary == "Transfers") & (df.Secondary == "Vacation"))]

        df_std_5 = apply_stand_dev(df, 5)

        graph_income_expenses_cumsum(df)
        graph_income_expenses_cumsum(df_std_5, "\nControl for 5 standar deviations")

        graph_income(df, "month")
        graph_income(df, "year")

        graph_expenses(df, "month")
        graph_expenses(df, "year")
        graph_expenses(df_std_5, "year", "\nControl for 5 standard deviation")

        graph_expense_type_area(df, "month")
        graph_expense_type_area(df, "year")
        graph_expense_type_area(df_std_5, "year", "\nControl for 5 standard deviation")

        graph_expense_type_area_perc_of_income(df, "month")
        graph_expense_type_area_perc_of_income(df, "year")

        graph_lifestyle_type_area(df, "month")
        graph_lifestyle_type_area(df, "year")
        graph_lifestyle_type_area(
            df_std_5, "year", "\nControl for 5 standard deviation"
        )

    elif variant in ("property"):
        raise Exception("Not implemented")

    plt.show()

    utils.print_status("Graphing complete complete")
