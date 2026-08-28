"""Optimal action selection logic for the Decision Engine."""

from engine.actions import ALL_ACTIONS
from engine.scorer import score_action

def choose_best_action(invoice, forecast, weights=None):
    """
    Loops through all allowable actions, scores them, and returns the optimal choice.
    """
    best_action = None
    best_score = -1.0
    best_sub_scores = {}

    for action in ALL_ACTIONS:
        evaluation = score_action(invoice, action, forecast, weights)
        
        if evaluation['total_score'] > best_score:
            best_score = evaluation['total_score']
            best_action = action
            best_sub_scores = evaluation['sub_scores']

    return {
        "invoice_id": invoice.get("invoice_id", "Unknown"),
        "recommended_action": best_action,
        "total_score": best_score,
        "sub_scores": best_sub_scores,
    }


if __name__ == "__main__":
    # --- Sample Test Invoices & Forecast ---
    sample_forecast = {
        "available_cash": 45000.0,
        "bank_interest_rate": 0.08,
    }

    sample_invoices = [
        {
            "invoice_id": "INV-1001",
            "amount": 12000.0,
            "discount_pct": 0.025,
            "supplier_priority": "high",
            "due_date": "2026-09-15",
        },
        {
            "invoice_id": "INV-1002",
            "amount": 60000.0,
            "discount_pct": 0.0,
            "supplier_priority": "critical",
            "supplier_financing_rate": 0.025,
            "due_date": "2026-09-05",
        },
        {
            "invoice_id": "INV-1003",
            "amount": 5000.0,
            "discount_pct": 0.0,
            "supplier_priority": "low",
            "due_date": "2026-09-30",
        },
    ]

    print("=" * 70)
    print("Decision Engine - Optimal Action Selection Test")
    print(f"Forecast Available Cash: ${sample_forecast['available_cash']:,.2f}")
    print("=" * 70)

    for inv in sample_invoices:
        decision = choose_best_action(inv, sample_forecast)
        print(f"\nInvoice: {decision['invoice_id']}")
        print(f"  Amount: ${inv['amount']:,.2f} | Discount: {inv['discount_pct'] * 100}% | Priority: {inv['supplier_priority']}")
        print(f"  Recommended Action: {decision['recommended_action']}")
        print(f"  Total Score:        {decision['total_score']:.4f}")
        print("  Sub-Scores Breakdown:")
        for metric, val in decision["sub_scores"].items():
            print(f"    - {metric:18s}: {val:.4f}")

    print("\n" + "=" * 70)