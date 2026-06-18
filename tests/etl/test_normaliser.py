from src.etl.normaliser import (
    normalize_year,
    normalize_ticker,
    normalize_text,
    normalize_currency,
    normalize_percentage
)


def test_normalize_year():
    assert normalize_year("2023") == 2023


def test_normalize_year_spaces():
    assert normalize_year(" 2022 ") == 2022


def test_normalize_ticker():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_ticker_spaces():
    assert normalize_ticker(" reliance ") == "RELIANCE"


def test_normalize_text():
    assert normalize_text(" hello ") == "hello"


def test_currency():
    assert normalize_currency("1,000") == 1000.0


def test_currency_decimal():
    assert normalize_currency("1,250.50") == 1250.50


def test_percentage():
    assert normalize_percentage("25%") == 25.0