from fastapi import APIRouter, HTTPException

from src.api.database import execute_query

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get(
    "/{company_id}",
    summary="Company Documents",
    description="Returns all available documents for a company."
)
def get_documents(company_id: str):

    sql = """
    SELECT

        d.company_id,

        c.company_name,

        d.year,

        d.annual_report

    FROM documents d

    JOIN companies c

      ON d.company_id = c.company_id

    WHERE d.company_id = ?

    ORDER BY d.year DESC;
    """

    rows = execute_query(sql, (company_id,))

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No documents found."
        )

    return rows

@router.get(
    "/{company_id}/annual-reports",
    summary="Annual Reports"
)
def annual_reports(company_id: str):

    sql = """
    SELECT

        company_id,

        company_name,

        year,

        report_url,

        status

    FROM annual_reports

    WHERE company_id = ?

    ORDER BY year DESC;
    """

    rows = execute_query(sql, (company_id,))

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Annual reports not found."
        )

    return rows

@router.get(
    "/{company_id}/latest"
)
def latest_report(company_id: str):

    sql = """
    SELECT

        company_id,

        company_name,

        year,

        report_url,

        status

    FROM annual_reports

    WHERE company_id = ?

    ORDER BY year DESC

    LIMIT 1;
    """

    rows = execute_query(sql, (company_id,))

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return rows[0]