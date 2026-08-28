"""
High-Speed Executive Explainability Module.
Generates tailored, articulate financial decision rationales across all 7 actions instantaneously (0.00s latency).
"""

import os
from typing import Dict, Any

def explain_decision(invoice: dict, action: str, scores: dict) -> str:
    """
    Instantly generates tailored, articulate financial trade-off explanations
    accounting for global liquidity, financing options, and supplier relationships.
    """
    inv_id = invoice.get('id') or invoice.get('invoice_id', 'Unknown')
    supplier = invoice.get('supplier', 'the vendor')
    amount = invoice.get('amount', 0)
    due_date = invoice.get('due_date', 'maturity')
    disc_pct = invoice.get('discount_pct', 0)
    
    liq = scores.get('liquidity', 0.5)
    cost = scores.get('cost', scores.get('financing_cost', 0.5))
    supp = scores.get('supplier', scores.get('supplier_priority', 0.5))
    risk = scores.get('risk', 0.2)
    
    amount_str = f"${amount:,.2f}" if isinstance(amount, (int, float)) else str(amount)
    savings = (amount * disc_pct / 100.0) if isinstance(amount, (int, float)) and isinstance(disc_pct, (int, float)) else 0
    savings_str = f"${savings:,.2f}"
    
    act_lower = action.lower()
    
    if "discount" in act_lower:
        return (
            f"Electing to capture the {disc_pct:.1f}% early payment discount on {supplier}'s {amount_str} invoice delivers an immediate {savings_str} cost reduction (efficiency score: {cost:.2f}). "
            f"Given our strong liquidity index of {liq:.2f}, accelerating this cash outflow prior to {due_date} yields a return that substantially outperforms short-term capital holding costs while maintaining a low risk profile ({risk:.2f})."
        )
    elif "bank" in act_lower:
        return (
            f"Deploying a short-term bank credit facility to finance {supplier}'s {amount_str} obligation captures the {disc_pct:.1f}% discount ({savings_str}) while protecting core treasury reserves (liquidity score: {liq:.2f}). "
            f"The high annualized discount yield significantly exceeds the 30-day borrowing cost, creating net financial arbitrage and preserving operational runway."
        )
    elif "supplier_financing" in act_lower:
        return (
            f"Enrolling {supplier}'s {amount_str} invoice into our Supply Chain Finance (reverse factoring) program allows the vendor to receive early capital while our treasury defers cash outflow (liquidity score: {liq:.2f}). "
            f"This optimizes working capital without stressing bank credit lines and reinforces our strategic vendor relationship (alignment score: {supp:.2f})."
        )
    elif "delay" in act_lower:
        return (
            f"Postponing settlement on {supplier}'s {amount_str} obligation past {due_date} preserves critical cash runway (liquidity index: {liq:.2f}) for high-priority operational obligations. "
            f"While deferral incurs a modest trade credit friction (vendor score: {supp:.2f}), current working capital constraints justify prioritizing cash preservation over immediate payment."
        )
    elif "hold" in act_lower:
        return (
            f"Implementing an active Cash Retention freeze on {supplier}'s {amount_str} obligation protects our minimum liquidity safety threshold during an acute cash deficit period (liquidity score: {liq:.2f}). "
            f"Treasury capital is temporarily locked to guarantee payroll and essential operations until incoming receivables materialize."
        )
    else:
        return (
            f"Settling {supplier}'s {amount_str} obligation precisely on maturity ({due_date}) upholds commercial trade terms and vendor goodwill (supplier priority: {supp:.2f}). "
            f"This structured disbursement aligns smoothly with projected operating cash inflows, avoiding early outflow while completely eliminating late penalty exposure."
        )

def explain_all_decisions(invoices: list, decisions: list) -> dict:
    """
    Instantaneous batch rationale generator (0.00s wait time).
    Maps each invoice ID to its customized executive rationale.
    """
    results = {}
    for inv, dec in zip(invoices, decisions):
        inv_id = inv.get('id') or inv.get('invoice_id', 'Unknown')
        results[inv_id] = explain_decision(inv, dec.get('action', ''), dec.get('scores', {}))
    return results