# Payment Delay Prediction Model

## Owner

Person A — Payment Delay ML

## Purpose

This module predicts the expected payment delay of an invoice in days.

The prediction is expressed relative to the invoice due date.

Examples:

- `-5` → expected 5 days early
- `0` → expected on time
- `+10` → expected 10 days late

---

## Current Best Model

Model: Payment Delay Model V6

File:

models/payment_delay_model_v6.pkl

Algorithm:

HistGradientBoostingRegressor

---

## Model Performance

Time-based test evaluation:

| Metric | V6 |
|---|---:|
| MAE | 3.06 days |
| RMSE | 6.53 days |
| R² | 0.667 |
| Median Absolute Error | 1.57 days |

V6 is currently the best-performing version among the tested models.

---

## Input

The model uses invoice and customer-behavior features including:

### Invoice features

- invoice amount
- days until due
- posting month
- posting day of week
- posting day
- posting quarter
- posting year

### Customer historical behavior

- previous payment delay
- average historical delay
- maximum historical delay
- minimum historical delay
- invoice count
- historical late-payment rate

### Recent behavior

- recent average delay
- recent late-payment rate
- recent 3-invoice average delay
- recent 3-invoice late rate
- recent 10-invoice average delay
- recent 10-invoice late rate

### Behavioral trend

- customer delay trend
- recent vs historical delay
- recent vs historical late rate
- customer delay volatility
- customer delay range

### Categorical features

- business code
- customer payment terms
- invoice currency
- document type

---

## Output

The open-invoice prediction pipeline generates:

- customer number
- invoice ID
- invoice amount
- due date
- predicted payment delay
- predicted payment date
- payment expectation

Output file:

data/v6_open_invoice_forecast.csv

---

## Payment Expectation

The prediction is classified as:

### EARLY

Predicted delay < -1 day

### ON TIME

Predicted delay between -1 and +1 days

### LATE

Predicted delay > +1 day

---

## Integration With Person B

Person B's Action Scoring Model can consume:

predicted_payment_delay

and:

predicted_payment_date

along with invoice/customer information.

Recommended integration:

Invoice Data
    ↓
Payment Delay V6
    ↓
predicted_payment_delay
predicted_payment_date
    ↓
Person B Action Scoring Model
    ↓
Action Score
    ↓
Recommended Action

---

## Important

The V6 model is a regression model.

It predicts the number of days relative to the invoice due date.

It does NOT directly produce the final collection/action score.

The Action Scoring Model is a downstream component.

---

## Files

### Model

models/payment_delay_model_v6.pkl

### Training

train_model_v6.py

### Prediction

predict_v6.py

### Data preparation

prepare_data.py

### Test predictions

data/v6_test_predictions.csv

### Open invoice predictions

data/v6_open_invoice_forecast.csv

---

## Model Versions

V3:

MAE = 3.51 days  
RMSE = 6.78 days  
R² = 0.641

V5:

MAE = 3.41 days  
RMSE = 6.94 days  
R² = 0.624

V6:

MAE = 3.06 days  
RMSE = 6.53 days  
R² = 0.667

V6 is the current selected model.

