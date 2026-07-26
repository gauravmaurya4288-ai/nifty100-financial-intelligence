"""
API Tests - Documents API
"""

import time
import pytest

pytestmark = pytest.mark.api


class TestDocumentsAPI:

    BASE = "/api/v1/documents"
    COMPANY = "TCS"

    # --------------------------------------------------
    # Documents
    # --------------------------------------------------

    def test_get_documents_200(self, client):
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        assert response.status_code == 200

    def test_documents_returns_list(self, client):
        response = client.get(f"{self.BASE}/{self.COMPANY}")
        assert isinstance(response.json(), list)

    def test_documents_not_empty(self, client):
        data = client.get(f"{self.BASE}/{self.COMPANY}").json()
        assert len(data) > 0

    def test_document_fields(self, client):
        doc = client.get(f"{self.BASE}/{self.COMPANY}").json()[0]

        required = [
            "company_id",
            "company_name",
            "year",
            "annual_report",
        ]

        for field in required:
            assert field in doc

    # --------------------------------------------------
    # Annual Reports
    # --------------------------------------------------

    def test_annual_reports_200(self, client):
        response = client.get(
            f"{self.BASE}/{self.COMPANY}/annual-reports"
        )
        assert response.status_code == 200

    def test_annual_reports_list(self, client):
        response = client.get(
            f"{self.BASE}/{self.COMPANY}/annual-reports"
        )
        assert isinstance(response.json(), list)

    def test_annual_report_fields(self, client):
        report = client.get(
            f"{self.BASE}/{self.COMPANY}/annual-reports"
        ).json()[0]

        required = [
            "company_id",
            "company_name",
            "year",
            "report_url",
            "status",
        ]

        for field in required:
            assert field in report

    # --------------------------------------------------
    # Latest Report
    # --------------------------------------------------

    def test_latest_report_200(self, client):
        response = client.get(
            f"{self.BASE}/{self.COMPANY}/latest"
        )
        assert response.status_code == 200

    def test_latest_returns_dict(self, client):
        response = client.get(
            f"{self.BASE}/{self.COMPANY}/latest"
        )
        assert isinstance(response.json(), dict)

    def test_latest_report_fields(self, client):
        report = client.get(
            f"{self.BASE}/{self.COMPANY}/latest"
        ).json()

        required = [
            "company_id",
            "company_name",
            "year",
            "report_url",
            "status",
        ]

        for field in required:
            assert field in report

    # --------------------------------------------------
    # Invalid Company
    # --------------------------------------------------

    def test_invalid_documents(self, client):
        response = client.get(f"{self.BASE}/INVALID123")
        assert response.status_code == 404

    def test_invalid_annual_reports(self, client):
        response = client.get(
            f"{self.BASE}/INVALID123/annual-reports"
        )
        assert response.status_code == 404

    def test_invalid_latest(self, client):
        response = client.get(
            f"{self.BASE}/INVALID123/latest"
        )
        assert response.status_code == 404

    # --------------------------------------------------
    # General
    # --------------------------------------------------

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