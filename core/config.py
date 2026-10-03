"""
Dhaga & Co. COD Shield - System Configuration & Business Arithmetic Constants
"""

import os

# --- Business & Scale Constants (Directly from Case Study) ---
WEEKLY_TOTAL_ORDERS = 48000
COD_ORDER_SHARE = 0.61  # 61% of orders are Cash-on-Delivery
WEEKLY_COD_ORDERS = int(WEEKLY_TOTAL_ORDERS * COD_ORDER_SHARE)  # 29,280 orders/week
BASELINE_COD_RTO_RATE = 0.26  # 26% RTO rate on COD
WEEKLY_BASELINE_RTO_ORDERS = int(WEEKLY_COD_ORDERS * BASELINE_COD_RTO_RATE)  # ~7,613 orders/week
LOGISTICS_COST_PER_RTO_INR = 120.0  # ₹120 direct courier reverse pickup & burn
WEEKLY_LOGISTICS_BLEED_INR = WEEKLY_BASELINE_RTO_ORDERS * LOGISTICS_COST_PER_RTO_INR  # ₹9,13,560 / week
ANNUAL_LOGISTICS_BLEED_INR = WEEKLY_LOGISTICS_BLEED_INR * 52  # ₹4.75 Crore / year
AVERAGE_ORDER_VALUE_INR = 840.0  # ₹840 average order value

# Target RTO Impact
TARGET_RTO_REDUCTION_POINTS = 0.05  # 5% absolute reduction (26% -> 21%)
PROJECTED_WEEKLY_SAVED_ORDERS = int(WEEKLY_COD_ORDERS * TARGET_RTO_REDUCTION_POINTS)  # ~1,464 orders
PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR = PROJECTED_WEEKLY_SAVED_ORDERS * LOGISTICS_COST_PER_RTO_INR  # ₹1,75,680 / week

# Two models chosen with deliberate split on latency, cost, and judgment:
FAST_WORKER_MODEL = "gemini-flash-lite-latest"  # Ultra-low latency, rock-solid 200 OK, zero 503 spikes
JUDGMENT_EVAL_MODEL = "gemini-3.6-flash"         # High-reasoning model for ambiguous edge cases & WhatsApp synthesis



# Alternative models for OpenAI fallback
OPENAI_FAST_MODEL = "gpt-4o-mini"
OPENAI_JUDGMENT_MODEL = "gpt-4o"

# Stated Temperatures (Rule: Stated temperatures)
EXTRACTION_TEMPERATURE = 0.1   # Maximum determinism and schema fidelity
EVALUATION_TEMPERATURE = 0.3   # Calibrated judgment + natural Hindi/Hinglish language synthesis

# USD to INR Exchange Rate
USD_TO_INR = 84.0

# Inference Cost Calculations (per 1,000,000 tokens)
# Gemini 1.5 Flash: $0.075 / 1M input, $0.30 / 1M output
GEMINI_FLASH_INPUT_COST_PER_1M = 0.075
GEMINI_FLASH_OUTPUT_COST_PER_1M = 0.30

# Gemini 1.5 Pro: $1.25 / 1M input, $5.00 / 1M output
GEMINI_PRO_INPUT_COST_PER_1M = 1.25
GEMINI_PRO_OUTPUT_COST_PER_1M = 5.00

# Estimated Token Usage per Order
AVG_PARSE_INPUT_TOKENS = 350
AVG_PARSE_OUTPUT_TOKENS = 120
AVG_EVAL_INPUT_TOKENS = 500
AVG_EVAL_OUTPUT_TOKENS = 200

def get_single_order_cost_inr(evaluated_by_pro: bool = False) -> float:
    """Calculate the exact cost of 1 order run in INR."""
    # Fast model cost
    flash_cost_usd = (
        (AVG_PARSE_INPUT_TOKENS / 1_000_000) * GEMINI_FLASH_INPUT_COST_PER_1M +
        (AVG_PARSE_OUTPUT_TOKENS / 1_000_000) * GEMINI_FLASH_OUTPUT_COST_PER_1M
    )
    total_cost_usd = flash_cost_usd
    if evaluated_by_pro:
        pro_cost_usd = (
            (AVG_EVAL_INPUT_TOKENS / 1_000_000) * GEMINI_PRO_INPUT_COST_PER_1M +
            (AVG_EVAL_OUTPUT_TOKENS / 1_000_000) * GEMINI_PRO_OUTPUT_COST_PER_1M
        )
        total_cost_usd += pro_cost_usd
    return round(total_cost_usd * USD_TO_INR, 4)

def get_weekly_projected_ai_cost_inr(flagged_rate: float = 0.30) -> dict:
    """Calculate the total AI infrastructure bill at Dhaga's weekly scale (29,280 COD orders)."""
    # 100% of COD orders run through Fast Model
    all_flash_runs = WEEKLY_COD_ORDERS
    flash_unit_cost = (
        (AVG_PARSE_INPUT_TOKENS / 1_000_000) * GEMINI_FLASH_INPUT_COST_PER_1M +
        (AVG_PARSE_OUTPUT_TOKENS / 1_000_000) * GEMINI_FLASH_OUTPUT_COST_PER_1M
    ) * USD_TO_INR
    flash_total_inr = all_flash_runs * flash_unit_cost

    # Only flagged medium/high risk orders (approx 30%) route to Judgment/Pro model
    pro_runs = int(WEEKLY_COD_ORDERS * flagged_rate)
    pro_unit_cost = (
        (AVG_EVAL_INPUT_TOKENS / 1_000_000) * GEMINI_PRO_INPUT_COST_PER_1M +
        (AVG_EVAL_OUTPUT_TOKENS / 1_000_000) * GEMINI_PRO_OUTPUT_COST_PER_1M
    ) * USD_TO_INR
    pro_total_inr = pro_runs * pro_unit_cost

    total_ai_inr = flash_total_inr + pro_total_inr
    net_weekly_savings = PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR - total_ai_inr
    roi_multiple = (
        PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR / total_ai_inr if total_ai_inr > 0 else 0
    )

    return {
        "weekly_cod_orders": WEEKLY_COD_ORDERS,
        "flash_cost_inr": round(flash_total_inr, 2),
        "pro_cost_inr": round(pro_total_inr, 2),
        "total_ai_cost_inr": round(total_ai_inr, 2),
        "logistics_saved_inr": round(PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR, 2),
        "net_weekly_profit_inr": round(net_weekly_savings, 2),
        "roi_multiple": round(roi_multiple, 1),
    }
