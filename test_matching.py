import pandas as pd
from matching import match_transactions


def make_ledger(rows):
    if len(rows) == 0:
        return pd.DataFrame(columns=["reference_id", "amount_kobo"])
    df = pd.DataFrame(rows)
    df["reference_id"] = df["reference_id"].astype(str)
    df["amount_kobo"] = df["amount_kobo"].astype(int)
    return df


def test_perfect_match():
    ledger = make_ledger([{"reference_id": "TXN001", "amount_kobo": 5000}])
    gateway = make_ledger([{"reference_id": "TXN001", "amount_kobo": 5000}])
    result = match_transactions(ledger, gateway)
    assert len(result) == 1
    assert result.iloc[0]["status"] == "MATCHED"


def test_missing_in_gateway():
    ledger = make_ledger([{"reference_id": "TXN001", "amount_kobo": 5000}])
    gateway = make_ledger([{"reference_id": "TXN999", "amount_kobo": 5000}])
    result = match_transactions(ledger, gateway)
    statuses = set(result["status"])
    assert "MISSING_IN_GATEWAY" in statuses
    assert "MISSING_IN_LEDGER" in statuses


def test_amount_mismatch():
    ledger = make_ledger([{"reference_id": "TXN001", "amount_kobo": 5000}])
    gateway = make_ledger([{"reference_id": "TXN001", "amount_kobo": 6000}])
    result = match_transactions(ledger, gateway)
    assert len(result) == 1
    assert result.iloc[0]["status"] == "AMOUNT_MISMATCH"


def test_duplicate_in_gateway():
    ledger = make_ledger([{"reference_id": "TXN001", "amount_kobo": 5000}])
    gateway = make_ledger([{"reference_id": "TXN001", "amount_kobo": 5000}, {"reference_id": "TXN001", "amount_kobo": 5000}])
    result = match_transactions(ledger, gateway)
    assert len(result) == 1
    assert result.iloc[0]["status"] == "DUPLICATE_IN_GATEWAY"


def test_empty_inputs():
    ledger = make_ledger([])
    gateway = make_ledger([])
    result = match_transactions(ledger, gateway)
    assert len(result) == 0
