def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow
    """
    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    """
    CFO / PAT Ratio
    """

    if pat == 0:
        return None

    score = cfo / pat

    if score > 1:
        return "High Quality"

    elif score >= 0.5:
        return "Moderate"

    else:
        return "Accrual Risk"


def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity (%)
    """

    if sales == 0:
        return None

    value = abs(investing_activity) / sales * 100

    if value < 3:
        label = "Asset Light"

    elif value <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(value, 2), label


def fcf_conversion(fcf, operating_profit):
    """
    FCF Conversion Rate
    """

    if operating_profit == 0:
        return None

    return round((fcf / operating_profit) * 100, 2)


def capital_allocation_pattern(cfo, cfi, cff, quality=""):
    """
    8-pattern classifier
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):

        if quality == "High Quality":
            return "Shareholder Returns"

        return "Reinvestor"

    elif signs == ("+", "+", "-"):
        return "Liquidating Assets"

    elif signs == ("-", "+", "+"):
        return "Distress Signal"

    elif signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    elif signs == ("+", "+", "+"):
        return "Cash Accumulator"

    elif signs == ("-", "-", "-"):
        return "Pre-Revenue"

    elif signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"