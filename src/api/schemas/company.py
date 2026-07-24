"""
Company response schemas.
"""

from pydantic import BaseModel


class Company(BaseModel):
    ticker: str
    company_name: str
    sector: str | None = None
    industry: str | None = None


class CompanyDetail(Company):
    market_cap: float | None = None