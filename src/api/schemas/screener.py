from typing import Optional, List

from pydantic import BaseModel, Field


class ScreenerResult(BaseModel):
    company_id: str
    company_name: str
    broad_sector: Optional[str] = None

    return_on_equity_pct: Optional[float] = None
    return_on_capital_employed_pct: Optional[float] = None

    debt_to_equity: Optional[float] = None
    free_cash_flow_cr: Optional[float] = None

    revenue_cagr_5yr: Optional[float] = None
    pat_cagr_5yr: Optional[float] = None

    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None

    market_cap_crore: Optional[float] = None

    composite_quality_score: Optional[float] = None


class ScreenerResponse(BaseModel):
    success: bool = True

    page: int
    page_size: int

    total_records: int
    total_pages: int

    results: List[ScreenerResult]


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str