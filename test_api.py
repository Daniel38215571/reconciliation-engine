import os
import sys

sys.path.insert(0, "/content/reconciliation-engine")

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

BASE = "/content/reconciliation-engine"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reconcile_success():
    with open(BASE + "/data/ledger.csv", "rb") as lf:
        with open(BASE + "/data/gateway.csv", "rb") as gf:
            files = {
                "ledger_file": ("ledger.csv", lf, "text/csv"),
                "gateway_file": ("gateway.csv", gf, "text/csv"),
            }
            response = client.post("/reconcile", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["total_ledger_rows"] == 1000
    assert data["total_gateway_rows"] == 964
    assert "run_id" in data
    assert "value_at_risk_naira" in data
    assert data["status_breakdown"]["MATCHED"] == 702


def test_missing_ledger_file():
    with open(BASE + "/data/gateway.csv", "rb") as gf:
        files = {
            "gateway_file": ("gateway.csv", gf, "text/csv"),
        }
        response = client.post("/reconcile", files=files)

    assert response.status_code == 422


def test_get_unknown_run_id():
    response = client.get("/reconcile/nonexistent-run-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"


def test_invalid_csv_schema():
    bad_csv = b"wrong_col,other_col\nfoo,bar\n"

    files = {
        "ledger_file": ("bad.csv", bad_csv, "text/csv"),
        "gateway_file": ("bad.csv", bad_csv, "text/csv"),
    }
    response = client.post("/reconcile", files=files)

    assert response.status_code == 400
