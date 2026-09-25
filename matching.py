import pandas as pd


def match_transactions(ledger, gateway):
    """Match ledger and gateway transactions using a hash map.
    Returns a DataFrame with one row per transaction (ledger + gateway).
    """

    ledger_refs = set(ledger["reference_id"])

    dup_counter = gateway["reference_id"].value_counts().to_dict()

    gateway_index = {}
    for _, row in gateway.iterrows():
        ref = row["reference_id"]
        if ref not in gateway_index:
            gateway_index[ref] = row

    results = []
    seen_refs = set()

    for _, l_row in ledger.iterrows():
        ref = l_row["reference_id"]
        l_amount = int(l_row["amount_kobo"])

        if ref not in gateway_index:
            results.append({
                "reference_id": ref,
                "status": "MISSING_IN_GATEWAY",
                "ledger_amount": l_amount,
                "gateway_amount": None,
            })
            continue

        g_row = gateway_index[ref]
        g_amount = int(g_row["amount_kobo"])

        if dup_counter.get(ref, 0) > 1:
            results.append({
                "reference_id": ref,
                "status": "DUPLICATE_IN_GATEWAY",
                "ledger_amount": l_amount,
                "gateway_amount": g_amount,
            })
        elif l_amount == g_amount:
            results.append({
                "reference_id": ref,
                "status": "MATCHED",
                "ledger_amount": l_amount,
                "gateway_amount": g_amount,
            })
        else:
            results.append({
                "reference_id": ref,
                "status": "AMOUNT_MISMATCH",
                "ledger_amount": l_amount,
                "gateway_amount": g_amount,
            })

        seen_refs.add(ref)

    for ref, g_row in gateway_index.items():
        if ref not in seen_refs:
            results.append({
                "reference_id": ref,
                "status": "MISSING_IN_LEDGER",
                "ledger_amount": None,
                "gateway_amount": int(g_row["amount_kobo"]),
            })

    return pd.DataFrame(results)
