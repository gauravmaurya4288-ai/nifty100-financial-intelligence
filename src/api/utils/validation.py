from fastapi import HTTPException


ALLOWED_SORT_FIELDS = {
    "roe": "return_on_equity_pct",
    "roce": "return_on_capital_employed_pct",
    "pe": "pe_ratio",
    "pb": "pb_ratio",
    "market_cap": "market_cap_crore",
    "quality": "composite_quality_score",
    "revenue_cagr": "revenue_cagr_5yr",
    "pat_cagr": "pat_cagr_5yr",
}


def validate_positive(value, name):
    if value is not None and value < 0:
        raise HTTPException(
            status_code=400,
            detail=f"{name} cannot be negative."
        )


def validate_sort(sort_by: str):
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field '{sort_by}'."
        )


def validate_sort_order(order: str):
    if order.lower() not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="sort_order must be asc or desc."
        )


def validate_page(page: int, page_size: int):
    if page < 1:
        raise HTTPException(400, "page must be >=1")

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            400,
            "page_size must be between 1 and 100."
        )