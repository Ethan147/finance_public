import datetime
import subprocess
from typing import Dict, OrderedDict

import pandas as pd
from colorama import Fore, Style, init

# Initialize terminal coloring
init(autoreset=True)


def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_status(text: str) -> None:
    status_blue = Fore.CYAN
    print(f"{status_blue}{timestamp()} - {text}")


def print_error(text: str) -> None:
    error_red = Fore.RED
    print(f"{error_red}{timestamp()} - {text}")


def open(file: str) -> None:
    """Open the analysis file. Will need to close and run scripts."""
    subprocess.Popen(["libreoffice", "--calc", file])


def get_sheet_df(
    book: OrderedDict, sheet_name: str, dtype_spec: Dict = dict()
) -> pd.DataFrame:
    if not dtype_spec:
        raise ValueError("dtype spec required")

    sheet_data = book.get(sheet_name, [])

    if sheet_data:
        df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
    else:
        df = pd.DataFrame()

    for column, dtype in dtype_spec.items():
        if column in df.columns:
            fillna_value = "" if type(dtype) is str else 0
            _astype = str if type(dtype) is str else float
            df[column] = (
                df[column].astype(dtype).fillna(value=fillna_value).astype(_astype)
            )

    return df
