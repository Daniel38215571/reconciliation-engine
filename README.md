# Reconciliation Engine

An automated transaction reconciliation system for fintech, built in Python with a FastAPI service.

## The Problem

Every fintech company processes thousands of daily transactions across two systems:

- An **internal ledger** (our record of what happened)
- A **payment gateway report** (the provider's record of the same transactions)

These two never match perfectly. Failed webhooks, timing differences, duplicates, and rounding errors mean **30% of transactions typically disagree**. Manual reconciliation takes days. Errors mean real money lost.

## The Solution

This engine classifies every transaction automatically:

- `MATCHED` - both systems agree
- `MISSING_IN_GATEWAY` - we recorded it, gateway did not
- `MISSING_IN_LEDGER` - gateway recorded it, we did not
- `AMOUNT_MISMATCH` - both agree it exists, disagree on amount
- `DUPLICATE_IN_GATEWAY` - gateway recorded it more than once

It produces a **value-at-risk** report - the total naira amount that needs investigation - so finance teams know exactly where to focus.

## Architecture

The matching engine uses a **hash map** for O(1) lookups, reducing complexity from O(n squared) to O(n).

The same business logic is exposed two ways:
- **CLI mode** - run the scripts directly
- **API mode** - call the FastAPI endpoints

## Tech Stack

- Python 3.10+
- Pandas (data manipulation)
- Faker (synthetic test data)
- FastAPI + Uvicorn (HTTP API)
- Pytest (testing)

## Files

- `data_gen.py` - generates synthetic ledger and gateway CSVs
- `ingestion.py` - loads and cleans CSVs
- `matching.py` - the core matching algorithm (hash map based)
- `reporting.py` - summary, value-at-risk, and exports
- `api/main.py` - FastAPI application with three endpoints
- `test_matching.py` - five unit tests for the matching engine
- `test_api.py` - five integration tests for the API

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/reconcile` | Upload two CSVs, get summary JSON |
| GET | `/reconcile/{run_id}` | Fetch a previous result |

Interactive docs (once running): `http://localhost:8000/docs`

## How to Run

Install dependencies:
```bash
pip install -r requirements.txt
```

Generate test data:
```bash
python data_gen.py
```

Run the API:
```bash
uvicorn api.main:app --reload
```

Run the tests:
```bash
pytest test_matching.py test_api.py -v
```

## Sample Output

```
MATCHED                : 702
MISSING_IN_GATEWAY     : 161
MISSING_IN_LEDGER      : 81
AMOUNT_MISMATCH        : 93
DUPLICATE_IN_GATEWAY   : 44
value_at_risk_naira    : 485,046.93
```

## What I Learned

- Hash maps reduce matching complexity from O(n squared) to O(n)
- Financial data must be stored as integers (kobo), never floats
- Idempotency is non-negotiable in fintech
- Edge cases (empty inputs, duplicates) are where production bugs hide
- Separating transport layer (FastAPI) from business logic makes both easier to test
- Type annotations in FastAPI generate validation and docs automatically

## Author

Anuoluwapo Daniel Ojo
Full Stack Software Engineer | Lagos, Nigeria
