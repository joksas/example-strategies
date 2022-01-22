import datetime
from pathlib import Path

import yfinance as yf
from example_strategies import data


def test_ticker_data_path():
    path = data.ticker_data_path("MSFT")
    parts = Path(path).parts

    assert parts[-2] == ".data"
    assert parts[-1][:6] == "MSFT__"
    # Attempt to convert to date
    datetime.datetime.strptime(parts[-1][6:-4], "%Y-%m-%d").date()
    assert parts[-1][-4:] == ".csv"


def test_ticker_data_path_metadata():
    path = "/home/abc/example-strategies/.data/MSFT__2020-01-01.csv"
    ticker, date = data.ticker_data_path_metadata(path)

    assert ticker == "MSFT"
    assert date == datetime.date(2020, 1, 1)


def test_load():
    msft_data = data.load("MSFT")
    print(msft_data)
    assert msft_data.loc["2000-01-10"]["Close"] == 56.125
