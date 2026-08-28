import streamlit as st
import pandas as pd
import datetime
from typing import List, Dict, Any
import random

# Required Integrations & Imports
try:
    from data.forecast import project_cashflow
    from engine.decide import choose_best_action
    from explain.rationale import explain_decision
    from explain.monitor import detect_change, reoptimize
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    
    # ---------------------------------------------------------
    # Mock Data Generation (Fallback for missing backend)
    # ---------------------------------------------------------
    def project_cashflow(*args, **kwargs) -> List[Dict[str, Any]]:
        """Returns a day-by-day cash-flow projection list"""
        start_date = st.session_state.current_simulated_date
        current_cash = st.session_state.current_cash_balance
        days = 30
        cash = current_cash
        projection = []
        for i in range(days):
            date_str = (start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            projection.append({"date": date_str, "cash_projection": cash})
            # Add some random walk for the projection
            cash += random.uniform(-5000, 10000)
        return projection

    def choose_best_action(invoice: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """Returns a Decision dict matching the required schema"""
        actions = ["take_discount", "delay_payment", "pay_on_time"]
        chosen = random.choice(actions)
        return {
            "invoice_id": invoice["id"],
            "action": chosen,
            "scores": {
                "liquidity": round(random.uniform(0.1, 0.9), 2),
                "cost": round(random.uniform(0.1, 0.9), 2),
                "discount": round(random.uniform(0.1, 0.9), 2),
                "supplier": round(random.uniform(0.1, 0.9), 2),
                "risk": round(random.uniform(0.1, 0.9), 2)
            },
            "rationale": f"Model selected {chosen} based on calculated financial and risk trade-offs."
        }

    def explain_decision(invoice: Dict[str, Any], action: str, scores: Dict[str, Any]) -> str:
        """Returns a plain-English explanation"""
        return (f"The recommended action for Invoice {invoice['id']} is to '{action}'. "
                f"This decision is supported by a liquidity score of {scores.get('liquidity')} "
                f"and a supplier impact score of {scores.get('supplier')}. "
                f"Rationale: Model selected {action} based on calculated financial and risk trade-offs.")

    def detect_change(previous_state: dict, current_state: dict) -> list:
        """Mock monitor function to simulate dynamic real-world financial shifts"""
        return []

    def reoptimize(current_state: dict, forecast_func, decide_func):
        """Mock monitor function to re-evaluate decisions"""
        return [], []

def generate_mock_invoices(base_date: datetime.date) -> List[Dict[str, Any]]:
    """Helper to generate initial invoice data matching the required schema"""
    return [
        {
            "id": f"INV-{random.randint(1000, 9999)}",
            "supplier": random.choice(["Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Industries"]),
            "amount": round(random.uniform(5000, 50000), 2),
            "due_date": (base_date + datetime.timedelta(days=random.randint(10, 45))).strftime("%Y-%m-%d"),
            "discount_pct": round(random.uniform(1.0, 3.0), 2),
            "discount_deadline": (base_date + datetime.timedelta(days=random.randint(2, 10))).strftime("%Y-%m-%d"),
            "penalty_pct": round(random.uniform(1.0, 5.0), 2)
        }
        for _ in range(5)
    ]

# ---------------------------------------------------------
# State Management (st.session_state)
# ---------------------------------------------------------
if "current_simulated_date" not in st.session_state:
    st.session_state.current_simulated_date = datetime.date.today()

if "current_cash_balance" not in st.session_state:
    st.session_state.current_cash_balance = 250000.0

if "active_invoices" not in st.session_state:
    st.session_state.active_invoices = generate_mock_invoices(st.session_state.current_simulated_date)

# ---------------------------------------------------------
# UI Components & Layout
# ---------------------------------------------------------

# 1. Header & Overview
st.title("Working Capital Agent")

if not BACKEND_AVAILABLE:
    st.info("Backend modules not found. Running in simulation mode with robust fallback data.")

st.write(f"**Current Simulated Date:** {st.session_state.current_simulated_date.strftime('%Y-%m-%d')}")

total_outstanding = sum(inv["amount"] for inv in st.session_state.active_invoices)

col1, col2 = st.columns(2)
with col1:
    st.metric("Current Cash Balance", f"${st.session_state.current_cash_balance:,.2f}")
with col2:
    st.metric("Total Outstanding Payables", f"${total_outstanding:,.2f}")

st.divider()

# 2. Cash Timeline Chart
st.subheader("Cash Timeline Projection")

# Project cashflow based on the backend function or our mock
projection_list = project_cashflow(
    st.session_state.current_simulated_date, 
    st.session_state.current_cash_balance
)

if projection_list and isinstance(projection_list, list):
    # Convert list of dicts to dataframe for st.line_chart
    df_projection = pd.DataFrame(projection_list)
    if "date" in df_projection.columns and "cash_projection" in df_projection.columns:
        df_projection.set_index("date", inplace=True)
        st.line_chart(df_projection["cash_projection"], y_label="Cash (Currency)", x_label="Time (Days)")
    else:
        st.line_chart(df_projection)
else:
    st.write("No projection data available.")

st.divider()

# Compute decisions for active invoices
decisions = []
for inv in st.session_state.active_invoices:
    dec = choose_best_action(inv, st.session_state.current_simulated_date, st.session_state.current_cash_balance)
    decisions.append(dec)

# 3. Invoice Decision Table
st.subheader("Invoice Decision Table")
table_data = []
for inv, dec in zip(st.session_state.active_invoices, decisions):
    table_data.append({
        "Invoice ID": inv["id"],
        "Supplier": inv["supplier"],
        "Amount": f"${inv['amount']:,.2f}",
        "Due Date": inv["due_date"],
        "Recommended Action": dec["action"].replace("_", " ").title()
    })

st.dataframe(pd.DataFrame(table_data), use_container_width=True)

# 4. Explainability Panel
st.subheader("Explainability Panel")
for inv, dec in zip(st.session_state.active_invoices, decisions):
    with st.expander(f"View Rationale for {inv['id']} - {inv['supplier']}"):
        # Display the plain-English explanation generated by the explain_decision function
        explanation = explain_decision(inv, dec["action"], dec["scores"])
        st.write(explanation)
        
        st.write("**Detailed Scores:**")
        scores_df = pd.DataFrame([dec["scores"]])
        st.dataframe(scores_df, hide_index=True)

st.divider()

# ---------------------------------------------------------
# Simulation Loop & Event Handling
# ---------------------------------------------------------
if st.button("Simulate Next Day", type="primary", use_container_width=True):
    # Capture previous state
    previous_state = {
        "date": st.session_state.current_simulated_date,
        "cash_balance": st.session_state.current_cash_balance,
        "invoices": list(st.session_state.active_invoices),
        "receivables": []
    }
    
    # 1. Advance current_simulated_date by one day
    st.session_state.current_simulated_date += datetime.timedelta(days=1)
    
    # Apply some mock dynamic financial shifts
    st.session_state.current_cash_balance += random.uniform(-15000, 20000)
    
    # Remove older invoices (simulating payment) and add new ones (simulating new obligations)
    if random.random() > 0.4 and st.session_state.active_invoices:
        st.session_state.active_invoices.pop(0)
    if random.random() > 0.6:
        new_invs = generate_mock_invoices(st.session_state.current_simulated_date)
        st.session_state.active_invoices.append(new_invs[0])
        
    # Capture current state
    current_state = {
        "date": st.session_state.current_simulated_date,
        "cash_balance": st.session_state.current_cash_balance,
        "invoices": list(st.session_state.active_invoices),
        "receivables": []
    }
    
    # 2. Trigger detect_change() and reoptimize()
    changes = detect_change(previous_state, current_state)
    updated_forecast, updated_decisions = reoptimize(current_state, project_cashflow, choose_best_action)
    
    # 3. Refresh dashboard screen
    st.rerun()
