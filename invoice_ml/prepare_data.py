import pandas as pd

print("=" * 60)
print("STEP 2 - PREPARING OUR ML DATA")
print("=" * 60)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

df = pd.read_csv("data/dataset.csv")

print("\nOriginal dataset:")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# --------------------------------------------------
# 2. CONVERT DATES
# --------------------------------------------------

df["clear_date"] = pd.to_datetime(
    df["clear_date"],
    errors="coerce"
)

df["due_in_date"] = pd.to_datetime(
    df["due_in_date"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)

df["posting_date"] = pd.to_datetime(
    df["posting_date"],
    errors="coerce"
)


# --------------------------------------------------
# 3. CREATE PAYMENT DELAY
# --------------------------------------------------

df["payment_delay_days"] = (
    df["clear_date"] - df["due_in_date"]
).dt.days


# --------------------------------------------------
# 4. LOOK AT THE RESULT
# --------------------------------------------------

print("\nPayment delay examples:")

print(
    df[
        [
            "due_in_date",
            "clear_date",
            "payment_delay_days"
        ]
    ].head(10)
)


# --------------------------------------------------
# 5. BASIC INFORMATION
# --------------------------------------------------

print("\nPayment delay statistics:")

print(
    df["payment_delay_days"].describe()
)


# --------------------------------------------------
# 6. COUNT MISSING TARGETS
# --------------------------------------------------

print("\nMissing payment delays:")

print(
    df["payment_delay_days"].isna().sum()
)


# --------------------------------------------------
# 7. COUNT EARLY / ON-TIME / LATE
# --------------------------------------------------

print("\nPayment behavior:")

print(
    "Paid early:",
    (df["payment_delay_days"] < 0).sum()
)

print(
    "Paid on time:",
    (df["payment_delay_days"] == 0).sum()
)

print(
    "Paid late:",
    (df["payment_delay_days"] > 0).sum()
)
