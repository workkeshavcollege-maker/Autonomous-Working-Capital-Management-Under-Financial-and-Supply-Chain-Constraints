import pandas as pd
import numpy as np
import joblib

print("=" * 70)
print("PAYMENT DELAY MODEL V6 - OPEN INVOICE PREDICTION")
print("=" * 70)

# ============================================================
# 1. LOAD MODEL
# ============================================================

MODEL_PATH = "models/payment_delay_model_v6.pkl"

model = joblib.load(MODEL_PATH)

print()
print("✅ V6 model loaded")


# ============================================================
# 2. LOAD ORIGINAL DATA
# ============================================================

df = pd.read_csv(
    "data/ml_dataset.csv",
    low_memory=False
)

print("Historical dataset loaded:", len(df))


# ============================================================
# 3. CONVERT DATES
# ============================================================

for col in ["posting_date", "due_in_date", "clear_date"]:
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce"
    )


# ============================================================
# 4. SORT CUSTOMER HISTORY
# ============================================================

df = df.sort_values(
    ["cust_number", "posting_date"]
).reset_index(drop=True)


# ============================================================
# 5. CREATE FEATURES EXACTLY LIKE V6
# ============================================================

df["invoice_amount"] = (
    pd.to_numeric(
        df["total_open_amount"],
        errors="coerce"
    ).fillna(0)
)

df["days_until_due"] = (
    df["due_in_date"] -
    df["posting_date"]
).dt.days

df["posting_month"] = (
    df["posting_date"].dt.month
)

df["posting_day_of_week"] = (
    df["posting_date"].dt.dayofweek
)

df["posting_day"] = (
    df["posting_date"].dt.day
)

df["posting_quarter"] = (
    df["posting_date"].dt.quarter
)

df["posting_year"] = (
    df["posting_date"].dt.year
)


group = df.groupby(
    "cust_number",
    sort=False
)


# ============================================================
# CUSTOMER HISTORY
# ============================================================

df["customer_previous_delay"] = (
    group["payment_delay_days"]
    .shift(1)
)

df["customer_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)

df["customer_max_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .max()
    )
)

df["customer_min_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .min()
    )
)

df["customer_invoice_count"] = (
    group.cumcount()
)


# ============================================================
# LATE RATE
# ============================================================

df["_late_flag"] = (
    df["payment_delay_days"] > 0
).astype(float)

df["customer_late_rate"] = (
    df.groupby(
        "cust_number",
        sort=False
    )["_late_flag"]
    .transform(
        lambda x:
        x.shift(1)
        .expanding()
        .mean()
    )
)


# ============================================================
# RECENT 5
# ============================================================

df["customer_recent_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            5,
            min_periods=1
        )
        .mean()
    )
)

df["customer_recent_late_rate"] = (
    df.groupby(
        "cust_number",
        sort=False
    )["_late_flag"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            5,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# RECENT 3
# ============================================================

df["customer_recent3_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)

df["customer_recent3_late_rate"] = (
    df.groupby(
        "cust_number",
        sort=False
    )["_late_flag"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            3,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# TREND
# ============================================================

df["customer_delay_trend"] = (
    df["customer_recent3_avg_delay"]
    -
    df["customer_avg_delay"]
)


# ============================================================
# VOLATILITY
# ============================================================

df["customer_delay_volatility"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            5,
            min_periods=2
        )
        .std()
    )
)


# ============================================================
# RECENT 10
# ============================================================

df["customer_recent10_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            10,
            min_periods=1
        )
        .mean()
    )
)

df["customer_recent10_late_rate"] = (
    df.groupby(
        "cust_number",
        sort=False
    )["_late_flag"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            10,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# RECENT VS HISTORICAL
# ============================================================

df["recent_vs_historical_delay"] = (
    df["customer_recent_avg_delay"]
    -
    df["customer_avg_delay"]
)

df["recent_vs_historical_late_rate"] = (
    df["customer_recent_late_rate"]
    -
    df["customer_late_rate"]
)


# ============================================================
# CONSISTENCY
# ============================================================

df["customer_delay_range"] = (
    df["customer_max_delay"]
    -
    df["customer_min_delay"]
)


df["log_invoice_amount"] = np.log1p(
    df["invoice_amount"].clip(lower=0)
)


df["customer_history_strength"] = np.log1p(
    df["customer_invoice_count"]
)


# ============================================================
# 6. SELECT OPEN INVOICES
# ============================================================

open_invoices = df[
    df["clear_date"].isna()
].copy()

print()
print("Open invoices:", len(open_invoices))


# ============================================================
# 7. FEATURES
# ============================================================

numeric_features = [

    "invoice_amount",
    "log_invoice_amount",

    "days_until_due",

    "posting_month",
    "posting_day_of_week",
    "posting_day",
    "posting_quarter",
    "posting_year",

    "customer_previous_delay",

    "customer_avg_delay",
    "customer_max_delay",
    "customer_min_delay",

    "customer_invoice_count",

    "customer_late_rate",

    "customer_recent_avg_delay",
    "customer_recent_late_rate",

    "customer_recent3_avg_delay",
    "customer_recent3_late_rate",

    "customer_recent10_avg_delay",
    "customer_recent10_late_rate",

    "customer_delay_trend",

    "customer_delay_volatility",

    "recent_vs_historical_delay",
    "recent_vs_historical_late_rate",

    "customer_delay_range",

    "customer_history_strength"
]


categorical_features = [

    "business_code",
    "cust_payment_terms",
    "invoice_currency",
    "document type"
]


# ============================================================
# 8. CLEAN FEATURES
# ============================================================

for col in numeric_features:

    open_invoices[col] = pd.to_numeric(
        open_invoices[col],
        errors="coerce"
    )

    open_invoices[col] = (
        open_invoices[col]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
    )


for col in categorical_features:

    open_invoices[col] = (
        open_invoices[col]
        .fillna("UNKNOWN")
        .astype(str)
    )


# ============================================================
# 9. PREDICT
# ============================================================

X_open = open_invoices[
    numeric_features +
    categorical_features
]


print()
print("Generating V6 predictions...")


predicted_delay = model.predict(
    X_open
)


# ============================================================
# 10. PAYMENT DATE
# ============================================================

open_invoices[
    "predicted_payment_delay"
] = predicted_delay


open_invoices[
    "predicted_payment_date"
] = (
    open_invoices["due_in_date"]
    +
    pd.to_timedelta(
        predicted_delay,
        unit="D"
    )
)


# ============================================================
# 11. PAYMENT EXPECTATION
# ============================================================

def classify_payment(delay):

    if delay < -1:

        return "EARLY"

    elif delay <= 1:

        return "ON TIME"

    else:

        return "LATE"


open_invoices[
    "payment_expectation"
] = (
    open_invoices[
        "predicted_payment_delay"
    ]
    .apply(classify_payment)
)


# ============================================================
# 12. OUTPUT
# ============================================================

output_columns = [

    "business_code",
    "cust_number",
    "name_customer",
    "invoice_id",

    "posting_date",
    "due_in_date",

    "total_open_amount",

    "cust_payment_terms",

    "customer_invoice_count",
    "customer_avg_delay",
    "customer_recent_avg_delay",
    "customer_late_rate",
    "customer_recent_late_rate",

    "predicted_payment_delay",
    "predicted_payment_date",
    "payment_expectation"
]


output = open_invoices[
    output_columns
].copy()


output = output.rename(
    columns={
        "total_open_amount":
        "invoice_amount"
    }
)


# ============================================================
# 13. SAVE
# ============================================================

output_path = (
    "data/v6_open_invoice_forecast.csv"
)

output.to_csv(
    output_path,
    index=False
)


# ============================================================
# 14. SUMMARY
# ============================================================

print()
print("=" * 70)
print("V6 OPEN INVOICE FORECAST")
print("=" * 70)

print()
print(
    "Total open invoices:",
    len(output)
)

print()
print(
    "EARLY:",
    (output["payment_expectation"] == "EARLY").sum()
)

print(
    "ON TIME:",
    (output["payment_expectation"] == "ON TIME").sum()
)

print(
    "LATE:",
    (output["payment_expectation"] == "LATE").sum()
)

print()
print(
    "Average predicted delay:",
    round(
        output["predicted_payment_delay"].mean(),
        2
    ),
    "days"
)

print()
print(
    "Forecast saved:"
)

print(
    output_path
)

print()
print("=" * 70)
print("V6 PREDICTION COMPLETE")
print("=" * 70)
