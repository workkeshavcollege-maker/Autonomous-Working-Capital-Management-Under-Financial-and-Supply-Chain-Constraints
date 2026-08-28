"""Allowable actions for the Decision Engine (CSI ORIGIN 2026 - Problem Statement 4)."""

PAY_NOW = 'pay_now'
PAY_AT_MATURITY = 'pay_at_maturity'
DELAY_PAYMENT = 'delay_payment'
TAKE_DISCOUNT = 'take_discount'
BANK_FINANCING = 'bank_financing'
SUPPLIER_FINANCING = 'supplier_financing'
HOLD_CASH = 'hold_cash'

ALL_ACTIONS = [
    PAY_NOW,
    PAY_AT_MATURITY,
    DELAY_PAYMENT,
    TAKE_DISCOUNT,
    BANK_FINANCING,
    SUPPLIER_FINANCING,
    HOLD_CASH
]