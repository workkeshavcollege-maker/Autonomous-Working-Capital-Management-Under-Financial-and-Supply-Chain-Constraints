from explain.rationale import explain_decision
from explain.monitor import detect_change

# 1. Test the Monitor (Detecting a delayed receivable)
prev_state = {
    "cash_balance": 100000, 
    "receivables": [{"id": "REC1", "date": "2026-08-29"}]
}
curr_state = {
    "cash_balance": 100000, 
    "receivables": [{"id": "REC1", "date": "2026-09-05"}] # Simulating a delay
}

print("--- TESTING MONITOR ---")
changes = detect_change(prev_state, curr_state)
print("Changes flagged:", changes)

# 2. Test the LLM Rationale
mock_invoice = {
    "id": "INV001", 
    "supplier": "Acme Co", 
    "amount": 50000, 
    "due_date": "2026-09-05", 
    "discount_pct": 0.02
}
mock_scores = {"liquidity": 0.7, "cost": 0.4, "discount": 0.9, "supplier": 0.6, "risk": 0.3}

print("\n--- TESTING LLM EXPLANATION ---")
# This will call Gemini and print the 2-3 sentence explanation
rationale = explain_decision(mock_invoice, "take_discount", mock_scores)
print(rationale)