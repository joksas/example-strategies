import datetime
import glob
import os
from pathlib import Path

import pandas as pd
import yfinance as yf


def _data_dir_path() -> str:
    return os.path.join(Path(__file__).parent.parent.absolute(), ".data")


def ticker_data_path(ticker: str) -> str:
    """Returns ticker data's file path.

    Args:
        ticker: Stock symbol.

    Returns:
        Path.
    """
    return os.path.join(_data_dir_path(), f"{ticker.upper()}__{datetime.date.today()}.csv")


def ticker_data_path_pattern(ticker: str) -> str:
    """Returns ticker data's file path pattern that may match data downloaded on different days.

    Args:
        ticker: Stock symbol.

    Returns:
        Path pattern.
    """
    return os.path.join(_data_dir_path(), f"{ticker.upper()}__*.csv")


def ticker_data_path_metadata(path: str) -> tuple[str, datetime.date]:
    """Return metadata from a saved file's path.

    Args:
        path: Path of the file.

    Returns:
        ticker: Stock symbol.
        date: Date last downloaded.
    """
    parts = Path(path).parts
    filename = parts[-1]
    ticker, rest = filename.split("__")
    date_str = rest.split(".")[0]
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    return ticker, date


def load(
    ticker: str,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    source: str = "yahoo",
) -> pd.DataFrame:
    """Loads financial data.

    Args:
        ticker: Stock symbol.
        from_date: Date to get the data from.
        to_date: Date to get the data to.
        source: Source of financial information.

    Returns:
    """
    if source != "yahoo":
        raise ValueError('Currently only "yahoo" is supported as a source.')

    path = ticker_data_path(ticker)

    if os.path.exists(path) and ticker_data_path_metadata(path)[1] == datetime.date.today():
        financial_data = pd.read_csv(path, index_col=0, parse_dates=True)
        return _read_date_range(financial_data, from_date, to_date)

    old_file_paths = glob.glob(ticker_data_path_pattern(ticker))
    for old_file_path in old_file_paths:
        os.remove(old_file_path)
    Path(_data_dir_path()).mkdir(parents=True, exist_ok=True)

    financial_data = yf.download(ticker, period="max", timeout=60.0)
    financial_data.to_csv(path)

    return _read_date_range(financial_data, from_date, to_date)


def _read_date_range(
    financial_data: pd.DataFrame, from_date: datetime.date = None, to_date: datetime.date = None
) -> pd.DataFrame:
    financial_data.index = pd.to_datetime(financial_data.index)
    from_date_f = pd.to_datetime(from_date)
    to_date_f = pd.to_datetime(to_date)
    financial_data_index_f = pd.to_datetime(financial_data.index)

    if from_date is None and to_date is None:
        return financial_data

    if from_date is not None and to_date is None:
        return financial_data[financial_data_index_f >= from_date_f]

    if from_date is None and to_date is not None:
        return financial_data[financial_data_index_f <= to_date_f]

    return financial_data[
        (from_date_f <= financial_data_index_f) & (financial_data_index_f <= to_date_f)
    ]
