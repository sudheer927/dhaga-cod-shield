"""
Dhaga & Co. COD Shield
Pre-Dispatch Address Intelligence & RTO Interception Engine
Cohort 4 Mini Project 1 - Group 10
"""

import streamlit as st
import pandas as pd
import time
import os

from core.config import (
    WEEKLY_TOTAL_ORDERS,
    WEEKLY_COD_ORDERS,
    BASELINE_COD_RTO_RATE,
    LOGISTICS_COST_PER_RTO_INR,
    WEEKLY_LOGISTICS_BLEED_INR,
    PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR,
    FAST_WORKER_MODEL,
    JUDGMENT_EVAL_MODEL,
    EXTRACTION_TEMPERATURE,
    EVALUATION_TEMPERATURE,
    get_weekly_projected_ai_cost_inr,
)
from core.test_cases import REAL_SHAPED_TEST_CASES
from core.pipeline import process_dhaga_order

# Page configuration
st.set_page_config(
    page_title="Dhaga & Co. | COD Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished, professional typography & card aesthetics
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 12px;
    }
    .metric-title { font-size: 0.85rem; color: #6c757d; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #212529; }
    .status-badge-approved {
        background-color: #d4edda; color: #155724; padding: 6px 12px; border-radius: 4px; font-weight: 700; display: inline-block;
    }
    .status-badge-hold {
        background-color: #fff3cd; color: #856404; padding: 6px 12px; border-radius: 4px; font-weight: 700; display: inline-block;
    }
    .status-badge-reject {
        background-color: #f8d7da; color: #721c24; padding: 6px 12px; border-radius: 4px; font-weight: 700; display: inline-block;
    }
    .whatsapp-preview {
        background-color: #e5ddd5;
        border-radius: 12px;
        padding: 16px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #111;
        max-width: 520px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 10px;
    }
    .whatsapp-bubble {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.95rem;
        line-height: 1.45;
        position: relative;
    }
    .whatsapp-button {
        display: block;
        background-color: #ffffff;
        color: #00a884;
        text-align: center;
        padding: 8px;
        margin-top: 6px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #dcdcdc;
    }
</style>
""", unsafe_allow_html=True)


# --- Sidebar: Configuration & Telemetry ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=54)
    st.title("Dhaga & Co.")
    st.caption("**COD Shield Control Tower**")
    st.markdown("---")

    st.subheader("⚙️ Engine Settings")
    provider_choice = st.selectbox(
        "LLM Provider",
        ["Google Gemini (Recommended)", "OpenAI", "Offline Demo Mode (Zero Token Cost)"],
        index=0
    )

    api_key_input = ""
    if "Gemini" in provider_choice:
        provider = "gemini"
        default_key = os.getenv("GEMINI_API_KEY", "")
        api_key_input = st.text_input("Gemini API Key", value=default_key, type="password", help="Leave blank to use pre-cached evaluation engine")
    elif "OpenAI" in provider_choice:
        provider = "openai"
        default_key = os.getenv("OPENAI_API_KEY", "")
        api_key_input = st.text_input("OpenAI API Key", value=default_key, type="password")
    else:
        provider = "mock"
        api_key_input = ""

    st.markdown("---")
    st.markdown("### 👥 Group 10 (Cohort 4)")
    st.markdown("""
    - **Venkata Sairam Sudheer**
    - **Omita Thakur**
    - **Sheikh Habib**
    - **Rohit Yadav**
    """)
    st.caption("Reviewer: Ruthvik | Sun 4 Oct 5:45 PM")


# --- Top Dashboard Metrics ---
st.title("🛡️ Dhaga & Co. — COD RTO Shield")
st.markdown(
    "**Pre-dispatch address intelligence & RTO interception engine** preventing unlocatable "
    "deliveries across Tier-2/3 India before couriers burn ₹120 in dead logistics."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Weekly Volume", f"{WEEKLY_TOTAL_ORDERS:,} orders", f"{WEEKLY_COD_ORDERS:,} COD (61%)")
with col2:
    st.metric("COD RTO Rate", f"{BASELINE_COD_RTO_RATE*100:.0f}%", "7,613 parcels/wk returned", delta_color="inverse")
with col3:
    st.metric("Weekly Cash Bleed", f"₹{WEEKLY_LOGISTICS_BLEED_INR/100000:.2f} Lakhs", "Dead freight @ ₹120/RTO", delta_color="inverse")
with col4:
    st.metric("Projected Savings", f"₹{PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR/100000:.2f} Lakhs/wk", "+₹91.3 Lakhs / year")

st.markdown("---")

# Main Navigation Tabs
tab_single, tab_batch, tab_economics = st.tabs([
    "🎯 Live Order Dispatch Simulator",
    "📊 Batch Simulation & Historical Telemetry",
    "💼 Boardroom Economics & Architecture"
])


# ==============================================================================
# TAB 1: Single Order Live Dispatch Simulator
# ==============================================================================
with tab_single:
    st.subheader("Live Single Order Qualification")
    st.markdown("Select a real-shaped customer order scenario from Dhaga's actual customer base or type a custom address:")

    # Preset selection
    preset_titles = [f"{tc['category']} — {tc['title']}" for tc in REAL_SHAPED_TEST_CASES]
    selected_preset_idx = st.selectbox("📌 Select Test Scenario Preset:", range(len(preset_titles)), format_func=lambda i: preset_titles[i])
    current_test = REAL_SHAPED_TEST_CASES[selected_preset_idx]

    c_in1, c_in2, c_in3 = st.columns([2, 1, 1])
    with c_in1:
        customer_name_input = st.text_input("Recipient Name", value=current_test["customer_name"])
    with c_in2:
        order_id_input = st.text_input("Order ID", value=current_test["id"])
    with c_in3:
        order_val_input = st.number_input("Order Value (₹)", value=current_test["order_value"], step=50.0)

    raw_addr_input = st.text_area("Customer Submitted Address (Raw Free-Text / Hinglish):", value=current_test["raw_address"], height=90)
    st.info(f"💡 **Scenario Context:** {current_test['description']}")

    if st.button("🚀 Qualify Order for Dispatch", type="primary", use_container_width=True):
        with st.spinner("Executing Pattern Pipeline: Parsing -> Deterministic Verification -> Risk Scoring -> Optimization..."):
            decision_result = process_dhaga_order(
                raw_address=raw_addr_input,
                customer_name=customer_name_input,
                order_id=order_id_input,
                order_value=order_val_input,
                api_key=api_key_input if api_key_input else None,
                provider=provider
            )

        st.markdown("### 📋 Dispatch Decision & Risk Breakdown")

        # Visible Failure Alert Banner
        if decision_result.fails_visibly:
            st.error(f"🚨 **{decision_result.failure_banner_message}**\n\n*Action Taken: Dispatch Halted immediately. Saved ₹120 in dead reverse logistics.*")

        # Top Decision Banner
        c_dec1, c_dec2, c_dec3 = st.columns([2, 1, 1])
        with c_dec1:
            if decision_result.decision == "APPROVE_INSTANT_DISPATCH":
                st.markdown('<div class="status-badge-approved">✅ APPROVE INSTANT DISPATCH</div>', unsafe_allow_html=True)
            elif decision_result.decision == "HOLD_WHATSAPP_CONFIRMATION":
                st.markdown('<div class="status-badge-hold">⚠️ HOLD: QUEUE WHATSAPP CONFIRMATION</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge-reject">🛑 REJECT: UNSERVICEABLE ADDRESS</div>', unsafe_allow_html=True)
            st.write(f"**Reason:** {decision_result.decision_summary}")

        with c_dec2:
            st.metric("RTO Risk Score", f"{decision_result.rto_assessment.risk_score} / 100", f"Tier: {decision_result.rto_assessment.risk_tier}")

        with c_dec3:
            st.metric("Logistics Loss Prevented", f"₹{decision_result.logistics_loss_prevented_inr:.0f}", "Direct ₹120 saved" if decision_result.logistics_loss_prevented_inr > 0 else "0 (Deliverable)")

        st.markdown("---")

        # Two-column layout for details
        c_det1, c_det2 = st.columns(2)

        with c_det1:
            st.markdown("#### 1️⃣ Structured Address Extraction (Fast Model)")
            p = decision_result.parsed_address
            st.markdown(f"**Clean Courier Label Address:**\n```\n{p.normalized_formatted_address}\n```")
            
            addr_df = pd.DataFrame([
                {"Component": "Premise / House / Flat", "Extracted Value": p.house_or_building or "❌ Not Found"},
                {"Component": "Street / Road / Gali", "Extracted Value": p.street_or_road or "❌ Unspecified"},
                {"Component": "Landmark", "Extracted Value": p.landmark or "❌ Not Found"},
                {"Component": "Locality / Village", "Extracted Value": p.locality_area or "N/A"},
                {"Component": "City / District", "Extracted Value": p.city or "Unknown"},
                {"Component": "State", "Extracted Value": p.state or "Unspecified"},
                {"Component": "Postal PIN Code", "Extracted Value": p.pincode or "❌ Missing"},
                {"Component": "Language Mix", "Extracted Value": p.language_detected},
            ])
            st.table(addr_df)

            st.markdown("#### 2️⃣ Deterministic Verification (0 Model Tokens)")
            det = decision_result.deterministic_checks
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.write(f"**PIN Regex Valid:** {'✅ Yes' if det.pincode_valid_format else '❌ No'}")
                st.write(f"**Postal Circle Matched:** {'✅ Yes' if det.pincode_zone_verified else '❌ Conflict'}")
            with d_col2:
                st.write(f"**Door Number Found:** {'✅ Yes' if det.has_door_or_building_number else '⚠️ No'}")
                st.write(f"**Landmark Found:** {'✅ Yes' if det.has_actionable_landmark else '⚠️ Missing'}")

            if det.validation_flags:
                st.warning("\n".join(f"- {flag}" for flag in det.validation_flags))

        with c_det2:
            st.markdown("#### 3️⃣ Evaluator-Optimizer: WhatsApp Pre-Dispatch Outreach")
            if decision_result.whatsapp_intervention:
                wi = decision_result.whatsapp_intervention
                st.write("**Customer Communication Preview (Hinglish):**")
                
                # Render smartphone mock
                st.markdown(f"""
                <div class="whatsapp-preview">
                    <div style="font-weight: 700; color: #075e54; margin-bottom: 6px;">💬 Dhaga & Co. Verified Business</div>
                    <div class="whatsapp-bubble">
                        {wi.customer_message_hinglish}
                        <div style="font-size: 0.75rem; color: #888; text-align: right; margin-top: 4px;">Just now · Delivered</div>
                    </div>
                    {"".join(f'<div class="whatsapp-button">🔘 {btn}</div>' for btn in wi.quick_reply_suggestions)}
                </div>
                """, unsafe_allow_html=True)

                if wi.missing_fields_highlighted:
                    st.caption(f"**Missing attributes requested:** {', '.join(wi.missing_fields_highlighted)}")
            else:
                st.success("✅ **No WhatsApp intervention required.** Address is sufficiently complete for first-attempt courier delivery.")

            st.markdown("---")
            st.markdown("#### 4️⃣ Engineering & Cost Telemetry (The Code vs Model Line)")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.write(f"**Fast Model:** `{decision_result.fast_model}`")
                st.write(f"**Judgment Model:** `{decision_result.judgment_model or 'None (Skipped: Low Risk)'}`")
            with t_col2:
                st.write(f"**Processing Latency:** `{decision_result.processing_time_ms} ms`")
                st.write(f"**Inference Cost:** `₹{decision_result.estimated_api_cost_inr:.4f}`")


# ==============================================================================
# TAB 2: Batch Simulation & Historical RTO Telemetry
# ==============================================================================
with tab_batch:
    st.subheader("Batch Order Simulation & Historical Analysis")
    st.markdown(
        "Demonstrating pipeline behavior across a sample batch of real-shaped Dhaga orders. "
        "Evaluates the code vs. model split, auto-approval percentage, and net money saved."
    )

    if st.button("⚡ Run Batch Simulation (7 Test Orders)", type="primary"):
        results_list = []
        progress_bar = st.progress(0)
        
        for idx, tc in enumerate(REAL_SHAPED_TEST_CASES):
            res = process_dhaga_order(
                raw_address=tc["raw_address"],
                customer_name=tc["customer_name"],
                order_id=tc["id"],
                order_value=tc["order_value"],
                api_key=api_key_input if api_key_input else None,
                provider=provider
            )
            results_list.append({
                "Order ID": res.order_id,
                "Customer": tc["customer_name"],
                "Category": tc["category"],
                "Order Value (₹)": res.order_value_inr,
                "Decision": res.decision,
                "Risk Tier": res.rto_assessment.risk_tier,
                "Risk Score": res.rto_assessment.risk_score,
                "Loss Saved (₹)": res.logistics_loss_prevented_inr,
                "API Cost (₹)": res.estimated_api_cost_inr,
                "Latency (ms)": res.processing_time_ms,
            })
            progress_bar.progress((idx + 1) / len(REAL_SHAPED_TEST_CASES))

        df_batch = pd.DataFrame(results_list)

        # Batch Summary Metrics
        b1, b2, b3, b4 = st.columns(4)
        total_saved = df_batch["Loss Saved (₹)"].sum()
        total_cost = df_batch["API Cost (₹)"].sum()
        approved_pct = (df_batch["Decision"] == "APPROVE_INSTANT_DISPATCH").mean() * 100
        
        with b1:
            st.metric("Total Batch Orders", len(df_batch))
        with b2:
            st.metric("Auto-Approved for Dispatch", f"{approved_pct:.1f}%")
        with b3:
            st.metric("Logistics Loss Intercepted", f"₹{total_saved:.0f}")
        with b4:
            st.metric("Total AI Cost", f"₹{total_cost:.4f}", f"ROI: {total_saved / total_cost:.0f}x" if total_cost > 0 else "N/A")

        st.dataframe(df_batch, use_container_width=True)


# ==============================================================================
# TAB 3: Boardroom Economics & Architecture
# ==============================================================================
with tab_economics:
    st.subheader("Financial Arithmetic for the Boardroom (Faizan, Ritu & Dev)")
    st.markdown("""
    Dhaga & Co. runs at **48,000 orders/week** with **61% Cash-on-Delivery**. 
    At 26% baseline RTO, Faizan loses **₹9.13 Lakhs every week** in dead logistics.
    """)

    econ = get_weekly_projected_ai_cost_inr(flagged_rate=0.30)
    
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.metric("Weekly COD Orders", f"{econ['weekly_cod_orders']:,}")
    with e2:
        st.metric("Weekly AI Compute Bill", f"₹{econ['total_ai_cost_inr']:.2f}", f"~${econ['total_ai_cost_inr']/84:.1f} USD / wk")
    with e3:
        st.metric("Weekly Logistics Retained", f"₹{econ['logistics_saved_inr']:,.0f}", "Assuming 5% RTO drop")
    with e4:
        st.metric("Net Weekly Profit", f"₹{econ['net_weekly_profit_inr']:,.0f}", f"ROI: {econ['roi_multiple']}x")

    st.markdown("---")
    st.subheader("The Code versus Model Boundary")
    st.markdown("""
    Every step is deliberately classified into deterministic code or an LLM call. 
    Models earn their place on messy language mapping and judgment—never on arithmetic, string search, or database lookup.
    """)

    arch_df = pd.DataFrame([
        {
            "Step": "1. Pincode Regex & Format",
            "Execution Type": "Deterministic Code",
            "Rationale": "Regex ^[1-9][0-9]{5}$ runs in <0.01 ms. An LLM should never be asked to count 6 digits."
        },
        {
            "Step": "2. Postal Circle Verification",
            "Execution Type": "Deterministic Code",
            "Rationale": "India Post prefix circle lookup table. Deterministic lookup guarantees zero hallucination."
        },
        {
            "Step": "3. High-Risk Phrase Flagging",
            "Execution Type": "Deterministic Code",
            "Rationale": "Regex matching for 'phone karna', 'kahi bhi', 'fake'. Instant, zero token cost."
        },
        {
            "Step": "4. Messy Address Parsing",
            "Execution Type": "Fast Model (Gemini 1.5 Flash)",
            "Rationale": "Extracts relative landmarks, Hinglish colloquialisms ('ke bagal me', 'shankar talkies ke peeche')."
        },
        {
            "Step": "5. RTO Risk Classification",
            "Execution Type": "Model + Rules Boundary",
            "Rationale": "Synthesizes geographic and semantic reachability into a calibrated 0-100 risk score."
        },
        {
            "Step": "6. WhatsApp Prompt Optimization",
            "Execution Type": "Judgment Model (Gemini 1.5 Pro)",
            "Rationale": "Generates empathetic, polite Hinglish copy tailored to Tier-2/3 women buyers to maximize address confirmation."
        },
    ])
    st.table(arch_df)

    st.markdown("---")
    st.subheader("Pattern Architecture: Why Each Pattern is Here")
    st.markdown("""
    - **Prompt Chaining**: Separating raw address extraction from risk evaluation prevents the model from hallucinating components. If parsing fails, risk assessment fails visibly.
    - **Routing**: Over 65% of orders are low-risk and bypass the expensive judgment model entirely, slashing Dhaga's weekly compute bill from ₹2,500 down to ₹667.
    - **Evaluator-Optimizer**: Ambiguous orders are evaluated for exact missing attributes, and a dedicated optimizer generates tailored WhatsApp intervention copy.
    """)

st.markdown("---")
st.caption("Dhaga & Co. COD Shield | FDE Academy Cohort 4 · Group 10 | Tech Track Mini Project 1")
