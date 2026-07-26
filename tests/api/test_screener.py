"""
API Tests - Screener Endpoint
"""

import time

import pytest

pytestmark = pytest.mark.api


class TestScreenerAPI:

    def test_screener_returns_200(self, client, screener_endpoint):
        response = client.get(screener_endpoint)
        assert response.status_code == 200

    def test_screener_returns_list(self, client, screener_endpoint):
        response = client.get(screener_endpoint)
        assert isinstance(response.json(), list)

    def test_screener_not_empty(self, client, screener_endpoint):
        response = client.get(screener_endpoint)
        assert len(response.json()) > 0

    def test_company_contains_required_fields(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        company = response.json()[0]

        required = [
        "company_id",
        "company_name",
        "broad_sector",
        "year",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "composite_quality_score",
         ]

        for field in required:
            assert field in company

    def test_company_id_is_string(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        company = response.json()[0]

        assert isinstance(company["company_id"], str)

    def test_market_cap_is_number(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        company = response.json()[0]

        assert isinstance(company["market_cap_crore"], (int, float))

    def test_roe_is_number(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        company = response.json()[0]

        assert isinstance(company["return_on_equity_pct"], (int, float))

    def test_quality_score_is_number(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        company = response.json()[0]

        assert isinstance(company["composite_quality_score"], (int, float))

    def test_filter_sector_energy(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?sector=Energy"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["broad_sector"] == "Energy"

    def test_filter_roe(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?roe_min=15"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["return_on_equity_pct"] >= 15

    def test_filter_roce(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?roce_min=20"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["return_on_capital_employed_pct"] >= 20

    def test_filter_pe(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?pe_max=25"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["pe_ratio"] <= 25

    def test_filter_pb(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?pb_max=5"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["pb_ratio"] <= 5

    def test_filter_debt(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?debt_to_equity_max=1"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["debt_to_equity"] <= 1

    def test_filter_quality_score(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?quality_score_min=40"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["composite_quality_score"] >= 40

    def test_filter_revenue_cagr(self, client, screener_endpoint):

        response = client.get(
            f"{screener_endpoint}?revenue_cagr_5yr_min=10"
        )

        assert response.status_code == 200

        for company in response.json():
            assert company["revenue_cagr_5yr"] >= 10

    def test_content_type_json(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        assert response.headers["content-type"].startswith(
            "application/json"
        )

    def test_response_time(self, client, screener_endpoint):

        start = time.perf_counter()

        response = client.get(screener_endpoint)

        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2

    def test_no_server_error(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        assert response.status_code != 500

    def test_response_is_list(self, client, screener_endpoint):

        response = client.get(screener_endpoint)

        assert isinstance(response.json(), list)