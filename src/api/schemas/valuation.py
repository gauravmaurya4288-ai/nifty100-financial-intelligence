from typing import Optional

from pydantic import BaseModel


class ValuationResponse(BaseModel):
    company_id: str
    company_name: str

    market_cap_crore: Optional[float]

    pe_ratio: Optional[float]

    pb_ratio: Optional[float]

    ev_ebitda: Optional[float]

    dividend_yield_pct: Optional[float]

    valuation_status: str