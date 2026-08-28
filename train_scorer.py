import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

csv_name = 'WA_Fn-UseC_-Accounts-Receivable.csv'
df = pd.read_csv(csv_name)

df = df.rename(columns={'InvoiceAmount': 'amount', 'DaysLate': 'expected_delay'})

df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
df['expected_delay'] = (
    pd.to_numeric(df['expected_delay'], errors='coerce')
    .fillna(0)
    .clip(lower=0)
)

np.random.seed(42)

df['discount_pct'] = np.random.choice([0.0, 0.02, 0.05], size=len(df))
df['supplier_priority'] = np.random.choice(
    ['low', 'high', 'critical'], size=len(df)
)
df['action'] = np.random.choice(
    ['take_discount', 'pay_at_maturity', 'delay_payment'], size=len(df)
)


def calculate_target(row):
  score = 0.5

  if row['action'] == 'take_discount' and row['discount_pct'] > 0:
    if row['discount_pct'] >= 0.05:
      score += 0.30
    elif row['discount_pct'] >= 0.02:
      score += 0.15

  if row['action'] == 'delay_payment' and row['supplier_priority'] == 'critical':
    score -= 0.50

  if row['expected_delay'] > 15 and row['action'] == 'pay_at_maturity':
    score -= 0.25

  if row['amount'] > 50000 and row['action'] == 'take_discount':
    score += 0.10

  return max(0.0, min(1.0, score))


df['target_score'] = df.apply(calculate_target, axis=1)

le_pri = LabelEncoder()
df['priority_encoded'] = le_pri.fit_transform(df['supplier_priority'])
le_act = LabelEncoder()
df['action_encoded'] = le_act.fit_transform(df['action'])

X = df[
    [
        'amount',
        'expected_delay',
        'discount_pct',
        'priority_encoded',
        'action_encoded',
    ]
]
y = df['target_score']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
print(f'Training records: {len(X_train)} | Testing records: {len(X_test)}')

model = xgb.XGBRegressor(
    tree_method='hist',
    device='cpu',
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, predictions)

print('\n========== MODEL PERFORMANCE ==========')
print(f'MAE : {mae:.6f}')
print(f'MSE : {mse:.6f}')
print(f'RMSE : {rmse:.6f}')
print(f'R² : {r2:.6f}')
print('=======================================')

engine_path = os.path.join(os.getcwd(), 'engine')
os.makedirs(engine_path, exist_ok=True)

joblib.dump(model, os.path.join(engine_path, 'xgb_scorer.pkl'))
joblib.dump(le_pri, os.path.join(engine_path, 'le_pri.pkl'))
joblib.dump(le_act, os.path.join(engine_path, 'le_act.pkl'))

print('\n=======================================')
print('SUCCESS! Model saved in:', engine_path)
print('=======================================')