from src.analytics.cagr import *


def test_normal_cagr():

    value, flag = calculate_cagr(
        100,
        200,
        5
    )

    assert flag == "OK"
    assert value is not None


def test_turnaround():

    value, flag = calculate_cagr(
        -100,
        200,
        5
    )

    assert value is None
    assert flag == "TURNAROUND"


def test_decline_to_loss():

    value, flag = calculate_cagr(
        200,
        -50,
        5
    )

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():

    value, flag = calculate_cagr(
        -100,
        -50,
        5
    )

    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():

    value, flag = calculate_cagr(
        0,
        200,
        5
    )

    assert value is None
    assert flag == "ZERO_BASE"


def test_insufficient():

    value, flag = calculate_cagr(
        100,
        200,
        0
    )

    assert value is None
    assert flag == "INSUFFICIENT"


def test_revenue():

    value, flag = revenue_cagr(
        100,
        150,
        3
    )

    assert flag == "OK"


def test_pat():

    value, flag = pat_cagr(
        100,
        180,
        5
    )

    assert flag == "OK"


def test_eps():

    value, flag = eps_cagr(
        10,
        20,
        5
    )

    assert flag == "OK"


def test_large_growth():

    value, flag = calculate_cagr(
        100,
        1000,
        10
    )

    assert flag == "OK"