import joblib
import os

# Load the trained ML components and encoders once when the engine starts
current_dir = os.path.dirname(__file__)
model = joblib.load(os.path.join(current_dir, 'xgb_scorer.pkl'))
le_pri = joblib.load(os.path.join(current_dir, 'le_pri.pkl'))
le_act = joblib.load(os.path.join(current_dir, 'le_act.pkl'))

def score_action(invoice, action, forecast, weights=None):
    """
    Evaluates a working capital financial action using the trained XGBoost model.
    - invoice: dictionary containing invoice metadata (amount, discount_pct, supplier_priority, etc.)
    - action: string representing the chosen action (e.g., 'take_discount', 'pay_at_maturity', 'delay_payment')
    - forecast: dictionary from Teammate D's model containing 'predicted_delay_days'
    """
    # 1. Extract features from the request and Teammate D's forecast
    amount = invoice.get('amount', invoice.get('InvoiceAmount', 0))
    expected_delay = forecast.get('predicted_delay_days', forecast.get('expected_delay', 0))
    discount = invoice.get('discount_pct', 0.0)
    priority_str = invoice.get('supplier_priority', 'high')

    # 2. Safely encode categorical strings (fallback to index 0 if unknown)
    priority_encoded = le_pri.transform([priority_str])[0] if priority_str in le_pri.classes_ else 0
    action_encoded = le_act.transform([action])[0] if action in le_act.classes_ else 0

    # 3. Run prediction through your XGBoost model
    features = [[amount, expected_delay, discount, priority_encoded, action_encoded]]
    predicted_score = float(model.predict(features)[0])

    # 4. Return structured dictionary formatted for Gemini rationale & dashboard display
    return {
        'total_score': predicted_score,
        'sub_scores': {
            'liquidity_impact': predicted_score * 0.3, 
            'financing_cost': predicted_score * 0.2,
            'discount_value': discount * 10,
            'supplier_priority_risk': priority_encoded * 0.3,
            'forecast_penalty': max(0.0, 1.0 - (expected_delay / 30.0)) * 0.1
        }
    }