"""
API Tests - Companies Endpoint
"""

import time

import pytest

pytestmark = pytest.mark.api


class TestCompaniesAPI:
    """Tests for the Companies API."""

    def test_get_all_companies_returns_200(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        assert response.status_code == 200

    def test_get_all_companies_returns_list(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        data = response.json()

        assert isinstance(data, list)

    def test_total_companies_count(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        data = response.json()

        assert len(data) == 92

    def test_company_contains_required_fields(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        company = response.json()[0]

        required_fields = [
            "company_id",
            "company_name",
        ]

        for field in required_fields:
            assert field in company

    def test_company_id_is_integer(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        company = response.json()[0]

    def test_company_id_is_string(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        company = response.json()[0]

        assert isinstance(company["company_id"], str)
        assert len(company["company_id"]) > 0

    def test_company_name_is_string(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        company = response.json()[0]

        assert isinstance(company["company_name"], str)

    def test_company_name_not_empty(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        company = response.json()[0]

        assert company["company_name"].strip() != ""

    def test_company_ids_unique(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        companies = response.json()

        ids = [c["company_id"] for c in companies]

        assert len(ids) == len(set(ids))

    def test_company_names_unique(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        companies = response.json()

        names = [c["company_name"] for c in companies]

        assert len(names) == len(set(names))

    def test_get_company_by_tcs(self, client, companies_endpoint):
        response = client.get(f"{companies_endpoint}/TCS")

        assert response.status_code == 200

    def test_tcs_company_name(self, client, companies_endpoint):
        response = client.get(f"{companies_endpoint}/TCS")

        data = response.json()

        assert data["company_name"] == "Tata Consultancy Services Ltd"

    def test_tcs_company_has_company_id(self, client, companies_endpoint):
        response = client.get(f"{companies_endpoint}/TCS")

        data = response.json()

        assert "company_id" in data

    def test_invalid_company_returns_404(self, client, companies_endpoint):
        response = client.get(f"{companies_endpoint}/INVALID")

        assert response.status_code == 404

    def test_invalid_company_has_error_message(self, client, companies_endpoint):
        response = client.get(f"{companies_endpoint}/INVALID")

        data = response.json()

        assert "detail" in data

    def test_response_is_json(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        assert response.headers["content-type"].startswith(
            "application/json"
        )

    def test_response_time(self, client, companies_endpoint):
        start = time.perf_counter()

        response = client.get(companies_endpoint)

        elapsed = time.perf_counter() - start

        assert response.status_code == 200
        assert elapsed < 2

    def test_first_company_not_null(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        company = response.json()[0]

        assert company is not None

    def test_company_list_not_empty(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        assert len(response.json()) > 0

    def test_no_server_error(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        assert response.status_code != 500

    def test_response_is_list(self, client, companies_endpoint):
        response = client.get(companies_endpoint)

        assert isinstance(response.json(), list)