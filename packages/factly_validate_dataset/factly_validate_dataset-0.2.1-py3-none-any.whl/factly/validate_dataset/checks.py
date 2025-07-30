import calendar
import re

import pandera as pa
from pandera.api.pandas.model import DataFrameModel

from . import settings
from .app_logger import log
from .assets.constants import STATES
from .assets.names import factly_std_names
from .models import DateContinuity
from .utils import (
    check_dfcols,
    convert_date_col_format,
    convert_month_values,
    date_col_continuity_check,
    fiscal_year_month_continuity_check,
    get_date_month_cols,
    year_month_continuity_check,
)


class BaseSchemaModel(DataFrameModel):
    class Config:
        strict = True
        ordered = True
        coerce = True


class FactlyDatasetSchema(BaseSchemaModel):
    _duplicate_cols = None
    _sorting_cols = None

    _check_duplicates = True
    _save_duplicates = False
    _check_sort = True
    _check_column_names = True
    _check_white_space = True
    _check_state_names = True
    _check_month_names = True
    _check_country_names = True
    _check_null_values_in_date_cols = True
    _check_date_continuity = False
    _date_continuity_cols = {}

    # Cache for validation results
    _month_values_check_result = False
    _null_values_in_date_cols_check_result = False

    @pa.dataframe_check
    def check_column_names(cls, df):
        """
        Check for special characters and capital letters in all column names at once
        """
        if not cls._check_column_names:
            return True
        return df.columns.str.contains(r"^[a-z]+(?:_[a-z]+)*$", regex=True).all()

    @pa.dataframe_check
    def white_space_check(cls, df):
        """
        Check for multiple_white_spaces in middle and leading or tailing spaces in the dataframe
        """
        if not cls._check_white_space:
            return True
        return (
            ~df.map(
                lambda x: isinstance(x, str) and bool(re.search(r"\s{2,}|^\s|\s$", x))
            )
            .any()
            .any()
        )

    @pa.dataframe_check
    def state_names_check(cls, df):
        """
        Check for state names in the dataframe
        """
        if not cls._check_state_names:
            return True

        state_cols = df.columns[
            df.columns.str.contains(settings.STATE_COLUMN_REGEX, regex=True)
        ].values.tolist()
        for state_col in state_cols:
            if not df[state_col].isin(STATES).all():
                return False
        return True

    @pa.dataframe_check
    def country_names_check(cls, df):
        """
        Check for country names in the dataframe
        """
        if not cls._check_country_names:
            return True

        country_cols = df.columns[
            df.columns.str.contains(settings.COUNTRY_COLUMN_REGEX, regex=True)
        ].values.tolist()
        if country_cols:
            country_names = factly_std_names("country")
            for country_col in country_cols:
                if not df[country_col].isin(country_names).all():
                    return False
        return True

    @pa.dataframe_check
    def check_null_values_in_temporal(cls, df):
        """
        Check for null values in year or month columns
        """
        if not cls._check_null_values_in_date_cols:
            return True
        cols = get_date_month_cols(df)
        if cols and df.loc[:, cols].isnull().any().any():
            return False
        cls._null_values_in_date_cols_check_result = True
        return True

    @pa.dataframe_check
    def month_values_check(cls, df):
        """
        Check for month values in the dataframe
        """
        if not cls._check_month_names:
            return True
        month_cols = df.columns[
            df.columns.str.contains(settings.MONTH_COLUMN_REGEX, regex=True)
        ].values.tolist()
        for month_col in month_cols:
            if (
                not df[month_col]
                .isin([month for month in calendar.month_name[1:]])
                .all()
            ):
                return False
        cls._month_values_check_result = True
        return True

    @pa.dataframe_check
    def check_date_continuity(cls, df):
        """
        Check for continuity in date columns
        """
        if not cls._check_date_continuity:
            return True

        if not cls._check_month_names:
            log.warning("Cannot check date continuity without month values check")
            return False
        if not cls._null_values_in_date_cols_check_result:
            log.warning(
                "Skipping date continuity check because null values in date cols check failed"
            )
            return False

        # Skip date continuity check if month values check fails
        if not cls._month_values_check_result:
            log.warning(
                "Skipping date continuity check because month values check failed"
            )
            return False
        if not cls._date_continuity_cols:
            if "year" in df.columns and "month" in df.columns:
                cls._date_continuity_cols = {
                    "cols": ["year", "month"],
                    "format_name": "year_month",
                }
            elif "fiscal_year" in df.columns and "month" in df.columns:
                cls._date_continuity_cols = {
                    "cols": ["fiscal_year", "month"],
                    "format_name": "fiscal_year_month",
                }
            elif "date" in df.columns:
                cls._date_continuity_cols = {
                    "cols": ["date"],
                    "format_name": "date",
                    "frequency": "D",
                }
            else:
                log.error("Date columns not found")
                return False

        cls._date_continuity_cols = DateContinuity(**cls._date_continuity_cols)
        log.info(f"Date Continuity Config: {cls._date_continuity_cols}")

        if cls._date_continuity_cols.format_name == "year_month":
            return year_month_continuity_check(
                df,
                cls._date_continuity_cols.cols[0],
                cls._date_continuity_cols.cols[1],
                cls._date_continuity_cols.skip_dates,
            )
        elif cls._date_continuity_cols.format_name == "fiscal_year_month":
            return fiscal_year_month_continuity_check(
                df,
                cls._date_continuity_cols.cols[0],
                cls._date_continuity_cols.cols[1],
                cls._date_continuity_cols.skip_dates,
            )
        elif cls._date_continuity_cols.format_name == "date":
            return date_col_continuity_check(
                df,
                cls._date_continuity_cols.cols[0],
                cls._date_continuity_cols.frequency,
                cls._date_continuity_cols.skip_dates,
            )
        else:
            log.error("Invalid _date_continuity_cols")
            return False

    @pa.dataframe_check
    def check_duplicates(cls, df):
        """
        Check for duplicates in the dataframe
        """
        if not cls._check_duplicates:
            return True
        if cls._duplicate_cols is not None and check_dfcols(df, cls._duplicate_cols):
            return False

        cls._duplicate_cols = (
            df.columns.tolist() if cls._duplicate_cols is None else cls._duplicate_cols
        )
        log.info(f"Checking for Duplicates on columns: {cls._duplicate_cols}")
        if cls._save_duplicates:
            cls._duplicates = df[
                df.duplicated(subset=cls._duplicate_cols, keep=False)
            ].copy()
            cls._duplicates.sort_values(
                by=cls._duplicate_cols, ascending=False, inplace=True
            )
            cls._duplicates.to_csv("duplicates.log", index=False)

        if df.duplicated(subset=cls._duplicate_cols).any():
            log.error(
                "Duplicates found in the dataframe, to check duplicates run with _save_duplicates=True"
            )
            return False

        return True

    @pa.dataframe_check
    def check_sorting(cls, df):
        """
        Check for sorting in the dataframe
        """
        if not cls._check_sort:
            return True
        if not cls._check_month_names:
            log.warning("Cannot check sorting without month values check")
            return False
        if not cls._null_values_in_date_cols_check_result:
            log.warning(
                "Skipping sorting check because null values in date cols check failed"
            )
            return False
        if not cls._month_values_check_result:
            log.warning("Skipping sorting check because month values check failed")
            return False
        if cls._sorting_cols is None:
            cls._sorting_cols = get_date_month_cols(df)
        elif check_dfcols(df, cls._sorting_cols):
            return False

        if not cls.check_null_values_in_temporal(df):
            log.error(f"Null values found in columns {cls._sorting_cols}")
            return False

        data = convert_date_col_format(df, cls._sorting_cols)
        data = df.copy()
        data = convert_month_values(data, cls._sorting_cols)

        return data[cls._sorting_cols].equals(
            data[cls._sorting_cols].sort_values(
                by=cls._sorting_cols, kind="mergesort", ascending=False
            )
        )
