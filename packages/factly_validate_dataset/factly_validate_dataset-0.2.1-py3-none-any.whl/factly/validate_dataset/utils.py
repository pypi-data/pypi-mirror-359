import calendar
import re

import pandas as pd

from . import settings
from .app_logger import log


def check_dfcols(df: pd.core.frame.DataFrame, cols: list) -> bool:
    """
    Check if the columns are present in the dataframe
    """
    if not set(cols).issubset(df.columns):
        log.error(f"Columns {cols} not found in the DataFrame")
        return True
    else:
        return False


def get_date_month_cols(df: pd.core.frame.DataFrame) -> list:
    return df.columns[
        df.columns.str.extract(settings.DATE_MONTH_COLUMNS_REGEX, expand=False).notna()
    ].tolist()


def convert_month_values(df, sorting_cols):
    cols = [
        value for value in sorting_cols if re.search(settings.MONTH_COLUMN_REGEX, value)
    ]

    if "fiscal_year" in df.columns:
        map_values = settings.FISCAL_YEAR_MONTH_DICT
    else:
        map_values = settings.YEAR_MONTH_DICT
    for col in cols:
        df[col] = df[col].map(map_values)

    return df


def convert_date_col_format(data, sorting_cols):
    cols = [col for col in sorting_cols if re.search(settings.DATE_COLUMN_REGEX, col)]

    for col in cols:
        try:
            data[col] = pd.to_datetime(data[col], format="%d-%m-%Y")
        except Exception as e:
            raise e
    return data


def year_month_continuity_check(df, year_col, month_col, skip_dates):
    data = df[[year_col, month_col]].drop_duplicates().copy()
    try:
        dates = pd.to_datetime(
            data[year_col].astype(str) + "-" + data[month_col].astype(str),
            format="%Y-%B",
        )
    except ValueError as e:
        log.error(
            f"Check cols order it should be 'year, month' and respective values: {e}"
        )
        return False
    return date_continuity_check(dates, skip_dates=skip_dates)


def date_col_continuity_check(df, date_col, freq, skip_dates):
    data = df[date_col].drop_duplicates().copy()
    try:
        dates = pd.to_datetime(data, format="%d-%m-%Y")
    except ValueError as e:
        log.error(
            f"Check '{date_col}' column values they should be in 'dd-mm-yyyy' format: {e}"
        )
        return False
    return date_continuity_check(dates, freq=freq, skip_dates=skip_dates)


def fiscal_year_month_continuity_check(df, fiscal_year_col, month_col, skip_dates):
    data = df[[fiscal_year_col, month_col]].drop_duplicates().copy()
    month_map = {month: idx for idx, month in enumerate(calendar.month_name[1:], 1)}
    data["month_num"] = data[month_col].map(month_map)
    data["year"] = data.apply(
        lambda x: int(x[fiscal_year_col].split("-")[0])
        if int(x["month_num"]) >= 4
        else int(x[fiscal_year_col].split("-")[0]) + 1,
        axis=1,
    )
    data["date"] = pd.to_datetime(
        dict(year=data["year"], month=data["month_num"], day=1)
    )
    try:
        dates = pd.to_datetime(data["date"], format="%d-%m-%Y")
    except ValueError as e:
        log.error(
            f"Check cols order it should be 'fiscal_year, month' and respective values: {e}"
        )
        return False
    return date_continuity_check(dates, skip_dates=skip_dates)


def date_continuity_check(dates, freq="MS", skip_dates=None):
    min_date = dates.min()
    max_date = dates.max()
    intermediate_dates = pd.date_range(min_date, max_date, freq=freq)
    missing_dates = set(intermediate_dates) - set(dates)
    if skip_dates:
        missing_dates = missing_dates - set(skip_dates)
    if missing_dates:
        log.error(f"Missing dates in data: {sorted(missing_dates)}")
        return False
    return True
