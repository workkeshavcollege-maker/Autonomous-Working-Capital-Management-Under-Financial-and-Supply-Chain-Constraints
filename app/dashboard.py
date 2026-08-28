import streamlit as st
import pandas as pd
import datetime
from typing import List, Dict, Any
import random
import sys
import os

# Ensure the root directory is in the Python path so Streamlit can find data, engine, and explain folders
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set page config with a refined executive title
st.set_page_config(
    page_title="Working Capital Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Bespoke Professional Earth-Tone CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1C1917;
    }

    .main {
        background-color: #F7F5F0;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1320px;
    }

    /* Professional Section Headers */
    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #44403C;
        margin-bottom: 8px;
    }

    /* Metric Cards - Warm Linen Theme */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #EAE5D9;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 1px 4px rgba(44, 36, 30, 0.03);
        transition: all 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: #D9D2C3;
        box-shadow: 0 4px 10px rgba(44, 36, 30, 0.05);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.76rem !important;
        color: #78716C !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        line-height: 1.2 !important;
    }

    [data-testid="stMetricLabel"] * {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.45rem;
        color: #1C1917;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Content Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border: 1px solid #EAE5D9;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(44, 36, 30, 0.02);
        margin-bottom: 1.25rem;
    }

    /* Expander - Clean Professional Style */
    [data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid #EAE5D9;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(44, 36, 30, 0.02);
        margin-bottom: 0.65rem;
        transition: border-color 0.2s ease;
    }

    [data-testid="stExpander"]:hover {
        border-color: #C25E3E;
    }

    /* Primary Action Button */
    .stButton > button {
        background-color: #C25E3E !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.7rem 1.4rem !important;
        box-shadow: 0 2px 8px rgba(194, 94, 62, 0.2) !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #A84E32 !important;
        box-shadow: 0 4px 12px rgba(194, 94, 62, 0.3) !important;
    }

    /* Info Alert Styling */
    [data-testid="stAlert"] {
        background-color: #FAF8F5;
        border: 1px solid #EAE5D9;
        border-left: 3px solid #C25E3E;
        border-radius: 6px;
        color: #292524;
    }

    [data-testid="stAlert"] p {
        color: #292524 !important;
        font-size: 0.9rem !important;
        line-height: 1.45 !important;
    }
</style>
""", unsafe_allow_html=True)

# Required Integrations & Imports
try:
    from data.forecast import project_cashflow
    from engine.decide import choose_best_action
    from explain.rationale import explain_decision, explain_all_decisions
    from explain.monitor import detect_change, reoptimize
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    st.error(f"DEBUG - ImportError: {e}")
    
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
# Professional Header (Restrained & High-Signal)
# ---------------------------------------------------------
formatted_date = st.session_state.current_simulated_date.strftime('%B %d, %Y')

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 20px; border-bottom: 1.5px solid #E6E0D2; margin-bottom: 24px;">
    <div>
        <h1 style="font-family: 'Newsreader', Georgia, serif; font-size: 2.35rem; font-weight: 500; font-style: italic; color: #1C1917; margin: 0; line-height: 1.1;">
            Working Capital <span style="font-style: normal; font-weight: 600; color: #C25E3E;">Agent</span>
        </h1>
    </div>
    <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
        <div style="display: inline-flex; align-items: center; gap: 6px; background: #EFECE6; padding: 4px 12px; border-radius: 9999px; border: 1px solid #DFD9CD;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: #4A6B5D; display: inline-block;"></span>
            <span style="font-size: 0.75rem; font-weight: 600; color: #44403C; letter-spacing: 0.02em;">System Active</span>
        </div>
        <span style="font-size: 0.82rem; color: #78716C;">Current Date: <strong style="color: #292524;">{formatted_date}</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

if not BACKEND_AVAILABLE:
    st.info("Backend modules not found. Running in simulation mode with robust fallback data.")

# ---------------------------------------------------------
# KPI Row
# ---------------------------------------------------------
total_outstanding = sum(inv["amount"] for inv in st.session_state.active_invoices)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Treasury Cash Balance", 
        value=f"${st.session_state.current_cash_balance:,.2f}",
        delta="Available Liquidity"
    )
with col2:
    st.metric(
        label="Outstanding Payables", 
        value=f"${total_outstanding:,.2f}",
        delta=f"{len(st.session_state.active_invoices)} Invoices Due",
        delta_color="off"
    )
with col3:
    st.metric(
        label="Operational Date", 
        value=st.session_state.current_simulated_date.strftime('%b %d, %Y'),
        delta="Daily Cycle"
    )

st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Two-Column Split-Screen Master Layout
# ---------------------------------------------------------
left_col, right_col = st.columns([1, 1.25], gap="large")

# Compute decisions for active invoices
decisions = []
for inv in st.session_state.active_invoices:
    dec = choose_best_action(inv, st.session_state.current_simulated_date, st.session_state.current_cash_balance)
    decisions.append(dec)

# Count decision breakdown for summary badges
discount_count = sum(1 for d in decisions if "discount" in d["action"].lower())
delay_count = sum(1 for d in decisions if "delay" in d["action"].lower())
maturity_count = len(decisions) - discount_count - delay_count

with left_col:
    # 1. Cashflow Projection Card
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
        <span class="section-header">Cashflow Projection</span>
        <span style="font-size: 0.75rem; font-weight: 600; color: #8C827A; background: #EFECE6; padding: 2px 8px; border-radius: 4px;">30-Day Window</span>
    </div>
    """, unsafe_allow_html=True)
    
    projection_list = project_cashflow(
        st.session_state.current_simulated_date, 
        st.session_state.current_cash_balance
    )

    with st.container(border=True):
        if projection_list and isinstance(projection_list, list):
            df_projection = pd.DataFrame(projection_list)
            if "date" in df_projection.columns and "cash_projection" in df_projection.columns:
                df_projection.set_index("date", inplace=True)
                st.line_chart(
                    df_projection["cash_projection"], 
                    y_label="Cash Balance ($)", 
                    x_label="Date"
                )
            else:
                st.line_chart(df_projection)
        else:
            st.write("No projection data available.")

    # 2. Simulation Console Card
    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 8px;">
        <span class="section-header">Simulation Controls</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("""
        <p style="font-size: 0.88rem; color: #57534E; margin-bottom: 14px; line-height: 1.5;">
            Step to the next operational day to process payment settlements, evaluate incoming vendor liabilities, and re-optimize treasury decisions in real time.
        </p>
        """, unsafe_allow_html=True)
        
        if st.button("Advance Simulation Cycle", type="primary", use_container_width=True):
            # Capture previous state
            previous_state = {
                "date": st.session_state.current_simulated_date,
                "cash_balance": st.session_state.current_cash_balance,
                "invoices": list(st.session_state.active_invoices),
                "receivables": []
            }
            
            # 1. Advance current_simulated_date by one day
            st.session_state.current_simulated_date += datetime.timedelta(days=1)
            
            # Apply dynamic financial shifts
            st.session_state.current_cash_balance += random.uniform(-15000, 20000)
            
            # Remove older invoices (simulating payment) and add new ones
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

with right_col:
    # 3. Payables Decision Ledger
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
        <span class="section-header">Payables Ledger</span>
        <div style="display: flex; gap: 6px;">
            <span style="background: #EDF3F0; color: #264739; font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; border: 1px solid #C8DCD3;">{discount_count} Discounts</span>
            <span style="background: #FEF3C7; color: #92400E; font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; border: 1px solid #FDE68A;">{delay_count} Delayed</span>
            <span style="background: #FDF2EE; color: #9C3E20; font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; border: 1px solid #F8D7CC;">{maturity_count} Standard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    table_data = []
    for inv, dec in zip(st.session_state.active_invoices, decisions):
        table_data.append({
            "Invoice ID": inv["id"],
            "Supplier": inv["supplier"],
            "Amount": f"${inv['amount']:,.2f}",
            "Due Date": inv["due_date"],
            "Recommended Action": dec["action"].replace("_", " ").title()
        })

    df_table = pd.DataFrame(table_data)

    # Earth-tone Styler mapping
    def highlight_actions(val):
        val_str = str(val).lower()
        if "discount" in val_str:
            return "background-color: #EDF3F0; color: #264739; font-weight: 700;"
        elif "delay" in val_str:
            return "background-color: #FEF3C7; color: #92400E; font-weight: 700;"
        else:
            return "background-color: #FDF2EE; color: #9C3E20; font-weight: 700;"

    styled_df = df_table.style
    if hasattr(styled_df, "map"):
        styled_df = styled_df.map(highlight_actions, subset=["Recommended Action"])
    else:
        styled_df = styled_df.applymap(highlight_actions, subset=["Recommended Action"])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Decision Rationale & Scorecards (High-Speed Batch AI Generation)
    @st.cache_data(show_spinner=False)
    def get_all_explanations_cached(invoices_list: list, decisions_list: list) -> dict:
        try:
            return explain_all_decisions(invoices_list, decisions_list)
        except Exception:
            return {}

    all_explanations = get_all_explanations_cached(st.session_state.active_invoices, decisions)

    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
        <span class="section-header">Decision Rationale & Scorecards</span>
    </div>
    """, unsafe_allow_html=True)

    for inv, dec in zip(st.session_state.active_invoices, decisions):
        action_title = dec["action"].replace("_", " ").title()
        with st.expander(f"{inv['id']} — {inv['supplier']} | Recommendation: {action_title}"):
            explanation = all_explanations.get(inv["id"])
            if not explanation:
                # High-fidelity custom contextual analysis if API is offline
                supplier = inv["supplier"]
                amount = inv["amount"]
                due_date = inv["due_date"]
                discount_pct = inv.get("discount_pct", 0.0)
                liq = dec["scores"].get('liquidity', 0.5)
                cost = dec["scores"].get('cost', 0.5)
                supp = dec["scores"].get('supplier', 0.5)
                
                if "discount" in dec["action"].lower():
                    explanation = (f"Electing to capture the {discount_pct:.1f}% early payment discount on {supplier}'s ${amount:,.2f} invoice delivers an immediate, risk-free cost reduction (optimization score: {cost:.2f}). "
                                   f"While this accelerates a cash outflow prior to {due_date}, the company's current liquidity index of {liq:.2f} comfortably absorbs the payment without stressing working capital.")
                elif "delay" in dec["action"].lower():
                    explanation = (f"Postponing settlement on {supplier}'s ${amount:,.2f} obligation preserves crucial short-term liquidity (score: {liq:.2f}) to maintain buffer for higher-priority operations. "
                                   f"Although delaying past {due_date} introduces a supplier impact trade-off (alignment: {supp:.2f}), the immediate cash retention outweighs the late financing friction.")
                else:
                    explanation = (f"Settling {supplier}'s ${amount:,.2f} invoice on its maturity date ({due_date}) preserves full trade credit terms and vendor goodwill (supplier score: {supp:.2f}). "
                                   f"This neutral timing aligns smoothly with scheduled cash inflows, avoiding early outflow while eliminating late penalty exposure.")

            st.info(explanation)
            
            # Sub-scores breakdown using native cards with truncation-prevention CSS
            scores = dec.get("scores", {})
            if scores:
                score_cols = st.columns(len(scores))
                for col, (score_name, score_val) in zip(score_cols, scores.items()):
                    with col:
                        col.metric(
                            label=score_name.replace("_", " ").title(), 
                            value=f"{score_val:.2f}" if isinstance(score_val, float) else f"{score_val}"
                        )
