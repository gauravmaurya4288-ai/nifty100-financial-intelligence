from src.analytics.ratios import *


def test_debt_free():
    assert debt_to_equity(
        0,
        100,
        200
    ) == 0


def test_negative_equity():
    assert debt_to_equity(
        100,
        -50,
        -100
    ) is None


def test_normal_de():
    assert debt_to_equity(
        300,
        100,
        200
    ) == 1.0


def test_interest_zero():
    assert interest_coverage_ratio(
        100,
        50,
        0
    ) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_icr_warning():
    assert icr_warning(1.2) is True


def test_net_debt():
    assert net_debt(
        500,
        150
    ) == 350


def test_asset_turnover():
    assert asset_turnover(
        1000,
        500
    ) == 2.0