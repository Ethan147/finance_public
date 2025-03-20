"""
Area containing the base relationships for categorizing a variety of personal expenses.

Each dictionary is a collection of key value pairs.
    - The key is a regex for identifying one or more charges that we want to categorize under a single logical grouping
    - The value is what would like to categorize that regex-grouping as in a "Primary: Secondary: Tertiary" (where only Primary is required)

Some example of categorization:
{
    "(?i)Acme.*CO": "Shopping: Hardware: Hijinks: Acme Corporation",
    "Wallmart": "Shopping: Retail: Wallmart",
    "Burger":  "Restaurant: A burger joint"
}
"""

import re

import numpy as np
import pandas as pd

# python >= 3.7 preserves dictionary order, order in terms of priority
patterns_restaurant = {
    r"(?i)Regex_For_Some_Restaurant": "Restaurant: Just: Ok: Restaurant X",
    r"(?i)Super.*Duper.*Cafe.*Food": "Restaurant: Super: Good: Super Duper Cafe",
}

patterns_stores = {
    r"(?i)Amazon.*Mktp": "Shopping: Retail: Amazon",
    r"(?i)The.Home.Depot": "Shopping: Home: The Home Depot",
}

patterns_entertainment = {
    r"(?i)Alamo.*(Rest|Retail)": "Entertainment: Activity: Alamo Drafthouse, Misc",
    r"(?i)Prime.*Video": "Entertainment: Video: Prime Video",
}

patterns_travel = {
    r"(?i)Airbnb": "Travel: Lodging: Airbnb",
    r"(?i)Alaska.*Air": "Travel: Transport: Alaska Air",
}

patterns_fuel = {
    r"(?i)7.*Eleven.*Gas": "Fuel: Gas: 7-11",
    r"(?i)Buc-Ee.*Gas": "Fuel: Gas: Buc-Ee",
    r"(?i)Tesla.*Supercharger": "Fuel: Electric: Tesla",
}

patterns_automotive = {
    r"(?i)Autowash": "Automotive: Wash: Car Wash",
    r"(?i)Aaa.*Acg.*Sw": "Automotive: Maintenance: AAA",
}

patterns_transfers = {
    r"(?i)Atm.*Cach.*Deposit": "Transfers: Atm: Deposit",
    r"(?i)Check.*\D": "Transfers: Check: Payment",
}

patterns_subscriptions = {
    # Video
    r"(?i)Alamo Drafthouse (Entertainment|Shopping)": "Subscription: Video: Alamo Drafthouse",
    r"(?i)Amazon Prime": "Subscription: Video: Amazon Prime Video",
}

patterns_services = {
    r"(?i)Birds.Barber": "Service: Haircut: Birds Barbershop",
    r"(?i)Rover": "Service: Pet: Rover",
}

patterns_health = {
    r"(?i)Eye.*Clinic": "Health: Medical: Eye Clinic",
    r"(?i)Vca.Animal.Hosp": "Health: Vet: Vca Animal Hospital",
}

patterns_utilities = {
    r"(?i)Check.*Passportservices": "Utilities: General: Passport Renewal",
    r"(?i)Google.*Fiber": "Utilities: Internet: Google Fiber",
}

patterns_contractor = {
    r"(?i)Wacky.*Win": "Contractor: Wacky Windows",
    r"(?i)Make.*It.*Work.*Hvac": "Contractor: Make It Work HVAC",
}

patterns_income = {
    r"(?i)Acme CO.*Payroll": "Income: Salary: Acme Co",
}

patterns_kiosk = {
    r"(?i)Temp.*Kiosk": "Kiosk: Snacks, Misc",
}

patterns_insurance = {
    r"(?i)Claim.*\d.*Health": "Insurance: Claim",
    r"(?i)Dogs.Are.Good.Ins": "Insurance: Pet",
}

patterns_mortgage = {
    r"(?i)Mortgage.*Holdings.*Llc": "Mortgage: Misc",
}

patterns_tax = {
    r"(?i)Irs.*Usatax": "Tax: IRS",
}

patterns_charity = {
    r"(?i)Unduemedicaldebt": "Charity: Undue Medical Debt",
    r"(?i)Ripmedicaldebt": "Charity: Undue Medical Debt",
}

patterns_expense = {
    **patterns_income,
    **patterns_subscriptions,
    **patterns_utilities,
    **patterns_health,
    **patterns_fuel,
    **patterns_entertainment,
    **patterns_restaurant,
    **patterns_kiosk,
    **patterns_automotive,
    **patterns_stores,
    **patterns_services,
    **patterns_mortgage,
    **patterns_insurance,
    **patterns_charity,
    **patterns_transfers,
    **patterns_travel,
    **patterns_tax,
    **patterns_contractor,
}


def apply_expense_label(description: str) -> str:
    for pattern, name in patterns_expense.items():
        if pd.notna(description) and re.search(pattern, description):
            return name
    return ""


def apply_type(df: pd.DataFrame) -> None:
    df["Type"] = ""

    # lifestyle
    df.Type = np.where(df.Primary == "Automotive", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Fuel", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Charity", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Tax", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Health", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Mortgage", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Insurance", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Utilities", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Contractor", "Lifestyle", df.Type)
    df.Type = np.where(df.Primary == "Service", "Lifestyle", df.Type)
    df.Type = np.where(
        df.Secondary == "Utility", "Lifestyle", df.Type
    )  # Subscription: Utility
    df.Type = np.where(
        df.Secondary == "Health", "Lifestyle", df.Type
    )  # Subscription: Health
    df.Type = np.where(
        df.Secondary == "Groceries", "Lifestyle", df.Type
    )  # Shopping: Groceries
    df.Type = np.where(df.Secondary == "Home", "Lifestyle", df.Type)  # Shopping: Home

    # fun
    df.Type = np.where(df.Primary == "Restaurant", "Fun", df.Type)
    df.Type = np.where(df.Primary == "Kiosk", "Fun", df.Type)
    df.Type = np.where(df.Primary == "Entertainment", "Fun", df.Type)
    df.Type = np.where(df.Secondary == "Video", "Fun", df.Type)

    # travel
    df.Type = np.where(df.Primary == "Travel", "Travel", df.Type)

    # transfers
    df.Type = np.where(df.Primary == "Transfers", "Transfers", df.Type)

    # income
    df.Type = np.where(df.Primary == "Income", "Income", df.Type)

    # shopping
    df.Type = np.where(df.Primary == "Shopping", "Retail", df.Type)

    uncategorized = df[df.Type == ""][["Type", "Primary", "Secondary"]].copy()
    if not uncategorized.empty:
        raise ValueError(uncategorized)
