import datetime
import random
from typing import List, Dict, Any

from engine.actions import (
    TAKE_DISCOUNT, PAY_AT_MATURITY, DELAY_PAYMENT,
    BANK_FINANCING, SUPPLIER_FINANCING, HOLD_CASH, PAY_NOW
)

def project_cashflow(*args, **kwargs) -> List[Dict[str, Any]]:
    """
    Returns a day-by-day forward cashflow projection list for the dashboard timeline.
    Accurately factors in:
      1. Starting Treasury Cash Balance.
      2. Baseline operational inflows (daily revenue).
      3. Scheduled payment deductions matching invoice due dates, discounts, and financing actions.
    """
    start_date = datetime.date.today()
    current_cash = 0.0
    invoices = []
    decisions = []
    receivables = []

    # Handle polymorphic positional arguments
    if len(args) >= 2 and isinstance(args[0], datetime.date):
        # Called as: project_cashflow(start_date, current_cash, invoices, decisions)
        start_date = args[0]
        current_cash = float(args[1])
        if len(args) >= 3:
            invoices = args[2]
        if len(args) >= 4:
            decisions = args[3]
    elif len(args) >= 1:
        # Called as: project_cashflow(cash_balance, invoices, receivables)
        try:
            current_cash = float(args[0])
        except (ValueError, TypeError):
            current_cash = 0.0
        if len(args) >= 2:
            invoices = args[1]
        if len(args) >= 3:
            receivables = args[2]

    # Keyword argument overrides
    if "start_date" in kwargs:
        start_date = kwargs["start_date"]
    if "current_cash" in kwargs:
        current_cash = float(kwargs["current_cash"])
    if "invoices" in kwargs:
        invoices = kwargs["invoices"]
    if "decisions" in kwargs:
        decisions = kwargs["decisions"]
    if "receivables" in kwargs:
        receivables = kwargs["receivables"]

    # Map decision actions to invoice IDs
    dec_map = {}
    if decisions:
        for dec in decisions:
            if isinstance(dec, dict):
                inv_id = dec.get("invoice_id") or dec.get("id")
                action = dec.get("action") or dec.get("decision")
                if inv_id and action:
                    dec_map[str(inv_id)] = action

    # Calculate scheduled settlement outflows mapped to payment dates (YYYY-MM-DD)
    scheduled_outflows = {}

    if invoices and isinstance(invoices, list):
        for inv in invoices:
            inv_id = str(inv.get("id") or inv.get("invoice_id", ""))
            amount = float(inv.get("amount", 0.0))
            due_date_str = str(inv.get("due_date", ""))
            disc_pct = float(inv.get("discount_pct", 0.0))
            disc_deadline_str = str(inv.get("discount_deadline", ""))

            action = dec_map.get(inv_id, PAY_AT_MATURITY)
            if isinstance(action, dict):
                action = action.get("action", PAY_AT_MATURITY)
            action_str = str(action).lower()

            if "discount" in action_str or action_str == PAY_NOW:
                # Capture discount: paid early with discount deducted
                net_amount = amount * (1.0 - (disc_pct / 100.0))
                if disc_deadline_str and len(disc_deadline_str) >= 10:
                    pay_date = disc_deadline_str[:10]
                else:
                    pay_date = (start_date + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

            elif "bank" in action_str:
                # Bank Financing: Bank advances cash to vendor early; company repays bank at maturity (due date + 30 days)
                # Outflow is deferred past the 30-day window, protecting immediate liquidity!
                try:
                    due_dt = datetime.datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                    pay_date = (due_dt + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                except Exception:
                    pay_date = (start_date + datetime.timedelta(days=35)).strftime("%Y-%m-%d")
                net_amount = amount * 1.006  # ~0.6% monthly financing interest

            elif "supplier_financing" in action_str:
                # Supplier Financing (Reverse Factoring): SCF partner pays vendor; company settles on extended term
                try:
                    due_dt = datetime.datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                    pay_date = (due_dt + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                except Exception:
                    pay_date = (start_date + datetime.timedelta(days=35)).strftime("%Y-%m-%d")
                net_amount = amount * 1.004

            elif "delay" in action_str:
                # Delay payment: paid after due date with penalty
                penalty_pct = float(inv.get("penalty_pct", 2.0))
                net_amount = amount * (1.0 + (penalty_pct / 100.0))
                try:
                    due_dt = datetime.datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                    pay_date = (due_dt + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
                except Exception:
                    pay_date = (start_date + datetime.timedelta(days=25)).strftime("%Y-%m-%d")

            elif "hold" in action_str:
                # Hold Cash / Liquidity Freeze: Payment deferred beyond current planning horizon
                pay_date = (start_date + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
                net_amount = amount

            else:
                # Pay at maturity on contractual due date
                net_amount = amount
                if due_date_str and len(due_date_str) >= 10:
                    pay_date = due_date_str[:10]
                else:
                    pay_date = (start_date + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

            scheduled_outflows[pay_date] = scheduled_outflows.get(pay_date, 0.0) + net_amount

    # Build 30-day projection
    days = 30
    cash = current_cash
    projection = []
    
    # Baseline steady operating daily revenue inflow
    daily_revenue_inflow = 1200.0

    for i in range(days):
        current_dt = start_date + datetime.timedelta(days=i)
        date_str = current_dt.strftime("%Y-%m-%d")

        # Add operating cash inflow
        cash += daily_revenue_inflow

        # Deduct all scheduled supplier payouts due on this date
        if date_str in scheduled_outflows:
            cash -= scheduled_outflows[date_str]

        projection.append({
            "date": date_str,
            "cash_projection": round(cash, 2)
        })

    return projection
