import datetime
import os
from pathlib import Path


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
