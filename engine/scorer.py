"""Scoring module for evaluating working capital actions."""

from engine import actions

def score_action(invoice, action, forecast, weights=None):
    """
    Calculates sub-scores between 0.0 and 1.0 for a given action and invoice,
    returning a weighted total score and the breakdown.
    """
    if weights is None:
        weights = {
            'liquidity': 0.30,
            'financing_cost': 0.25,
            'discount_value': 0.20,
            'supplier_priority': 0.15,
            'risk': 0.10
        }

    # Baseline scores (0.5 represents neutral impact)
    sub_scores = {
        'liquidity': 0.5,
        'financing_cost': 0.5,
        'discount_value': 0.5,
        'supplier_priority': 0.5,
        'risk': 0.5
    }

    # Simulate algorithmic adjustments based on action type
    discount_pct = invoice.get("discount_pct", 0.0)
    
    if action == actions.TAKE_DISCOUNT:
        sub_scores['discount_value'] = 0.95 if discount_pct > 0 else 0.10
        sub_scores['liquidity'] = 0.40
    elif action == actions.PAY_AT_MATURITY:
        sub_scores['liquidity'] = 0.85
        sub_scores['financing_cost'] = 1.00
    elif action == actions.SUPPLIER_FINANCING:
        sub_scores['liquidity'] = 0.90
        sub_scores['financing_cost'] = 0.60
    
    # Adjust priority score based on invoice data
    priority = invoice.get("supplier_priority", "low")
    if priority == "critical":
        sub_scores['supplier_priority'] = 0.90
    elif priority == "high":
        sub_scores['supplier_priority'] = 0.75

    total_score = sum(sub_scores[metric] * weights[metric] for metric in weights)

    return {
        'total_score': total_score,
        'sub_scores': sub_scores
    }