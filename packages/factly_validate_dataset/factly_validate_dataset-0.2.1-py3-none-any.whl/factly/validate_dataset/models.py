from datetime import datetime
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings

from .app_logger import log


class DateContinuity(BaseSettings):
    cols: List[str] = []
    format_name: str = "year_month"
    frequency: str = "MS"
    skip_dates: List[str] = []

    @model_validator(mode="after")
    def validate_cols(self):
        format_name = self.format_name
        if format_name not in ["year_month", "fiscal_year_month", "date"]:
            log.error(
                "Invalid format_name, possible values are 'year_month', 'fiscal_year_month', 'date'"
            )
            raise ValueError("Invalid format_name")
        if format_name == "date" and len(self.cols) != 1:
            log.error("date format requires exactly 1 column")
            raise ValueError("date format requires exactly 1 column")
        elif format_name in ["year_month", "fiscal_year_month"] and len(self.cols) != 2:
            log.error(
                "year_month and fiscal_year_month formats require exactly 2 columns"
            )
            raise ValueError(
                "year_month and fiscal_year_month formats require exactly 2 columns"
            )
        elif self.skip_dates:
            dates = []
            # check format of skip_dates dd-mm-yyyy
            for date in self.skip_dates:
                try:
                    dates.append(datetime.strptime(date, "%d-%m-%Y"))
                except ValueError:
                    log.error("Invalid date format, should be dd-mm-yyyy")
                    raise ValueError("Invalid date format, should be dd-mm-yyyy")
            log.info(f"Skipping dates: {self.skip_dates}")
            self.skip_dates = dates
        return self
