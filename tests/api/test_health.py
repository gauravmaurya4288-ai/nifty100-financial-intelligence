"""
API Tests - Health Endpoint
"""

import time

import pytest


pytestmark = pytest.mark.api


class TestHealthAPI:
    """Tests for the Health API."""

    def test_health_returns_200(self, client, health_endpoint):
        """Health endpoint should return HTTP 200."""

        response = client.get(health_endpoint)

        assert response.status_code == 200

    def test_health_status_ok(self, client, health_endpoint):
        """Health status should be 'ok'."""

        response = client.get(health_endpoint)

        data = response.json()

        assert "status" in data
        assert data["status"].lower() == "ok"

    def test_health_contains_db_row_counts(self, client, health_endpoint):
        """Health response should include db_row_counts."""

        response = client.get(health_endpoint)

        data = response.json()

        assert "db_row_counts" in data
        assert isinstance(data["db_row_counts"], dict)

    def test_health_contains_expected_tables(
        self,
        client,
        health_endpoint,
        expected_counts,
    ):
        """Health response should contain expected table names."""

        response = client.get(health_endpoint)

        data = response.json()

        row_counts = data["db_row_counts"]

        for table in expected_counts:
            assert table in row_counts

    def test_health_row_counts_are_integers(
        self,
        client,
        health_endpoint,
    ):
        """Every row count should be an integer."""

        response = client.get(health_endpoint)

        row_counts = response.json()["db_row_counts"]

        for value in row_counts.values():
            assert isinstance(value, int)
            assert value >= 0

    def test_health_returns_json(self, client, health_endpoint):
        """Response should be JSON."""

        response = client.get(health_endpoint)

        assert response.headers["content-type"].startswith(
            "application/json"
        )

    def test_health_response_time(self, client, health_endpoint):
        """Health endpoint should respond quickly."""

        start = time.perf_counter()

        response = client.get(health_endpoint)

        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2

    def test_health_database_not_empty(self, client, health_endpoint):
        """Database should contain at least one table with rows."""

        response = client.get(health_endpoint)

        counts = response.json()["db_row_counts"]

        assert any(value > 0 for value in counts.values())

    def test_health_no_server_error(self, client, health_endpoint):
        """Health endpoint should never return HTTP 500."""

        response = client.get(health_endpoint)

        assert response.status_code != 500

    def test_health_response_is_dictionary(self, client, health_endpoint):
        """Top-level response should be a JSON object."""

        response = client.get(health_endpoint)

        assert isinstance(response.json(), dict)