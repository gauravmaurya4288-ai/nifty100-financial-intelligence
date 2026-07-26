import requests

API = "http://localhost:8000/api/v1"


def test_health():
    r = requests.get(f"{API}/health")
    assert r.status_code == 200


def test_screener():
    r = requests.get(
        f"{API}/screener?min_roe=15"
    )

    assert r.status_code == 200

    data = r.json()

    assert len(data) > 0

    for company in data:
        assert company["return_on_equity_pct"] >= 15