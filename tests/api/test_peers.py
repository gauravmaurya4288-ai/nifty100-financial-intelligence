"""
API Tests - Peers API
"""

import time
import pytest

pytestmark = pytest.mark.api


class TestPeersAPI:

    BASE = "/api/v1/peers"
    PEER_GROUP = "IT Services"

    # --------------------------------------------------
    # Peer Group Endpoint
    # --------------------------------------------------

    def test_get_peer_group_200(self, client):
        response = client.get(f"{self.BASE}/{self.PEER_GROUP}")
        assert response.status_code == 200

    def test_returns_list(self, client):
        response = client.get(f"{self.BASE}/{self.PEER_GROUP}")
        assert isinstance(response.json(), list)

    def test_not_empty(self, client):
        response = client.get(f"{self.BASE}/{self.PEER_GROUP}")
        assert len(response.json()) > 0

    # --------------------------------------------------
    # Response Structure
    # --------------------------------------------------

    def test_company_fields(self, client):

        company = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        ).json()[0]

        assert "company_id" in company
        assert "company_name" in company

    def test_company_id_string(self, client):

        company = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        ).json()[0]

        assert isinstance(company["company_id"], str)

    def test_company_name_string(self, client):

        company = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        ).json()[0]

        assert isinstance(company["company_name"], str)

    # --------------------------------------------------
    # Metric Validation
    # --------------------------------------------------

    def test_contains_metrics(self, client):

        company = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        ).json()[0]

        metrics = [
            k for k in company.keys()
            if k not in ("company_id", "company_name")
        ]

        assert len(metrics) > 0

    def test_metric_structure(self, client):

        company = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        ).json()[0]

        for key, value in company.items():

            if key in ("company_id", "company_name"):
                continue

            assert isinstance(value, dict)
            assert "value" in value
            assert "percentile" in value

    # --------------------------------------------------
    # Invalid Peer Group
    # --------------------------------------------------

    def test_invalid_peer_group(self, client):

        response = client.get(
            f"{self.BASE}/INVALID_GROUP"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Peer group not found"

    # --------------------------------------------------
    # Compare Endpoint
    # --------------------------------------------------

    def test_invalid_compare_company(self, client):

        response = client.get(
            f"{self.BASE}/companies/INVALID123/compare"
        )

        assert response.status_code == 404

    # --------------------------------------------------
    # General Tests
    # --------------------------------------------------

    def test_content_type(self, client):

        response = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        )

        assert response.headers["content-type"].startswith(
            "application/json"
        )

    def test_response_time(self, client):

        start = time.perf_counter()

        response = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        )

        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2

    def test_no_server_error(self, client):

        response = client.get(
            f"{self.BASE}/{self.PEER_GROUP}"
        )

        assert response.status_code != 500