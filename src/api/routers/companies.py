"""
Companies API.
"""

from fastapi import APIRouter, HTTPException

from ..database import execute_query

router = APIRouter()


# -------------------------------------------------------
# List Companies
# -------------------------------------------------------

@router.get("/")
def list_companies():

    sql = """
    SELECT *
    FROM companies
    ORDER BY company_name
    """

    return execute_query(sql)


# -------------------------------------------------------
# Company Profile
# -------------------------------------------------------

@router.get("/{company_id}")
def company_profile(company_id: str):

    sql = """
    SELECT *
    FROM companies
    WHERE company_id = ?
    """

    rows = execute_query(sql, (company_id,))

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return rows[0]


# -------------------------------------------------------
# Profit & Loss
# -------------------------------------------------------

@router.get("/{company_id}/pl")
def profit_loss(company_id: str):

    sql = """
    SELECT *
    FROM profit_loss
    WHERE company_id = ?
    ORDER BY year DESC
    """

    return execute_query(sql, (company_id,))


# -------------------------------------------------------
# Balance Sheet
# -------------------------------------------------------

@router.get("/{company_id}/bs")
def balance_sheet(company_id: str):

    sql = """
    SELECT *
    FROM balance_sheet
    WHERE company_id = ?
    ORDER BY year DESC
    """

    return execute_query(sql, (company_id,))


# -------------------------------------------------------
# Cash Flow
# -------------------------------------------------------

@router.get("/{company_id}/cashflow")
def cashflow(company_id: str):

    sql = """
    SELECT *
    FROM cash_flow
    WHERE company_id = ?
    ORDER BY year DESC
    """

    return execute_query(sql, (company_id,))


# -------------------------------------------------------
# Financial Ratios
# -------------------------------------------------------

@router.get("/{company_id}/ratios")
def ratios(company_id: str):

    sql = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year DESC
    """

    return execute_query(sql, (company_id,))


# -------------------------------------------------------
# Company Tearsheet
# -------------------------------------------------------

@router.get("/{company_id}/tearsheet")
def tearsheet(company_id: str):

    profile = execute_query(
        """
        SELECT *
        FROM companies
        WHERE company_id = ?
        """,
        (company_id,),
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return {
        "profile": profile[0],
        "profit_loss": execute_query(
            """
            SELECT *
            FROM profit_loss
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (company_id,),
        ),
        "balance_sheet": execute_query(
            """
            SELECT *
            FROM balance_sheet
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (company_id,),
        ),
        "cash_flow": execute_query(
            """
            SELECT *
            FROM cash_flow
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (company_id,),
        ),
        "ratios": execute_query(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (company_id,),
        ),
    }