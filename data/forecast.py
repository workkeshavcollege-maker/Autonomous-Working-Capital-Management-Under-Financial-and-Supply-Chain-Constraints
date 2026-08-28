from datetime import date, timedelta
from typing import List, Dict, Any

def project_cashflow(cash_balance: float, invoices: List[Dict[str, Any]], receivables: List[Dict[str, Any]], days: int = 30) -> List[Dict[str, Any]]:
    """
    Projects the business's cash balance forward day by day.
    
    Returns a list of {date, projected_balance} for each of the next `days` days.
    This serves as the baseline forecast for the Decision Engine (Person B) and Explainability (Person C).
    
    Assumptions:
    - Invoices: Assumes payment on the exact `due_date` for the full amount. Deciding whether to pay 
      early to capture `discount_pct` is the Decision Engine's job; this function just provides the baseline.
    - Receivables: Uses a simple Expected Value (EV) adjustment. If an invoice has a 30% chance of delay, 
      we only recognize 70% of the cash on the expected date. This provides a conservative, easily explainable 
      forecast without statistically complex simulations.
    """
    today = date.today()
    current_balance = cash_balance
    projection = []
    
    # Walk forward day by day (starting tomorrow)
    for i in range(1, days + 1):
        current_date = today + timedelta(days=i)
        date_str = current_date.isoformat()
        
        # 1. Process expected cash inflows (Receivables)
        for rec in receivables:
            if rec.get("expected_date") == date_str:
                # Expected value adjustment: Amount * Probability of arriving on time
                prob_on_time = 1.0 - rec.get("delay_probability", 0.0)
                expected_inflow = rec.get("amount", 0.0) * prob_on_time
                current_balance += expected_inflow
                
        # 2. Process expected cash outflows (Invoices)
        for inv in invoices:
            if inv.get("due_date") == date_str:
                # Baseline: Pay the full amount on the actual due date
                current_balance -= inv.get("amount", 0.0)
                
        projection.append({
            "date": date_str,
            "projected_balance": round(current_balance, 2)
        })
        
    return projection
