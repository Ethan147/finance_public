import unittest
from typing import Any

import pandas as pd

from scripts.graph import (_sample, apply_stand_dev, df_base, df_expenses,
                           df_income, df_income_simple, df_lifestyle)


def sample_df() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "Date": ["2023-01-01", "2023-02-01", "2023-03-01"],
            "Amount": [1000, -500, 2000],
            "Primary": ["Income", "Expenses", "Income"],
            "Secondary": ["Salary", "Rent", "Bonus"],
            "Terciary": ["Job", "Home", "Freelance"],
            "Type": ["Income", "Lifestyle", "Income"],
        }
    )
    df["Date"] = pd.to_datetime(df["Date"])
    return df


class TestSampleFunction(unittest.TestCase):

    def test_sample_valid(self) -> None:
        self.assertEqual(_sample("month"), "ME")
        self.assertEqual(_sample("year"), "YE")

    def test_sample_invalid(self) -> None:
        with self.assertRaises(KeyError):
            _sample("day")  # Invalid key


class TestDfBaseFunction(unittest.TestCase):

    def setUp(self) -> None:
        self.df: pd.DataFrame = sample_df()

    def test_df_base(self) -> None:
        result: pd.DataFrame = df_base(self.df)
        self.assertEqual(
            list(result.columns),
            ["Date", "Amount", "Primary", "Secondary", "Terciary", "Type"],
        )
        self.assertTrue(result["Date"].is_monotonic_increasing)


class TestDfIncomeFunction(unittest.TestCase):

    def setUp(self) -> None:
        self.df: pd.DataFrame = sample_df()

    def test_df_income_no_sample(self) -> None:
        result: pd.DataFrame = df_income(self.df)
        self.assertEqual(list(result.columns), ["Amount", "Source"])
        self.assertTrue("Income" in self.df.Primary.values)

    @unittest.mock.patch("scripts.graph._sample", return_value="M")
    def test_df_income_with_sample(self, mock_sample: Any) -> None:
        result: pd.DataFrame = df_income(self.df, sample="month")
        mock_sample.assert_called_once_with("month")

        self.assertIsInstance(result.index.get_level_values(1), pd.DatetimeIndex)


class TestDfIncomeSimpleFunction(unittest.TestCase):

    def setUp(self) -> None:
        self.df: pd.DataFrame = sample_df()

    def test_df_income_simple_no_sample(self) -> None:
        result: pd.DataFrame = df_income_simple(self.df)

        self.assertIsInstance(result.index, pd.DatetimeIndex)

    @unittest.mock.patch("scripts.graph._sample", return_value="M")
    def test_df_income_simple_with_sample(self, mock_sample: Any) -> None:
        result: pd.DataFrame = df_income_simple(self.df, sample="month")
        mock_sample.assert_called_once_with("month")

        self.assertIsInstance(result.index, pd.DatetimeIndex)


class TestDfExpensesFunction(unittest.TestCase):

    def setUp(self) -> None:
        self.df: pd.DataFrame = sample_df()

    def test_df_expenses_no_sample(self) -> None:
        result: pd.DataFrame = df_expenses(self.df)
        self.assertTrue((result["Amount"] == [500]).all())  # Absolute value test

    @unittest.mock.patch("scripts.graph._sample", return_value="M")
    def test_df_expenses_with_sample(self, mock_sample: Any) -> None:
        result: pd.DataFrame = df_expenses(self.df, sample="month")
        mock_sample.assert_called_once_with("month")

        # Check if the second level of the MultiIndex is a DatetimeIndex
        self.assertIsInstance(result.index.get_level_values(1), pd.DatetimeIndex)


class TestDfLifestyleFunction(unittest.TestCase):

    def setUp(self) -> None:
        self.df: pd.DataFrame = sample_df()

    def test_df_lifestyle(self) -> None:
        result: pd.DataFrame = df_lifestyle(self.df)
        self.assertTrue(
            (result["Amount"] == [500]).all()
        )  # Absolute value for lifestyle


class TestApplyStandDevFunction(unittest.TestCase):

    def test_apply_stand_dev(self) -> None:
        df: pd.DataFrame = pd.DataFrame(
            {
                "Amount": [1000, 2000, -500, -600, 3000, -200],
                "Date": pd.date_range(start="2023-01-01", periods=6),
            }
        )
        result: pd.DataFrame = apply_stand_dev(df, num_stand_devs=1)

        # Test that the result only contains rows within the 1 standard deviation
        self.assertTrue(result.shape[0] > 0)
        self.assertTrue(all(result.Amount <= 3000))
        self.assertTrue(all(result.Amount >= -600))
