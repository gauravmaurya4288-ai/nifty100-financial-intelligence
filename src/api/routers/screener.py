"""
Stock Screener API
"""

from typing import Optional

from fastapi import APIRouter, Query

from ..database import execute_query

router = APIRouter()


@router.get("/")
def screener(
    sector: Optional[str] = Query(None),
    market_cap_min: Optional[float] = Query(None),
    market_cap_max: Optional[float] = Query(None),

    # Supports both parameter names
    min_roe: Optional[float] = Query(None),
    roe_min: Optional[float] = Query(None),

    roce_min: Optional[float] = Query(None),
    pe_max: Optional[float] = Query(None),
    pb_max: Optional[float] = Query(None),
    debt_to_equity_max: Optional[float] = Query(None),
    revenue_cagr_5yr_min: Optional[float] = Query(None),
    quality_score_min: Optional[float] = Query(None),
):
    """
    Stock screener with optional filters.
    """

    sql = """
    WITH latest_ratios AS (
        SELECT *
        FROM financial_ratios f1
        WHERE rowid = (
            SELECT MAX(rowid)
            FROM financial_ratios f2
            WHERE f2.company_id = f1.company_id
        )
    )

    SELECT
        c.company_id,
        c.company_name,
        s.broad_sector,
        lr.year,
        lr.market_cap_crore,
        lr.pe_ratio,
        lr.pb_ratio,
        lr.return_on_equity_pct,
        lr.return_on_capital_employed_pct,
        lr.debt_to_equity,
        lr.revenue_cagr_5yr,
        lr.composite_quality_score

    FROM companies c

    LEFT JOIN sectors s
        ON c.company_id = s.company_id

    LEFT JOIN latest_ratios lr
        ON c.company_id = lr.company_id

    WHERE 1 = 1
    """

    params = []

    if sector:
        sql += " AND s.broad_sector = ?"
        params.append(sector)

    if market_cap_min is not None:
        sql += " AND lr.market_cap_crore >= ?"
        params.append(market_cap_min)

    if market_cap_max is not None:
        sql += " AND lr.market_cap_crore <= ?"
        params.append(market_cap_max)

    # Support both ?min_roe= and ?roe_min=
    effective_roe = (
        min_roe if min_roe is not None else roe_min
    )

    if effective_roe is not None:
        sql += " AND lr.return_on_equity_pct >= ?"
        params.append(effective_roe)

    if roce_min is not None:
        sql += " AND lr.return_on_capital_employed_pct >= ?"
        params.append(roce_min)

    if pe_max is not None:
        sql += " AND lr.pe_ratio <= ?"
        params.append(pe_max)

    if pb_max is not None:
        sql += " AND lr.pb_ratio <= ?"
        params.append(pb_max)

    if debt_to_equity_max is not None:
        sql += " AND lr.debt_to_equity <= ?"
        params.append(debt_to_equity_max)

    if revenue_cagr_5yr_min is not None:
        sql += " AND lr.revenue_cagr_5yr >= ?"
        params.append(revenue_cagr_5yr_min)

    if quality_score_min is not None:
        sql += " AND lr.composite_quality_score >= ?"
        params.append(quality_score_min)

    sql += """
    ORDER BY
        lr.composite_quality_score DESC,
        lr.return_on_equity_pct DESC
    """

    return execute_query(sql, tuple(params))


@router.get("/available-sectors")
def available_sectors():
    """
    Return all available sectors.
    """

    sql = """
    SELECT DISTINCT broad_sector
    FROM sectors
    ORDER BY broad_sector
    """

    return execute_query(sql)