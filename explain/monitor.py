def detect_change(previous_state: dict, current_state: dict) -> list:
    """
    Compares previous_state and current_state and returns a list of material changes.
    """
    changes = []
    
    for key, curr_val in current_state.items():
        if key in previous_state:
            prev_val = previous_state[key]
            if prev_val != curr_val:
                changes.append(f"Material change in '{key}': {prev_val} -> {curr_val}")
        else:
            changes.append(f"New metric added '{key}': {curr_val}")
            
    for key, prev_val in previous_state.items():
        if key not in current_state:
            changes.append(f"Metric removed '{key}': {prev_val}")
            
    return changes

def reoptimize(current_state: dict, forecast_func, decide_func):
    """
    Continuous decision loop: re-runs forecast_func, loops through all 
    invoices to re-run decide_func, and returns the newly updated forecast and decisions.
    """
    updated_forecast = forecast_func(
        current_state.get('cash_balance', 0),
        current_state.get('invoices', []),
        current_state.get('receivables', [])
    )
    
    invoices = current_state.get('invoices', [])
    updated_decisions = []
    
    for invoice in invoices:
        decision = decide_func(invoice, updated_forecast)
        updated_decisions.append({
            "invoice_id": invoice.get("invoice_id", "Unknown"),
            "decision": decision
        })
        
    return updated_forecast, updated_decisions