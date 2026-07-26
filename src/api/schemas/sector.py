from typing import List, Optional

from pydantic import BaseModel


class SectorSummary(BaseModel):
    broad_sector: str
    company_count: int
    median_roe: Optional[float] = None
    median_pe: Optional[float] = None
    median_de: Optional[float] = None


class SectorCompany(BaseModel):
    company_id: str
    company_name: str

    return_on_equity_pct: Optional[float] = None
    return_on_capital_employed_pct: Optional[float] = None

    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None

    market_cap_crore: Optional[float] = None

    composite_quality_score: Optional[float] = None


class SectorCompaniesResponse(BaseModel):
    sector: str
    company_count: int
    companies: List[SectorCompany]