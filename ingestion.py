import pandas as pd

def load_and_clean(path, source_name):
    df = pd.read_csv(path)
    print("Loaded " + source_name + ": " + str(len(df)) + " rows")

    required = ["reference_id", "amount_kobo", "transaction_date"]
    for col in required:
        if col not in df.columns:
            raise ValueError("Missing column: " + col)

    missing_refs = df["reference_id"].isna().sum()
    missing_amounts = df["amount_kobo"].isna().sum()
    print("  Missing reference_id: " + str(missing_refs))
    print("  Missing amount_kobo:  " + str(missing_amounts))

    df = df.copy()

    df["reference_id"] = df["reference_id"].astype(str).str.strip().str.upper()
    df["amount_kobo"] = df["amount_kobo"].astype(int)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    if "customer_name" in df.columns:
        df["customer_name"] = df["customer_name"].astype(str).str.strip()

    print("  Cleaned successfully.")
    print()
    return df
