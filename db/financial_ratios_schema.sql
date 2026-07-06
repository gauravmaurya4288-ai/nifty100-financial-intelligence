CREATE TABLE financial_ratios (

    company_id TEXT NOT NULL,
    year TEXT NOT NULL,

    -------------------------------------------------
    -- Profitability
    -------------------------------------------------

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    return_on_capital_employed_pct REAL,
    return_on_assets_pct REAL,

    -------------------------------------------------
    -- Leverage
    -------------------------------------------------

    debt_to_equity REAL,
    high_leverage_flag INTEGER,

    interest_coverage REAL,
    icr_label TEXT,
    icr_warning INTEGER,

    net_debt REAL,
    asset_turnover REAL,

    -------------------------------------------------
    -- Cash Flow
    -------------------------------------------------

    free_cash_flow_cr REAL,
    cfo_quality_score TEXT,

    capex_intensity_pct REAL,
    capex_category TEXT,

    fcf_conversion_pct REAL,

    capital_allocation_pattern TEXT,

    -------------------------------------------------
    -- Market Valuation
    -------------------------------------------------

    market_cap_crore REAL,
    enterprise_value_crore REAL,

    pe_ratio REAL,
    pb_ratio REAL,
    ev_ebitda REAL,

    dividend_yield_pct REAL,

    -------------------------------------------------
    -- Other Financials
    -------------------------------------------------

    earnings_per_share REAL,
    book_value_per_share REAL,

    dividend_payout_ratio_pct REAL,

    total_debt_cr REAL,

    cash_from_operations_cr REAL,

    -------------------------------------------------
    -- CAGR
    -------------------------------------------------

    revenue_cagr_3yr REAL,
    revenue_cagr_5yr REAL,
    revenue_cagr_10yr REAL,

    pat_cagr_3yr REAL,
    pat_cagr_5yr REAL,
    pat_cagr_10yr REAL,

    eps_cagr_3yr REAL,
    eps_cagr_5yr REAL,
    eps_cagr_10yr REAL,

    -------------------------------------------------
    -- Flags
    -------------------------------------------------

    revenue_cagr_flag TEXT,
    pat_cagr_flag TEXT,
    eps_cagr_flag TEXT,

    -------------------------------------------------
    -- Composite
    -------------------------------------------------

    composite_quality_score REAL,

    -------------------------------------------------
    -- Audit
    -------------------------------------------------

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY(company_id, year)

);