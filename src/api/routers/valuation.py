from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.api.database import execute_query

router = APIRouter(
    prefix="/valuation",
    tags=["Valuation"]
)


# -------------------------------------------------------
# Response Model
# -------------------------------------------------------

class ValuationResponse(BaseModel):
    company_id: str
    company_name: str

    market_cap_crore: Optional[float]

    pe_ratio: Optional[float]

    pb_ratio: Optional[float]

    ev_ebitda: Optional[float]

    dividend_yield_pct: Optional[float]

    valuation_status: str


# -------------------------------------------------------
# Helper Function
# -------------------------------------------------------

def calculate_valuation_status(pe_ratio):

    if pe_ratio is None:
        return "Unknown"

    if pe_ratio < 15:
        return "Undervalued"

    if pe_ratio <= 30:
        return "Fairly Valued"

    return "Overvalued"


# -------------------------------------------------------
# API Endpoint
# -------------------------------------------------------

@router.get(
    "/{company_id}",
    response_model=ValuationResponse,
    summary="Company Valuation",
    description="Returns latest valuation metrics for a company."
)
def get_company_valuation(company_id: str):

    sql = """
    WITH latest AS (

        SELECT *

        FROM financial_ratios fr

        WHERE year = (

            SELECT MAX(year)

            FROM financial_ratios x

            WHERE x.company_id = fr.company_id

        )

    )

    SELECT

        c.company_id,

        c.company_name,

        l.market_cap_crore,

        l.pe_ratio,

        l.pb_ratio,

        l.ev_ebitda,

        l.dividend_yield_pct

    FROM companies c

    JOIN latest l

        ON c.company_id = l.company_id

    WHERE c.company_id = ?;
    """

    result = execute_query(sql, (company_id,))

    if not result:

        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    row = result[0]

    return ValuationResponse(

        company_id=row["company_id"],

        company_name=row["company_name"],

        market_cap_crore=row["market_cap_crore"],

        pe_ratio=row["pe_ratio"],

        pb_ratio=row["pb_ratio"],

        ev_ebitda=row["ev_ebitda"],

        dividend_yield_pct=row["dividend_yield_pct"],

        valuation_status=calculate_valuation_status(
            row["pe_ratio"]
        )
    )