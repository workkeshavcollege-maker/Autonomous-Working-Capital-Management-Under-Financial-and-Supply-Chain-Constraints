"""
Realistic mock data for a small business's cash position, invoices, and receivables.
Used for forecasting and working capital decisions.
"""

# Starting cash balance for the business
STARTING_CASH_BALANCE = 125450.00

# 8 supplier invoices representing upcoming obligations
# Mix of near-due, far-due, and various discount terms
INVOICES = [
    {
        "id": "INV001",
        "supplier": "Acme Co",
        "amount": 50000.00,
        "due_date": "2026-09-05",
        "discount_pct": 0.02,
        "discount_deadline": "2026-08-30",
        "penalty_pct": 0.015
    },
    {
        "id": "INV002",
        "supplier": "Globex Corp",
        "amount": 15400.00,
        "due_date": "2026-09-01",
        "discount_pct": 0.01,
        "discount_deadline": "2026-08-29",
        "penalty_pct": 0.02
    },
    {
        "id": "INV003",
        "supplier": "Initech",
        "amount": 8200.00,
        "due_date": "2026-09-15",
        "discount_pct": 0.0,
        "discount_deadline": None,
        "penalty_pct": 0.01
    },
    {
        "id": "INV004",
        "supplier": "Umbrella Corp",
        "amount": 22000.00,
        "due_date": "2026-09-10",
        "discount_pct": 0.015,
        "discount_deadline": "2026-09-02",
        "penalty_pct": 0.025
    },
    {
        "id": "INV005",
        "supplier": "Massive Dynamic",
        "amount": 12500.00,
        "due_date": "2026-09-08",
        "discount_pct": 0.0,
        "discount_deadline": None,
        "penalty_pct": 0.015
    },
    {
        "id": "INV006",
        "supplier": "Soylent Corp",
        "amount": 35000.00,
        "due_date": "2026-09-20",
        "discount_pct": 0.03,
        "discount_deadline": "2026-09-10",
        "penalty_pct": 0.02
    },
    {
        "id": "INV007",
        "supplier": "Cyberdyne",
        "amount": 5500.00,
        "due_date": "2026-08-30",
        "discount_pct": 0.0,
        "discount_deadline": None,
        "penalty_pct": 0.05
    },
    {
        "id": "INV008",
        "supplier": "Weyland-Yutani",
        "amount": 42000.00,
        "due_date": "2026-09-25",
        "discount_pct": 0.02,
        "discount_deadline": "2026-09-15",
        "penalty_pct": 0.01
    }
]

# 5 receivables representing expected incoming cash
# Mix of near-certain and risky expected payments
RECEIVABLES = [
    {
        "id": "REC001",
        "amount": 30000.00,
        "expected_date": "2026-09-02",
        "delay_probability": 0.3
    },
    {
        "id": "REC002",
        "amount": 18500.00,
        "expected_date": "2026-08-31",
        "delay_probability": 0.1  # Very likely to be on time
    },
    {
        "id": "REC003",
        "amount": 45000.00,
        "expected_date": "2026-09-12",
        "delay_probability": 0.5  # Risky, 50/50 chance of delay
    },
    {
        "id": "REC004",
        "amount": 25000.00,
        "expected_date": "2026-09-05",
        "delay_probability": 0.2
    },
    {
        "id": "REC005",
        "amount": 12000.00,
        "expected_date": "2026-09-18",
        "delay_probability": 0.05 # Highly certain
    }
]

if __name__ == "__main__":
    print("=== SMALL BUSINESS MOCK DATA ===")
    print(f"Starting Cash Balance: ${STARTING_CASH_BALANCE:,.2f}")
    print(f"\nInvoices ({len(INVOICES)} total):")
    for inv in INVOICES:
        print(f"  - {inv['id']}: ${inv['amount']:,.2f} to {inv['supplier']} (Due: {inv['due_date']})")
    
    print(f"\nReceivables ({len(RECEIVABLES)} total):")
    for rec in RECEIVABLES:
        print(f"  - {rec['id']}: ${rec['amount']:,.2f} expected on {rec['expected_date']} (Delay Risk: {rec['delay_probability']:.0%})")
