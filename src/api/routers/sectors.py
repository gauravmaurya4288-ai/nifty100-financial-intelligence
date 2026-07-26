from fastapi import APIRouter, HTTPException

from src.api.database import execute_query
from src.api.schemas.sector import (
    SectorSummary,
    SectorCompaniesResponse,
)

router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"],
)




@router.get(
    "/",
response_model=list[SectorSummary],
summary="Get all sectors"
)
def get_sectors():

        sql = """
        WITH latest_ratios AS (

            SELECT *
            FROM financial_ratios fr

            WHERE year = (
                SELECT MAX(year)
                FROM financial_ratios x
                WHERE x.company_id = fr.company_id
            )

        )

        SELECT

            s.broad_sector,

            COUNT(*) AS company_count,

            ROUND(AVG(fr.return_on_equity_pct),2) AS median_roe,

            ROUND(AVG(fr.pe_ratio),2) AS median_pe,

            ROUND(AVG(fr.debt_to_equity),2) AS median_de

        FROM sectors s

        JOIN latest_ratios fr
            ON s.company_id = fr.company_id

        GROUP BY s.broad_sector

        ORDER BY s.broad_sector;
        """

        return execute_query(sql)

@router.get("/{sector}/companies")
def get_sector_companies(sector: str):

    sql = """
    WITH latest_ratios AS (

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

        fr.return_on_equity_pct,

        fr.return_on_capital_employed_pct,

        fr.pe_ratio,

        fr.pb_ratio,

        fr.market_cap_crore,

        fr.composite_quality_score

    FROM companies c

    JOIN sectors s
        ON c.company_id = s.company_id

    JOIN latest_ratios fr
        ON c.company_id = fr.company_id

    WHERE LOWER(s.broad_sector) = LOWER(?)

    ORDER BY fr.composite_quality_score DESC;
    """

    companies = execute_query(sql, (sector,))
    if not companies:
        raise HTTPException(
            status_code=404,
            detail=f"No companies found for sector '{sector}'"
        )

    return companies