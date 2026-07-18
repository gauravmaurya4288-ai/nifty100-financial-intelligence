import math


def calculate_cagr(start_value, end_value, years):
    """
    Generic CAGR calculator.

    Returns:
        (cagr_value, flag)
    """

    # Insufficient years
    if years <= 0:
        return None, "INSUFFICIENT"

    # Zero base
    if start_value == 0:
        return None, "ZERO_BASE"

    # Positive -> Negative
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative -> Positive
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # Negative -> Negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    try:
        cagr = (
            (end_value / start_value) ** (1 / years) - 1
        ) * 100

        return round(cagr, 2), "OK"

    except Exception:
        return None, "ERROR"
    
def revenue_cagr(start_sales, end_sales, years):
    return calculate_cagr(start_sales, end_sales, years)


def pat_cagr(start_profit, end_profit, years):
    return calculate_cagr(start_profit, end_profit, years)


def eps_cagr(start_eps, end_eps, years):
    return calculate_cagr(start_eps, end_eps, years)