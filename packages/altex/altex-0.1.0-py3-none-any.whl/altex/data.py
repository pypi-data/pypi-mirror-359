"""Data utilities for Altex charts."""

import numpy as np
import pandas as pd

try:
    from streamlit import cache_data  # streamlit >= 1.18.0
except ImportError:
    from streamlit import experimental_memo as cache_data  # streamlit >= 0.89


def _url_to_dataframe(url: str) -> pd.DataFrame:
    """Collects a CSV/JSON file from a URL and load it into a dataframe.

    Args:
        url: URL of the CSV/JSON file

    Returns:
        Resulting dataframe
    """
    if url.endswith(".csv"):
        return pd.read_csv(url)
    if url.endswith(".json"):
        return pd.read_json(url)
    raise Exception("URL must end with .json or .csv")


# Sample data URLs
WEATHER_DATA_URL = (
    "https://raw.githubusercontent.com/tvst/plost/master/data/seattle-weather.csv"
)
STOCKS_DATA_URL = (
    "https://raw.githubusercontent.com/vega/vega/main/docs/data/stocks.csv"
)
BARLEY_DATA_URL = (
    "https://raw.githubusercontent.com/vega/vega/main/docs/data/barley.json"
)


@cache_data
def get_weather_data() -> pd.DataFrame:
    """Get sample weather data from Seattle.

    Returns:
        DataFrame with weather data including temperature, wind, etc.
    """
    return _url_to_dataframe(WEATHER_DATA_URL)


@cache_data
def get_stocks_data() -> pd.DataFrame:
    """Get sample stock price data.

    Returns:
        DataFrame with stock prices for different symbols over time.
    """
    return _url_to_dataframe(STOCKS_DATA_URL).assign(
        date=lambda df: pd.to_datetime(df.date)
    )


@cache_data
def get_barley_data() -> pd.DataFrame:
    """Get sample barley yield data.

    Returns:
        DataFrame with barley yield data by variety and site.
    """
    return _url_to_dataframe(BARLEY_DATA_URL)


def get_random_data() -> pd.DataFrame:
    """Generate random sample data.

    Returns:
        DataFrame with random numerical data.
    """
    return pd.DataFrame(
        np.random.randn(20, 7),
        columns=list("abcdefg"),
    ).reset_index()
