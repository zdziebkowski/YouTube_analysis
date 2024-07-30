# utils/helpers.py

from datetime import datetime

import pandas as pd


def string_to_date(date_str: str) -> datetime.date:
    """
    Convert a string date to a datetime.date object.

    Args:
        date_str (str): Date as a string in the format 'YYYY-MM-DD'.

    Returns:
        datetime.date: Corresponding date object.
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def filter_by_date(df: pd.DataFrame, date_range: tuple) -> pd.DataFrame:
    """
    Filter the DataFrame by a date range.

    Args:
        df (pd.DataFrame): DataFrame containing a 'date' column.
        date_range (tuple): Tuple containing start and end dates.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    rng = sorted(date_range)
    dates = pd.to_datetime(df["date"], format="%Y-%m-%d").dt.date
    return df[(dates >= rng[0]) & (dates <= rng[1])]
