import os
import uuid
import tempfile
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException

import sys
sys.path.insert(0, "/content/reconciliation-engine")

from ingestion import load_and_clean
from matching import match_transactions
from reporting import summarize

app = FastAPI(
    title="Reconciliation Engine API",
    description="Automated transaction reconciliation for fintech.",
    version="0.1.0",
)

RESULTS_STORE = {}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/reconcile")
async def reconcile_endpoint(
    ledger_file: UploadFile = File(...),
    gateway_file: UploadFile = File(...),
):
    run_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()

    try:
        ledger_path = os.path.join(temp_dir, "ledger.csv")
        gateway_path = os.path.join(temp_dir, "gateway.csv")

        with open(ledger_path, "wb") as f:
            f.write(await ledger_file.read())

        with open(gateway_path, "wb") as f:
            f.write(await gateway_file.read())

        ledger = load_and_clean(ledger_path, "LEDGER")
        gateway = load_and_clean(gateway_path, "GATEWAY")

        results = match_transactions(ledger, gateway)
        summary = summarize(results, ledger, gateway)

        summary["run_id"] = run_id
        summary["status"] = "COMPLETED"

        RESULTS_STORE[run_id] = summary

        return summary

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Reconciliation failed: " + str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/reconcile/{run_id}")
def get_result(run_id: str):
    if run_id not in RESULTS_STORE:
        raise HTTPException(status_code=404, detail="Run not found")
    return RESULTS_STORE[run_id]
