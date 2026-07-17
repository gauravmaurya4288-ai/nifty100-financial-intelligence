import math


def net_profit_margin(net_profit, sales):
    """Net Profit Margin (%)"""
    if sales == 0 or sales is None:
        return None
    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit, sales):
    """Operating Profit Margin (%)"""
    if sales == 0 or sales is None:
        return None
    return round((operating_profit / sales) * 100, 2)


def opm_cross_check(calculated_opm, source_opm):
    """
    Returns True if difference > 1%
    """
    if calculated_opm is None or source_opm is None:
        return False

    return abs(calculated_opm - source_opm) > 1


def return_on_equity(net_profit, equity_capital, reserves):
    """ROE (%)"""

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def return_on_capital_employed(
    ebit,
    equity_capital,
    reserves,
    borrowings
):
    """ROCE (%)"""

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)


def return_on_assets(net_profit, total_assets):
    """ROA (%)"""

    if total_assets == 0 or total_assets is None:
        return None

    return round((net_profit / total_assets) * 100, 2)

# ==========================================
# LEVERAGE & EFFICIENCY RATIOS
# ==========================================

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt to Equity Ratio
    """

    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def high_leverage_flag(de_ratio, sector):
    """
    Returns True if D/E > 5 and sector is not Financials
    """

    if de_ratio is None:
        return False

    return de_ratio > 5 and sector != "Financials"


def interest_coverage_ratio(operating_profit,
                            other_income,
                            interest):
    """
    Interest Coverage Ratio
    """

    if interest == 0:
        return None

    return round(
        (operating_profit + other_income) / interest,
        2
    )


def icr_label(icr):
    """
    Debt Free Label
    """

    if icr is None:
        return "Debt Free"

    return ""


def icr_warning(icr):
    """
    Interest Coverage Risk
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt
    """

    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover
    """

    if total_assets == 0:
        return None

    return round(sales / total_assets, 2)