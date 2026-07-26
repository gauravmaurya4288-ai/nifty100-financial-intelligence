def build_screener_filters(
    min_roe,
    max_de,
    min_fcf,
    sector,
    min_rev_cagr_5yr,
    min_pat_cagr_5yr,
    max_pe,
):

    clauses = []
    params = []

    if min_roe is not None:
        clauses.append("fr.return_on_equity_pct >= ?")
        params.append(min_roe)

    if max_de is not None:
        clauses.append("fr.debt_to_equity <= ?")
        params.append(max_de)

    if min_fcf is not None:
        clauses.append("fr.free_cash_flow_cr >= ?")
        params.append(min_fcf)

    if sector:
        clauses.append("s.broad_sector = ?")
        params.append(sector)

    if min_rev_cagr_5yr is not None:
        clauses.append("fr.revenue_cagr_5yr >= ?")
        params.append(min_rev_cagr_5yr)

    if min_pat_cagr_5yr is not None:
        clauses.append("fr.pat_cagr_5yr >= ?")
        params.append(min_pat_cagr_5yr)

    if max_pe is not None:
        clauses.append("fr.pe_ratio <= ?")
        params.append(max_pe)

    return clauses, params