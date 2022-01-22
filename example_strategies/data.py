import datetime
import os
from pathlib import Path


def _data_dir_path() -> str:
    return os.path.join(Path(__file__).parent.parent.absolute(), ".data")


def ticker_data_path(ticker: str) -> str:
    pass


def ticker_data_path_metadata(path: str) -> tuple[str, datetime.date]:
    pass
