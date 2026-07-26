"""
API Tests - Sectors API
"""

import time
import pytest

pytestmark = pytest.mark.api


class TestSectorsAPI:

    BASE = "/api/v1/sectors"

    # --------------------------------------------------
    # Sector Summary
    # --------------------------------------------------

    def test_get_sectors_200(self, client):
        response = client.get(f"{self.BASE}/")
        assert response.status_code == 200

    def test_get_sectors_returns_list(self, client):
        response = client.get(f"{self.BASE}/")
        assert isinstance(response.json(), list)

    def test_sector_count(self, client):
        response = client.get(f"{self.BASE}/")
        assert len(response.json()) == 10

    def test_sector_summary_fields(self, client):
        sector = client.get(f"{self.BASE}/").json()[0]

        required = [
            "broad_sector",
            "company_count",
            "median_roe",
            "median_pe",
            "median_de",
        ]

        for field in required:
            assert field in sector

    def test_sector_name_is_string(self, client):
        sector = client.get(f"{self.BASE}/").json()[0]
        assert isinstance(sector["broad_sector"], str)

    def test_company_count_positive(self, client):
        sector = client.get(f"{self.BASE}/").json()[0]
        assert sector["company_count"] > 0

    def test_median_roe_numeric(self, client):
        sector = client.get(f"{self.BASE}/").json()[0]
        assert isinstance(sector["median_roe"], (int, float))

    def test_median_pe_numeric(self, client):
        sector = client.get(f"{self.BASE}/").json()[0]
        assert isinstance(sector["median_pe"], (int, float))

    def test_median_de_numeric(self, client):
        sector = client.get(f"{self.BASE}/").json()[0]
        assert isinstance(sector["median_de"], (int, float))

    def test_sector_names_unique(self, client):
        sectors = client.get(f"{self.BASE}/").json()
        names = [s["broad_sector"] for s in sectors]
        assert len(names) == len(set(names))

    # --------------------------------------------------
    # Companies in Energy Sector
    # --------------------------------------------------

    def test_energy_sector_returns_200(self, client):
        response = client.get(f"{self.BASE}/Energy/companies")
        assert response.status_code == 200

    def test_energy_sector_returns_list(self, client):
        response = client.get(f"{self.BASE}/Energy/companies")
        assert isinstance(response.json(), list)

    def test_energy_sector_not_empty(self, client):
        response = client.get(f"{self.BASE}/Energy/companies")
        assert len(response.json()) > 0

    def test_company_fields(self, client):
        company = client.get(
            f"{self.BASE}/Energy/companies"
        ).json()[0]

        required = [
            "company_id",
            "company_name",
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "pe_ratio",
            "pb_ratio",
            "market_cap_crore",
            "composite_quality_score",
        ]

        for field in required:
            assert field in company

    def test_company_id_string(self, client):
        company = client.get(
            f"{self.BASE}/Energy/companies"
        ).json()[0]

        assert isinstance(company["company_id"], str)

    def test_market_cap_numeric(self, client):
        company = client.get(
            f"{self.BASE}/Energy/companies"
        ).json()[0]

        assert isinstance(company["market_cap_crore"], (int, float))

    def test_quality_score_numeric(self, client):
        company = client.get(
            f"{self.BASE}/Energy/companies"
        ).json()[0]

        assert isinstance(
            company["composite_quality_score"],
            (int, float),
        )

    # --------------------------------------------------
    # Invalid Sector
    # --------------------------------------------------

    def test_invalid_sector_returns_empty_or_404(self, client):
        response = client.get(
            f"{self.BASE}/InvalidSector/companies"
        )

        assert response.status_code in (200, 404)

        if response.status_code == 200:
            assert response.json() == []

    # --------------------------------------------------
    # General
    # --------------------------------------------------

    def test_content_type(self, client):
        response = client.get(f"{self.BASE}/")

        assert response.headers["content-type"].startswith(
            "application/json"
        )

    def test_response_time(self, client):
        start = time.perf_counter()

        response = client.get(f"{self.BASE}/")

        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2

    def test_no_server_error(self, client):
        response = client.get(f"{self.BASE}/")
        assert response.status_code != 500