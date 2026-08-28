"""
Shared Data Contracts for the Working Capital Agent team.

These shapes represent the expected dictionaries passing between modules. 
We are using plain dictionaries rather than rigid classes to keep iteration fast 
and simple for the hackathon.

NOTE: Do not modify these keys without checking with the rest of the team first, 
as it will break downstream consumers (Decision Engine & Explainability).
"""

# ==========================================
# 1. INVOICE (Money we owe a supplier)
# ==========================================
# Frozen team contract.
INVOICE_SCHEMA_EXAMPLE = {
    "id": "INV001",
    "supplier": "Acme Co",
    "amount": 50000,
    "due_date": "2026-09-05",
    "discount_pct": 0.02,
    "discount_deadline": "2026-08-30",
    "penalty_pct": 0.015
}

# ==========================================
# 2. RECEIVABLE (Money we expect to receive)
# ==========================================
# Provisional shape proposed by Data (Person A).
# (Flag: We may want to revisit this with the team if we need a 'customer_name' field).
RECEIVABLE_SCHEMA_EXAMPLE = {
    "id": "REC001",
    "amount": 30000,
    "expected_date": "2026-09-02",
    "delay_probability": 0.3
}

# ==========================================
# 3. DECISION (The action chosen per invoice)
# ==========================================
# Included here for reference so we know what is consuming our data.
# Person B (Decision Engine) and Person C (Explainability) will formalize this shape.
DECISION_SCHEMA_EXAMPLE = {
    "invoice_id": "INV001",
    "action": "take_discount",
    "scores": {
        "liquidity": 0.7, 
        "cost": 0.4, 
        "discount": 0.9, 
        "supplier": 0.6, 
        "risk": 0.3
    },
    "rationale": None
}
