import pandas as pd
import json
from datetime import datetime


def summarize(results, ledger, gateway):
    summary = {}
    summary["reconciliation_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary["total_ledger_rows"] = len(ledger)
    summary["total_gateway_rows"] = len(gateway)
    summary["total_classifications"] = len(results)

    status_counts = results["status"].value_counts().to_dict()
    summary["status_breakdown"] = {}
    for status in ["MATCHED", "MISSING_IN_GATEWAY", "MISSING_IN_LEDGER", "AMOUNT_MISMATCH", "DUPLICATE_IN_GATEWAY"]:
        summary["status_breakdown"][status] = int(status_counts.get(status, 0))

    value_at_risk = 0
    for _, row in results.iterrows():
        if row["status"] == "MISSING_IN_GATEWAY":
            if pd.notna(row["ledger_amount"]):
                value_at_risk += int(row["ledger_amount"])
        elif row["status"] == "AMOUNT_MISMATCH":
            diff = abs(int(row["ledger_amount"]) - int(row["gateway_amount"]))
            value_at_risk += diff
        elif row["status"] == "DUPLICATE_IN_GATEWAY":
            if pd.notna(row["gateway_amount"]):
                value_at_risk += int(row["gateway_amount"])
    summary["value_at_risk_kobo"] = value_at_risk
    summary["value_at_risk_naira"] = round(value_at_risk / 100, 2)

    return summary


def discrepancies_only(results):
    mask = results["status"] != "MATCHED"
    return results[mask].copy()
