import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PAYMENT DELAY MODEL V6
# ============================================================

print("=" * 70)
print("PAYMENT DELAY MODEL V6 - GRADIENT BOOSTING")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(
    "data/ml_dataset.csv",
    low_memory=False
)

print()
print("Total invoices:", len(df))


# ============================================================
# 2. CONVERT DATES
# ============================================================

for col in ["posting_date", "due_in_date", "clear_date"]:
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce"
    )


# ============================================================
# 3. KEEP ONLY KNOWN PAYMENT DELAYS
# ============================================================

df = df[
    df["payment_delay_days"].notna()
].copy()

print(
    "Invoices with known payment delay:",
    len(df)
)


# ============================================================
# 4. SORT BY CUSTOMER + DATE
# ============================================================

df = df.sort_values(
    ["cust_number", "posting_date"]
).reset_index(drop=True)


# ============================================================
# 5. BASIC INVOICE FEATURES
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


# ============================================================
# 6. CUSTOMER HISTORY
#
# IMPORTANT:
# shift(1) means the current invoice is NEVER included
# in its own historical features.
# ============================================================

group = df.groupby(
    "cust_number",
    sort=False
)


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
# 7. CUSTOMER LATE RATE
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
# 8. RECENT CUSTOMER BEHAVIOR
# ============================================================

df["customer_recent_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            window=5,
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
            window=5,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# 9. LAST 3 INVOICES
# ============================================================

df["customer_recent3_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            window=3,
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
            window=3,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# 10. CUSTOMER TREND
# ============================================================

df["customer_delay_trend"] = (
    df["customer_recent3_avg_delay"]
    -
    df["customer_avg_delay"]
)


# ============================================================
# 11. CUSTOMER VOLATILITY
# ============================================================

df["customer_delay_volatility"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            window=5,
            min_periods=2
        )
        .std()
    )
)


# ============================================================
# 12. RECENT 10-INVOICE BEHAVIOR
# ============================================================

df["customer_recent10_avg_delay"] = (
    group["payment_delay_days"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            window=10,
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
            window=10,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# 13. RECENT vs LONG-TERM BEHAVIOR
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
# 14. PAYMENT DELAY CONSISTENCY
# ============================================================

df["customer_delay_range"] = (
    df["customer_max_delay"]
    -
    df["customer_min_delay"]
)


# ============================================================
# 15. LOG INVOICE AMOUNT
# ============================================================

df["log_invoice_amount"] = np.log1p(
    df["invoice_amount"].clip(lower=0)
)


# ============================================================
# 16. CUSTOMER HISTORY STRENGTH
# ============================================================

df["customer_history_strength"] = np.log1p(
    df["customer_invoice_count"]
)


# ============================================================
# 17. FEATURE LIST
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
# 18. CLEAN FEATURES
# ============================================================

for col in numeric_features:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    df[col] = df[col].replace(
        [np.inf, -np.inf],
        np.nan
    )

    df[col] = df[col].fillna(0)


for col in categorical_features:

    df[col] = (
        df[col]
        .fillna("UNKNOWN")
        .astype(str)
    )


# ============================================================
# 19. TIME-BASED SPLIT
# ============================================================

df = df.sort_values(
    "posting_date"
).reset_index(drop=True)


split_date = pd.Timestamp(
    "2020-02-01"
)


train = df[
    df["posting_date"] < split_date
].copy()


test = df[
    df["posting_date"] >= split_date
].copy()


print()
print("=" * 70)
print("TIME-BASED SPLIT")
print("=" * 70)

print()
print("TRAINING PERIOD:")
print(
    train["posting_date"].min(),
    "to",
    train["posting_date"].max()
)

print(
    "Training invoices:",
    len(train)
)

print()
print("TEST PERIOD:")
print(
    test["posting_date"].min(),
    "to",
    test["posting_date"].max()
)

print(
    "Testing invoices:",
    len(test)
)


# ============================================================
# 20. X / Y
# ============================================================

X_train = train[
    numeric_features +
    categorical_features
]

y_train = train[
    "payment_delay_days"
]


X_test = test[
    numeric_features +
    categorical_features
]

y_test = test[
    "payment_delay_days"
]


# ============================================================
# 21. PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(

    transformers=[

        (
            "numeric",
            "passthrough",
            numeric_features
        ),

        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        )
    ]
)


# ============================================================
# 22. HISTOGRAM GRADIENT BOOSTING
# ============================================================

model = HistGradientBoostingRegressor(

    max_iter=400,

    learning_rate=0.05,

    max_leaf_nodes=31,

    max_depth=None,

    min_samples_leaf=20,

    l2_regularization=1.0,

    random_state=42
)


pipeline = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )
    ]
)


# ============================================================
# 23. TRAIN
# ============================================================

print()
print("=" * 70)
print("TRAINING PAYMENT DELAY MODEL V6")
print("=" * 70)

print()
print(
    "Training HistGradientBoosting..."
)


pipeline.fit(
    X_train,
    y_train
)


print()
print(
    "✅ Model V6 training complete!"
)


# ============================================================
# 24. PREDICTION
# ============================================================

print()
print(
    "Generating predictions..."
)


predictions = pipeline.predict(
    X_test
)


# ============================================================
# 25. METRICS
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)


rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)


r2 = r2_score(
    y_test,
    predictions
)


median_error = np.median(
    np.abs(
        y_test.values -
        predictions
    )
)


# ============================================================
# 26. PERFORMANCE
# ============================================================

print()
print("=" * 70)
print("MODEL V6 PERFORMANCE")
print("=" * 70)

print()

print(
    f"MAE              : {mae:.2f} days"
)

print(
    f"RMSE             : {rmse:.2f} days"
)

print(
    f"R²               : {r2:.3f}"
)

print(
    f"Median Abs Error : {median_error:.2f} days"
)


# ============================================================
# 27. COMPARE ALL VERSIONS
# ============================================================

print()
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print()

print(
    "V3 → MAE 3.51 | RMSE 6.78 | R² 0.641"
)

print(
    "V5 → MAE 3.41 | RMSE 6.94 | R² 0.624"
)

print(
    f"V6 → MAE {mae:.2f} | "
    f"RMSE {rmse:.2f} | "
    f"R² {r2:.3f}"
)


# ============================================================
# 28. DETERMINE BEST MODEL
# ============================================================

print()
print("=" * 70)
print("MODEL DECISION")
print("=" * 70)

v3_mae = 3.51
v3_rmse = 6.78
v3_r2 = 0.641

v5_mae = 3.41
v5_rmse = 6.94
v5_r2 = 0.624


if (
    mae < v3_mae
    and rmse < v3_rmse
    and r2 > v3_r2
):

    print()
    print(
        "🏆 V6 BEATS V3 ON ALL THREE MAJOR METRICS"
    )

elif mae < v3_mae:

    print()
    print(
        "🟢 V6 has better MAE than V3"
    )

    print(
        "⚠️ V6 does not beat V3 on every metric"
    )

else:

    print()
    print(
        "⚠️ V6 did not beat V3 on MAE"
    )


# ============================================================
# 29. SAVE MODEL
# ============================================================

model_path = (
    "models/payment_delay_model_v6.pkl"
)


joblib.dump(
    pipeline,
    model_path
)


print()
print("=" * 70)
print("MODEL SAVING")
print("=" * 70)

print()
print(
    "✅ MODEL V6 SAVED!"
)

print()
print(
    "Location:"
)

print(
    model_path
)


# ============================================================
# 30. SAVE TEST PREDICTIONS
# ============================================================

results = test[
    [
        "cust_number",
        "posting_date",
        "due_in_date",
        "total_open_amount",
        "payment_delay_days"
    ]
].copy()


results[
    "predicted_payment_delay"
] = predictions


results[
    "absolute_error"
] = np.abs(
    results["payment_delay_days"]
    -
    results["predicted_payment_delay"]
)


results.to_csv(
    "data/v6_test_predictions.csv",
    index=False
)


# ============================================================
# 31. WORST PREDICTIONS
# ============================================================

worst = (
    results
    .sort_values(
        "absolute_error",
        ascending=False
    )
    .head(20)
)


print()
print("=" * 70)
print("TOP 20 WORST PREDICTIONS")
print("=" * 70)

print()

print(
    worst[
        [
            "cust_number",
            "payment_delay_days",
            "predicted_payment_delay",
            "absolute_error"
        ]
    ].to_string(index=False)
)


# ============================================================
# 32. FINAL
# ============================================================

print()
print("=" * 70)
print("PAYMENT DELAY MODEL V6 COMPLETE")
print("=" * 70)

print()
print(
    "Model:"
)

print(
    "models/payment_delay_model_v6.pkl"
)

print()
print(
    "Test predictions:"
)

print(
    "data/v6_test_predictions.csv"
)

print()
print("=" * 70)
