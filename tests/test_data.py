import datetime
from pathlib import Path

import pytest
from example_strategies import data


def test_ticker_data_path():
    path = data.ticker_data_path("MSFT")
    parts = Path(path).parts

    assert parts[-2] == ".data"
    assert parts[-1][:6] == "MSFT__"
    # Attempt to convert to date
    datetime.datetime.strptime(parts[-1][6:-4], "%Y-%m-%d").date()
    assert parts[-1][-4:] == ".csv"


def test_ticker_data_path_pattern():
    path = data.ticker_data_path_pattern("MSFT")
    parts = Path(path).parts

    assert parts[-2] == ".data"
    assert parts[-1] == "MSFT__*.csv"


def test_ticker_data_path_metadata():
    path = "/home/abc/example-strategies/.data/MSFT__2020-01-01.csv"
    ticker, date = data.ticker_data_path_metadata(path)

    assert ticker == "MSFT"
    assert date == datetime.date(2020, 1, 1)


load_testdata = [
    (
        "MSFT",
        None,
        None,
        datetime.date(2000, 1, 10),
        56.125,
    ),
    (
        "MSFT",
        datetime.date(2000, 1, 1),
        datetime.date(2000, 1, 31),
        datetime.date(2000, 1, 10),
        56.125,
    ),
    (
        "MSFT",
        None,
        datetime.date(2000, 1, 31),
        datetime.date(2000, 1, 10),
        56.125,
    ),
    (
        "MSFT",
        None,
        datetime.date(2000, 1, 31),
        datetime.date(2000, 2, 10),
        None,
    ),
    (
        "MSFT",
        datetime.date(2000, 1, 1),
        None,
        datetime.date(2000, 1, 10),
        56.125,
    ),
    (
        "MSFT",
        datetime.date(2000, 1, 1),
        None,
        datetime.date(1999, 12, 10),
        None,
    ),
    (
        "MSFT",
        datetime.date(2000, 1, 1),
        datetime.date(2000, 1, 31),
        datetime.date(2000, 2, 10),
        None,
    ),
]


@pytest.mark.parametrize("ticker,from_date,to_date,test_date,close_price", load_testdata)
def test_load(ticker, from_date, to_date, test_date, close_price):
    test_date_str = test_date.strftime("%Y-%m-%d")
    financial_data = data.load(ticker, from_date=from_date, to_date=to_date)
    if close_price is not None:
        assert financial_data.loc[test_date_str]["Close"] == close_price
    else:
        with pytest.raises(KeyError):
            financial_data.loc[test_date_str]["Close"]
