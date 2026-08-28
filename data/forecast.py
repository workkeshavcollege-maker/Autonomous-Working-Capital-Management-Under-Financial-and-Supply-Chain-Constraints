import datetime
import random
from typing import List, Dict, Any

def project_cashflow(*args, **kwargs) -> List[Dict[str, Any]]:
    """
    Returns a day-by-day cash-flow projection list for the dashboard timeline.
    (Currently uses a dynamic simulated walk until the ML cashflow model is fully integrated)
    """
    # Handle different argument signatures from dashboard.py and monitor.py
    start_date = datetime.date.today()
    current_cash = 0.0
    
    if len(args) >= 2 and isinstance(args[0], datetime.date):
        # dashboard.py calls: project_cashflow(start_date, current_cash)
        start_date = args[0]
        current_cash = float(args[1])
    elif len(args) >= 1:
        # monitor.py calls: project_cashflow(cash_balance, invoices, receivables)
        current_cash = float(args[0])

    days = 30
    cash = current_cash
    projection = []
    
    for i in range(days):
        date_str = (start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        projection.append({"date": date_str, "cash_projection": cash})
        
        # Simulate natural daily cash flow volatility 
        cash += random.uniform(-5000, 10000)
        
    return projection
