import pandas as pd

from .. import settings


def factly_std_names(filter: str = None):
    if filter is None or filter == "":
        raise Exception("filter is required")

    if filter == "country":
        data = pd.read_csv(settings.COUNTRY_NAMES_URL)
        return data["standard_country_name"].drop_duplicates().dropna().tolist()
    else:
        data = pd.read_csv(settings.STANDARD_NAMES_URL)
        if filter not in data.columns:
            raise Exception("Invalid filter")
        return data[filter].dropna().tolist()
