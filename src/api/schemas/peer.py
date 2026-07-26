from typing import List, Optional

from pydantic import BaseModel


class PeerCompany(BaseModel):
    company_id: str
    company_name: str

    roe_percentile: Optional[float]
    roce_percentile: Optional[float]
    pe_percentile: Optional[float]
    pb_percentile: Optional[float]
    market_cap_percentile: Optional[float]
    revenue_cagr_percentile: Optional[float]
    pat_cagr_percentile: Optional[float]
    debt_percentile: Optional[float]
    dividend_percentile: Optional[float]
    quality_percentile: Optional[float]


class RadarData(BaseModel):
    metric: str
    company: float
    peer_average: float
    benchmark: float


class PeerComparison(BaseModel):
    company_id: str
    benchmark_company: str
    radar: List[RadarData]