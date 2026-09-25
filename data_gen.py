import pandas as pd
import random
from faker import Faker

fake = Faker("en_NG")
random.seed(42)

def generate_transactions(n=1000):
    ledger = []
    gateway = []

    for i in range(n):
        ref_id = "TXN" + str(100000 + i)
        amount_kobo = random.randint(10000, 5000000)
        txn_date = fake.date_time_between(start_date="-30d", end_date="now")
        customer = fake.name()

        row = {}
        row["reference_id"] = ref_id
        row["amount_kobo"] = amount_kobo
        row["transaction_date"] = txn_date
        row["customer_name"] = customer
        ledger.append(row)

        scenario = random.choices(
            ["perfect", "missing_in_gateway", "missing_in_ledger", "amount_mismatch", "duplicate"],
            weights=[70, 8, 8, 10, 4]
        )[0]

        if scenario == "perfect":
            row2 = {}
            row2["reference_id"] = ref_id
            row2["amount_kobo"] = amount_kobo
            row2["transaction_date"] = txn_date
            row2["customer_name"] = customer
            gateway.append(row2)

        elif scenario == "missing_in_gateway":
            pass

        elif scenario == "missing_in_ledger":
            row3 = {}
            row3["reference_id"] = "TXN" + str(200000 + i)
            row3["amount_kobo"] = random.randint(10000, 5000000)
            row3["transaction_date"] = txn_date
            row3["customer_name"] = fake.name()
            gateway.append(row3)

        elif scenario == "amount_mismatch":
            row4 = {}
            row4["reference_id"] = ref_id
            row4["amount_kobo"] = amount_kobo + random.randint(-500, 500)
            row4["transaction_date"] = txn_date
            row4["customer_name"] = customer
            gateway.append(row4)

        elif scenario == "duplicate":
            row5 = {}
            row5["reference_id"] = ref_id
            row5["amount_kobo"] = amount_kobo
            row5["transaction_date"] = txn_date
            row5["customer_name"] = customer
            gateway.append(row5)
            gateway.append(row5)

    ledger_df = pd.DataFrame(ledger)
    gateway_df = pd.DataFrame(gateway)
    return ledger_df, gateway_df

BASE = "/content/reconciliation-engine"
ledger_df, gateway_df = generate_transactions(1000)

ledger_df.to_csv(BASE + "/data/ledger.csv", index=False)
gateway_df.to_csv(BASE + "/data/gateway.csv", index=False)

print("Ledger: " + str(len(ledger_df)) + " transactions")
print("Gateway: " + str(len(gateway_df)) + " transactions")
print()
print("LEDGER SAMPLE:")
print(ledger_df.head())
print()
print("GATEWAY SAMPLE:")
print(gateway_df.head())