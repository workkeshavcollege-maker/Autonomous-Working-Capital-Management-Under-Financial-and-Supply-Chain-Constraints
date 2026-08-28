import pandas as pd
import xgboost as xgb
import joblib
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder

# 1. Load the authentic B2B Accounts Receivable dataset
csv_name = 'WA_Fn-UseC_-Accounts-Receivable.csv'
df = pd.read_csv(csv_name)

# 2. Clean and map columns to match the Decision Engine requirements
df = df.rename(columns={
    'InvoiceAmount': 'amount', 
    'DaysLate': 'expected_delay'
})

# Ensure delay is non-negative
df['expected_delay'] = df['expected_delay'].fillna(0).clip(lower=0)

# Simulate business constraints (discount percentages and supplier priorities) for action modeling
np.random.seed(42)
df['discount_pct'] = np.random.choice([0.0, 0.02, 0.05], len(df))
df['supplier_priority'] = np.random.choice(['low', 'high', 'critical'], len(df))
df['action'] = np.random.choice(['take_discount', 'pay_at_maturity', 'delay_payment'], len(df))

# 3. Define the target score logic based on financial trade-offs
def calculate_target(row):
    score = 0.5
    if row['action'] == 'take_discount' and row['discount_pct'] > 0:
        score += 0.3
    if row['action'] == 'delay_payment' and row['supplier_priority'] == 'critical':
        score -= 0.4 
    if row['expected_delay'] > 10 and row['action'] != 'delay_payment':
        score -= 0.2
        
    return max(0.0, min(1.0, score))

df['target_score'] = df.apply(calculate_target, axis=1)

# 4. Encode categorical variables into numbers
le_pri = LabelEncoder()
df['priority_encoded'] = le_pri.fit_transform(df['supplier_priority'])
le_act = LabelEncoder()
df['action_encoded'] = le_act.fit_transform(df['action'])

X = df[['amount', 'expected_delay', 'discount_pct', 'priority_encoded', 'action_encoded']]
y = df['target_score']

# 5. Train XGBoost model (with automatic fallback if CUDA is unavailable)
print("Training XGBoost on Accounts Receivable dataset...")
try:
    model = xgb.XGBRegressor(tree_method='hist', device='cuda', n_estimators=100)
    model.fit(X, y)
except Exception:
    model = xgb.XGBRegressor(tree_method='hist', device='cpu', n_estimators=100)
    model.fit(X, y)

# 6. Save model and encoders into the engine folder
engine_path = os.path.join(os.getcwd(), 'engine')
os.makedirs(engine_path, exist_ok=True) 

joblib.dump(model, os.path.join(engine_path, 'xgb_scorer.pkl'))
joblib.dump(le_pri, os.path.join(engine_path, 'le_pri.pkl'))
joblib.dump(le_act, os.path.join(engine_path, 'le_act.pkl'))
print("Success! ML training complete and saved to the engine folder.")