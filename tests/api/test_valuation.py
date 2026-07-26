"""
API Tests - Valuation API
"""

import time
import pytest

pytestmark = pytest.mark.api


class TestValuationAPI:

    BASE = "/api/v1/valuation"
    COMPANY = "TCS"

    def test_get_valuation_200(self, client):
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        assert response.status_code == 200

    def test_returns_dictionary(self, client):
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        assert isinstance(response.json(), dict)

    def test_required_fields(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()

        required = [
            "company_id",
            "company_name",
            "market_cap_crore",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
            "dividend_yield_pct",
            "valuation_status",
        ]

        for field in required:
            assert field in data

    def test_company_id(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert data["company_id"] == self.COMPANY

    def test_company_name(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert isinstance(data["company_name"], str)

    def test_market_cap_type(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert data["market_cap_crore"] is None or isinstance(
            data["market_cap_crore"], (int, float)
        )

    def test_pe_ratio_type(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert data["pe_ratio"] is None or isinstance(
            data["pe_ratio"], (int, float)
        )

    def test_pb_ratio_type(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert data["pb_ratio"] is None or isinstance(
            data["pb_ratio"], (int, float)
        )

    def test_ev_ebitda_type(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert data["ev_ebitda"] is None or isinstance(
            data["ev_ebitda"], (int, float)
        )

    def test_dividend_yield_type(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert data["dividend_yield_pct"] is None or isinstance(
            data["dividend_yield_pct"], (int, float)
        )

    def test_valuation_status(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()

        assert data["valuation_status"] in [
            "Undervalued",
            "Fairly Valued",
            "Overvalued",
            "Unknown",
        ]

    def test_invalid_company(self, client):
        response = client.get(f"{self.BASE}/INVALID123")
        assert response.status_code == 404

    def test_content_type(self, client):
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        assert response.headers["content-type"].startswith(
            "application/json"
        )

    def test_response_time(self, client):
        start = time.perf_counter()
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2

    def test_no_server_error(self, client):
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        assert response.status_code != 500