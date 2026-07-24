"""
Day 40 - Stock Screener API Test Suite
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/screener"


def test_api(name, params=None, validator=None):
    print("=" * 80)
    print(f"TEST : {name}")

    response = requests.get(BASE_URL, params=params)

    print("Status Code :", response.status_code)

    if response.status_code != 200:
        print("FAILED")
        print(response.text)
        return

    data = response.json()

    print("Records Returned :", len(data))

    if validator:
        validator(data)

    print("PASSED")


# ----------------------------------------------------------------------
# Validators
# ----------------------------------------------------------------------

def check_sector(data):
    assert all(
        row["broad_sector"] == "Financials"
        for row in data
    )


def check_roe(data):
    assert all(
        row["return_on_equity_pct"] >= 20
        for row in data
    )


def check_pe(data):
    assert all(
        row["pe_ratio"] <= 30
        for row in data
    )


def check_pb(data):
    assert all(
        row["pb_ratio"] <= 5
        for row in data
    )


def check_debt(data):
    assert all(
        row["debt_to_equity"] <= 1
        for row in data
    )


def check_market_cap(data):
    assert all(
        row["market_cap_crore"] >= 500000
        for row in data
    )


def check_revenue(data):
    assert all(
        row["revenue_cagr_5yr"] is None
        or row["revenue_cagr_5yr"] >= 10
        for row in data
    )


def check_quality(data):
    assert all(
        row["composite_quality_score"] >= 80
        for row in data
    )


def check_unique(data):
    ids = [row["company_id"] for row in data]
    assert len(ids) == len(set(ids))


# ----------------------------------------------------------------------
# Run Tests
# ----------------------------------------------------------------------

print("\nDAY 40 STOCK SCREENER TEST SUITE\n")

# 1
test_api(
    "Basic Screener",
    validator=check_unique
)

# 2
test_api(
    "Financial Sector",
    {"sector": "Financials"},
    check_sector
)

# 3
test_api(
    "ROE >=20",
    {"roe_min": 20},
    check_roe
)

# 4
test_api(
    "PE <=30",
    {"pe_max": 30},
    check_pe
)

# 5
test_api(
    "PB <=5",
    {"pb_max": 5},
    check_pb
)

# 6
test_api(
    "Debt <=1",
    {"debt_to_equity_max": 1},
    check_debt
)

# 7
test_api(
    "Market Cap >=500000",
    {"market_cap_min": 500000},
    check_market_cap
)

# 8
test_api(
    "Revenue CAGR >=10",
    {"revenue_cagr_5yr_min": 10},
    check_revenue
)

# 9
test_api(
    "Quality Score >=80",
    {"quality_score_min": 80},
    check_quality
)

# 10
test_api(
    "Multiple Filters",
    {
        "sector": "Financials",
        "roe_min": 15,
        "pe_max": 25
    }
)

# 11
test_api(
    "Invalid Sector",
    {"sector": "XYZ"}
)

# 12
test_api(
    "Impossible Filter",
    {"roe_min": 10000}
)

print("\n")
print("=" * 80)
print("ALL DAY 40 TESTS COMPLETED")
print("=" * 80)