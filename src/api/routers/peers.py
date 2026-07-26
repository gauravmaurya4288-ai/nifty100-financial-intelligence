from collections import defaultdict

from fastapi import APIRouter, HTTPException

from src.api.database import execute_query

router = APIRouter(
    prefix="/peers",
    tags=["Peers"],
)


@router.get(
    "/{group_name}",
    summary="Peer Group Analysis",
    description="Returns all companies in a peer group with percentile ranks for every metric.",
)
def get_peer_group(group_name: str):

    sql = """
    SELECT

        c.company_id,
        c.company_name,

        pp.metric,
        pp.metric_value,
        pp.percentile_rank

    FROM peer_groups pg

    JOIN companies c
        ON pg.company_id = c.company_id

    JOIN peer_percentiles pp
        ON pg.company_id = pp.company_id
       AND pg.peer_group_name = pp.peer_group_name

    WHERE LOWER(pg.peer_group_name)=LOWER(?)

    ORDER BY
        c.company_name,
        pp.metric;
    """

    rows = execute_query(sql, (group_name,))

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Peer group not found",
        )

    companies = defaultdict(dict)

    for row in rows:

        cid = row["company_id"]

        companies[cid]["company_id"] = cid
        companies[cid]["company_name"] = row["company_name"]

        companies[cid][row["metric"]] = {
            "value": row["metric_value"],
            "percentile": row["percentile_rank"],
        }

    return list(companies.values())


   



# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def get_peer_group_name(company_id: str):
    sql = """
    SELECT peer_group_name
    FROM peer_groups
    WHERE company_id = ?
    LIMIT 1;
    """

    result = execute_query(sql, (company_id,))

    if not result:
        return None

    return result[0]["peer_group_name"]


def get_benchmark_company(peer_group: str):
    sql = """
    SELECT company_id
    FROM peer_groups
    WHERE peer_group_name = ?
      AND is_benchmark = 1
    LIMIT 1;
    """

    result = execute_query(sql, (peer_group,))

    if not result:
        return None

    return result[0]["company_id"]


def get_latest_ratios(company_id: str):

    sql = """
    WITH latest AS (

        SELECT *

        FROM financial_ratios fr

        WHERE year = (

            SELECT MAX(year)

            FROM financial_ratios x

            WHERE x.company_id = fr.company_id

        )

    )

    SELECT *

    FROM latest

    WHERE company_id = ?;
    """

    result = execute_query(sql, (company_id,))

    if not result:
        return None

    return result[0]


def get_peer_average(peer_group: str):

    sql = """
    WITH latest AS (

        SELECT *

        FROM financial_ratios fr

        WHERE year = (

            SELECT MAX(year)

            FROM financial_ratios x

            WHERE x.company_id = fr.company_id

        )

    )

    SELECT

        AVG(return_on_equity_pct) AS roe,

        AVG(return_on_capital_employed_pct) AS roce,

        AVG(pe_ratio) AS pe,

        AVG(pb_ratio) AS pb,

        AVG(revenue_cagr_5yr) AS rev_cagr,

        AVG(pat_cagr_5yr) AS pat_cagr,

        AVG(debt_to_equity) AS debt,

        AVG(composite_quality_score) AS quality

    FROM latest l

    JOIN peer_groups pg

      ON l.company_id = pg.company_id

    WHERE pg.peer_group_name = ?;
    """

    result = execute_query(sql, (peer_group,))

    return result[0]


# --------------------------------------------------------
# API Endpoint
# --------------------------------------------------------

@router.get(
    "/companies/{ticker}/compare",
    summary="Compare company with peer group",
    description="Returns radar chart data comparing a company, peer average and benchmark."
)
def compare_company(ticker: str):

    peer_group = get_peer_group_name(ticker)

    if peer_group is None:

        raise HTTPException(
            status_code=404,
            detail="Company not found in peer group."
        )

    benchmark = get_benchmark_company(peer_group)

    company = get_latest_ratios(ticker)

    benchmark_company = get_latest_ratios(benchmark)

    peer_avg = get_peer_average(peer_group)

    if company is None:

        raise HTTPException(
            status_code=404,
            detail="Financial ratios not found."
        )

    radar = [

        {
            "metric": "ROE",
            "company": company["return_on_equity_pct"],
            "peer_average": peer_avg["roe"],
            "benchmark": benchmark_company["return_on_equity_pct"]
        },

        {
            "metric": "ROCE",
            "company": company["return_on_capital_employed_pct"],
            "peer_average": peer_avg["roce"],
            "benchmark": benchmark_company["return_on_capital_employed_pct"]
        },

        {
            "metric": "PE",
            "company": company["pe_ratio"],
            "peer_average": peer_avg["pe"],
            "benchmark": benchmark_company["pe_ratio"]
        },

        {
            "metric": "PB",
            "company": company["pb_ratio"],
            "peer_average": peer_avg["pb"],
            "benchmark": benchmark_company["pb_ratio"]
        },

        {
            "metric": "Revenue CAGR 5Y",
            "company": company["revenue_cagr_5yr"],
            "peer_average": peer_avg["rev_cagr"],
            "benchmark": benchmark_company["revenue_cagr_5yr"]
        },

        {
            "metric": "PAT CAGR 5Y",
            "company": company["pat_cagr_5yr"],
            "peer_average": peer_avg["pat_cagr"],
            "benchmark": benchmark_company["pat_cagr_5yr"]
        },

        {
            "metric": "Debt / Equity",
            "company": company["debt_to_equity"],
            "peer_average": peer_avg["debt"],
            "benchmark": benchmark_company["debt_to_equity"]
        },

        {
            "metric": "Quality Score",
            "company": company["composite_quality_score"],
            "peer_average": peer_avg["quality"],
            "benchmark": benchmark_company["composite_quality_score"]
        }

    ]

    return {

        "company": ticker,

        "peer_group": peer_group,

        "benchmark_company": benchmark,

        "radar": radar

    }