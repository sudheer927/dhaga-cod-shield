"""
Dhaga & Co. COD Shield
Pre-Dispatch Address Intelligence & Automated RTO Interception Control Tower
FDE Academy Cohort 4 · Mini Project 1 · Group 10
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

# Custom High-End Enterprise Styling (Linear / Stripe-inspired Dark & Light Palette)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header Bar */
    .top-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 14px;
        padding: 22px 28px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .header-badge {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .top-header h1 {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .top-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 6px 0 0 0;
        max-width: 850px;
    }
    
    /* FC Status Indicators */
    .fc-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.06);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        color: #cbd5e1;
        margin-right: 8px;
    }
    .fc-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
    }

    /* Workflow Banner (Explains Zero-Touch Concept) */
    .workflow-banner {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 24px;
    }
    .step-badge {
        font-weight: 700;
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .step-title {
        font-weight: 700;
        font-size: 0.92rem;
        color: #0f172a;
        margin-top: 2px;
    }
    .step-desc {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 2px;
    }

    /* Metric Cards */
    .stat-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -4px rgba(0,0,0,0.06);
    }
    .stat-title {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .stat-val {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0;
        letter-spacing: -0.02em;
    }
    .stat-sub {
        font-size: 0.8rem;
        font-weight: 600;
    }
    .stat-sub-red { color: #ef4444; }
    .stat-sub-green { color: #10b981; }
    .stat-sub-blue { color: #3b82f6; }

    /* Status Badges */
    .status-badge-approved {
        background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0;
        padding: 8px 14px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px;
    }
    .status-badge-hold {
        background: #fffbeb; color: #92400e; border: 1px solid #fde68a;
        padding: 8px 14px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px;
    }
    .status-badge-reject {
        background: #fef2f2; color: #991b1b; border: 1px solid #fecaca;
        padding: 8px 14px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px;
    }

    /* WhatsApp Smartphone Card */
    .phone-mockup {
        background: #efeae2;
        border-radius: 20px;
        border: 4px solid #1e293b;
        padding: 16px;
        max-width: 440px;
        box-shadow: 0 12px 28px -6px rgba(0,0,0,0.18);
        margin: 12px auto;
    }
    .phone-header {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #075e54;
        color: white;
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 14px;
    }
    .wa-bubble {
        background: #ffffff;
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 0.9rem;
        line-height: 1.45;
        color: #111827;
        position: relative;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }
    .wa-interactive-btn {
        background: #ffffff;
        color: #00a884;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 9px;
        text-align: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-top: 6px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)


# --- Sidebar: Configuration & Settings ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=50)
    st.markdown("### **Dhaga & Co.**")
    st.caption("FDE Engagement · Group 10")
    st.markdown("---")

    st.subheader("⚙️ AI Infrastructure")
    provider_choice = st.selectbox(
        "Inference Engine",
        ["Google Gemini (Recommended)", "OpenAI", "Offline Demo Mode (Zero Token Cost)"],
        index=0
    )

    api_key_input = ""
    if "Gemini" in provider_choice:
        provider = "gemini"
        default_key = os.getenv("GEMINI_API_KEY", "")
        api_key_input = st.text_input("Gemini API Key", value=default_key, type="password", help="Enter key from Google AI Studio. If blank, app runs high-accuracy offline demo mode.")
    elif "OpenAI" in provider_choice:
        provider = "openai"
        default_key = os.getenv("OPENAI_API_KEY", "")
        api_key_input = st.text_input("OpenAI API Key", value=default_key, type="password")
    else:
        provider = "mock"
        api_key_input = ""

    if api_key_input:
        from core.pipeline import test_api_connection
        if st.button("🔍 Test API Key Connection", use_container_width=True):
            with st.spinner("Testing API key..."):
                ok, diag_msg = test_api_connection(api_key_input, provider)
                if ok:
                    st.success(f"✅ {diag_msg}")
                else:
                    st.error(f"❌ {diag_msg}")


    st.markdown("---")
    st.markdown("#### 👥 Group 10 Team")
    st.markdown("""
    - **Venkata Sairam Sudheer**
    - **Omita Thakur**
    - **Sheikh Habib**
    - **Rohit Yadav**
    """)
    st.caption("Panel: Ruthvik | Sun 4 Oct (5:45 PM)")


# --- Top Header & Operational Context ---
st.markdown("""
<div class="top-header">
    <span class="header-badge">Automated Pre-Dispatch Protection</span>
    <h1>Dhaga & Co. — COD RTO Shield</h1>
    <p>Zero-touch intelligence engine embedded between checkout and warehouse label generation, intercepting unlocatable Tier-2/3 Hinglish addresses before couriers burn ₹120 in dead logistics.</p>
    <div style="margin-top: 14px;">
        <span class="fc-status-pill"><span class="fc-dot"></span> Bhiwandi FC (Active)</span>
        <span class="fc-status-pill"><span class="fc-dot"></span> Gurugram FC (Active)</span>
        <span class="fc-status-pill"><span class="fc-dot"></span> Hyderabad FC (Active)</span>
        <span class="fc-status-pill"><span class="fc-dot" style="background:#38bdf8; box-shadow:0 0 8px #38bdf8;"></span> Unicommerce Webhook: Connected</span>
    </div>
</div>
""", unsafe_allow_html=True)


# --- 4 Executive KPI Cards ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Weekly Orders</div>
        <div class="stat-val">{WEEKLY_TOTAL_ORDERS:,}</div>
        <div class="stat-sub stat-sub-blue">{WEEKLY_COD_ORDERS:,} COD Mix (61%)</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">COD RTO Rate</div>
        <div class="stat-val">{BASELINE_COD_RTO_RATE*100:.0f}%</div>
        <div class="stat-sub stat-sub-red">7,613 parcels/wk returned</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Weekly Cash Bleed</div>
        <div class="stat-val">₹{WEEKLY_LOGISTICS_BLEED_INR/100000:.2f}L</div>
        <div class="stat-sub stat-sub-red">Dead freight @ ₹120/parcel</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">Projected Net Retained</div>
        <div class="stat-val">₹{PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR/100000:.2f}L/wk</div>
        <div class="stat-sub stat-sub-green">+₹91.3 Lakhs / year EBITDA</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


# --- Visual Workflow Banner (Explains Zero-Touch) ---
st.markdown("""
<div class="workflow-banner">
    <div style="font-weight: 800; font-size: 0.95rem; color: #0f172a; margin-bottom: 12px;">
        ⚡ How It Works Without Burdening Staff (100% Automated Zero-Touch Pipeline)
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;">
        <div>
            <div class="step-badge">1. Auto-Ingestion</div>
            <div class="step-title">Order Placed via App</div>
            <div class="step-desc">Unicommerce webhook sends raw Hinglish address payload in <10 ms.</div>
        </div>
        <div>
            <div class="step-badge">2. Fast Qualification</div>
            <div class="step-title">Deterministic + Fast AI</div>
            <div class="step-desc">72% clear orders auto-approved; 5% bogus PINs instantly blocked.</div>
        </div>
        <div>
            <div class="step-badge">3. Customer Self-Resolve</div>
            <div class="step-title">Automated WhatsApp</div>
            <div class="step-desc">Ambiguous 23% get warm Hinglish 1-click prompts. Zero staff effort.</div>
        </div>
        <div>
            <div class="step-badge">4. Dispatch or Protect</div>
            <div class="step-title">Saved Freight</div>
            <div class="step-desc">Verified orders print courier labels. Unconfirmed orders save ₹120.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Tabs Navigation ---
tab_simulator, tab_warehouse, tab_pitch, tab_economics = st.tabs([
    "🎯 Live Order Inspection Simulator",
    "🏭 Warehouse Live Stream & Exceptions Desk",
    "💼 The Executive Pitch & Selling Strategy",
    "📐 Technical Architecture & Rubric Notes"
])


# ==============================================================================
# TAB 1: Live Order Inspection Simulator
# ==============================================================================
with tab_simulator:
    st.markdown("#### Test Real-Shaped Indian Customer Addresses")
    st.caption("Select a pre-loaded customer order scenario representing Dhaga's Tier-2/3 customer base, or type your own test case:")

    # Preset selection
    preset_names = [f"[{tc['category']}] {tc['title']}" for tc in REAL_SHAPED_TEST_CASES]
    chosen_idx = st.selectbox("Select Test Scenario Preset:", range(len(preset_names)), format_func=lambda i: preset_names[i])
    current_case = REAL_SHAPED_TEST_CASES[chosen_idx]

    c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
    with c_f1:
        c_name = st.text_input("Customer Name", value=current_case["customer_name"])
    with c_f2:
        c_id = st.text_input("Order ID", value=current_case["id"])
    with c_f3:
        c_val = st.number_input("Order Value (₹)", value=current_case["order_value"], step=50.0)

    c_addr = st.text_area("Customer Submitted Address (Raw Free-Text / Hinglish):", value=current_case["raw_address"], height=80)
    st.info(f"💡 **Why This Scenario Matters:** {current_case['description']}")

    if st.button("⚡ Inspect & Qualify Order Now", type="primary", use_container_width=True):
        with st.spinner("Processing pipeline: Parsing -> Postal Regex -> Risk Scorer -> WhatsApp Optimizer..."):
            res = process_dhaga_order(
                raw_address=c_addr,
                customer_name=c_name,
                order_id=c_id,
                order_value=c_val,
                api_key=api_key_input if api_key_input else None,
                provider=provider
            )

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Visible Failure Alert
        if res.fails_visibly:
            st.error(f"🚨 **{res.failure_banner_message}**\n\n*Action: Dispatch Halted Automatically. Prevented ₹120 Dead Reverse Logistics.*")

        # Top Decision Header
        d_c1, d_c2, d_c3 = st.columns([2, 1, 1])
        with d_c1:
            if res.decision == "APPROVE_INSTANT_DISPATCH":
                st.markdown('<div class="status-badge-approved">✅ APPROVE INSTANT DISPATCH</div>', unsafe_allow_html=True)
            elif res.decision == "HOLD_WHATSAPP_CONFIRMATION":
                st.markdown('<div class="status-badge-hold">⚠️ HOLD: QUEUE WHATSAPP CONFIRMATION</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge-reject">🛑 REJECT: UNSERVICEABLE ADDRESS</div>', unsafe_allow_html=True)
            st.write(f"**Action Summary:** {res.decision_summary}")

        with d_c2:
            st.metric("RTO Risk Score", f"{res.rto_assessment.risk_score} / 100", f"Tier: {res.rto_assessment.risk_tier}")

        with d_c3:
            st.metric("Dead Freight Saved", f"₹{res.logistics_loss_prevented_inr:.0f}", "Saved ₹120" if res.logistics_loss_prevented_inr > 0 else "0 (Deliverable)")

        st.markdown("---")

        # Two-column layout
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.markdown("##### 1️⃣ Structured Courier Label Breakdown")
            pa = res.parsed_address
            st.code(pa.normalized_formatted_address, language="text")

            spec_df = pd.DataFrame([
                {"Component": "Premise / House / Shop", "Extracted Value": pa.house_or_building or "❌ Not Found"},
                {"Component": "Street / Road / Gali", "Extracted Value": pa.street_or_road or "❌ Unspecified"},
                {"Component": "Relative Landmark", "Extracted Value": pa.landmark or "❌ Not Found"},
                {"Component": "Locality / Village", "Extracted Value": pa.locality_area or "N/A"},
                {"Component": "City / District", "Extracted Value": pa.city or "Unknown"},
                {"Component": "State", "Extracted Value": pa.state or "Unspecified"},
                {"Component": "6-Digit Postal PIN", "Extracted Value": pa.pincode or "❌ Missing"},
                {"Component": "Language Mix", "Extracted Value": pa.language_detected},
            ])
            st.table(spec_df)

            st.markdown("##### 2️⃣ Deterministic Verification (0 Model Tokens)")
            det = res.deterministic_checks
            det_c1, det_c2 = st.columns(2)
            with det_c1:
                st.write(f"**PIN Regex Valid:** {'✅ Yes' if det.pincode_valid_format else '❌ No'}")
                st.write(f"**Postal Circle Matched:** {'✅ Yes' if det.pincode_zone_verified else '❌ Conflict'}")
            with det_c2:
                st.write(f"**Door Number Present:** {'✅ Yes' if det.has_door_or_building_number else '⚠️ No'}")
                st.write(f"**Landmark Present:** {'✅ Yes' if det.has_actionable_landmark else '⚠️ Missing'}")

            if det.validation_flags:
                for flag in det.validation_flags:
                    st.warning(flag)

        with right_col:
            st.markdown("##### 3️⃣ Evaluator-Optimizer: WhatsApp Empathy Outreach")
            if res.whatsapp_intervention:
                wi = res.whatsapp_intervention
                st.caption("Generated in Hinglish for mobile shopper with 1-click interactive resolution:")

                # Smartphone Mockup
                st.markdown(f"""
                <div class="phone-mockup">
                    <div class="phone-header">
                        <img src="https://img.icons8.com/color/48/whatsapp--v1.png" width="24"/>
                        <div>
                            <div style="font-weight:700; font-size:0.95rem;">Dhaga & Co. Verified</div>
                            <div style="font-size:0.75rem; opacity:0.85;">Official Business Account</div>
                        </div>
                    </div>
                    <div class="wa-bubble">
                        {wi.customer_message_hinglish}
                        <div style="font-size:0.75rem; color:#9ca3af; text-align:right; margin-top:4px;">14:45 · Delivered ✓✓</div>
                    </div>
                    {"".join(f'<div class="wa-interactive-btn">🔘 {btn}</div>' for btn in wi.quick_reply_suggestions)}
                </div>
                """, unsafe_allow_html=True)

                if wi.missing_fields_highlighted:
                    st.info(f"📌 **Missing details requested:** {', '.join(wi.missing_fields_highlighted)}")
            else:
                st.success("✅ **No customer outreach needed.** Address is clear and ready for courier label generation.")

            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 4️⃣ Telemetry & Cost Line")
            m_c1, m_c2 = st.columns(2)
            with m_c1:
                st.write(f"**Fast Model:** `{res.fast_model}`")
                st.write(f"**Judgment Model:** `{res.judgment_model or 'Skipped (Low Risk)'}`")
            with m_c2:
                st.write(f"**Execution Latency:** `{res.processing_time_ms} ms`")
                st.write(f"**Inference Cost:** `₹{res.estimated_api_cost_inr:.4f}`")


# ==============================================================================
# TAB 2: Warehouse Live Stream & Exceptions Desk
# ==============================================================================
with tab_warehouse:
    st.markdown("#### 🏭 Real-Time Warehouse Dispatch Feed")
    st.markdown("""
    Shows how the system runs **silently in the background** across Dhaga's 3 fulfillment centers. 
    Staff never manually input orders—they only monitor automated throughput and handle true exceptions.
    """)

    if st.button("🔄 Stream Simulated Orders (Bhiwandi / Gurugram / Hyderabad)", type="primary"):
        feed_data = []
        progress = st.progress(0)
        
        for i, tc in enumerate(REAL_SHAPED_TEST_CASES):
            order_res = process_dhaga_order(
                raw_address=tc["raw_address"],
                customer_name=tc["customer_name"],
                order_id=tc["id"],
                order_value=tc["order_value"],
                api_key=api_key_input if api_key_input else None,
                provider=provider
            )
            feed_data.append({
                "Order ID": order_res.order_id,
                "Recipient": tc["customer_name"],
                "Origin FC": ["Bhiwandi", "Gurugram", "Hyderabad"][i % 3],
                "Order Value": f"₹{order_res.order_value_inr:.0f}",
                "Status": "🟢 Auto-Approved" if order_res.decision == "APPROVE_INSTANT_DISPATCH" else ("🟡 WhatsApp Sent" if order_res.decision == "HOLD_WHATSAPP_CONFIRMATION" else "🔴 Blocked & Saved ₹120"),
                "Risk Tier": order_res.rto_assessment.risk_tier,
                "Action": order_res.decision_summary[:45] + "...",
                "Freight Saved": f"₹{order_res.logistics_loss_prevented_inr:.0f}",
            })
            progress.progress((i + 1) / len(REAL_SHAPED_TEST_CASES))

        st.dataframe(pd.DataFrame(feed_data), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🚨 The 1-Click Operations Exception Desk")
    st.markdown("""
    **This is the ONLY screen a human ever touches.** If a customer does not reply to WhatsApp within 12 hours, 
    the order appears here. The operator does not type anything—they resolve it with a single click:
    """)

    e_col1, e_col2, e_col3 = st.columns([2, 1, 1])
    with e_col1:
        st.markdown("""
        **Order #DHAGA-1003** · *Anita Devi (Deoria, UP)*  
        `Dr. Verma clinic ke samne, shiv mandir road, Deoria 274001`  
        **Issue:** Missing house number; landmark present. WhatsApp prompt sent 12h ago.
        """)
    with e_col2:
        if st.button("✓ Approve with Courier Note", key="appr_btn", use_container_width=True):
            st.success("Approved! Dispatched to Ekart with landmark highlighted on run sheet.")
    with e_col3:
        if st.button("✕ Cancel COD & Restock", key="canc_btn", use_container_width=True):
            st.warning("Cancelled. Saved ₹120 dead freight. Garment returned to live inventory.")


# ==============================================================================
# TAB 3: The Executive Pitch & Selling Strategy
# ==============================================================================
with tab_pitch:
    st.markdown("### 💼 How to Pitch & Sell This to Ritu, Faizan & Dev")
    st.markdown("""
    This guide explains **why this is not an administrative burden** and gives your team the exact talking points 
    to handle the boardroom during your 20-minute presentation with **Ruthvik**.
    """)

    st.markdown("#### 1️⃣ The Core Argument: Why This Is NOT a Burden on Staff")
    st.markdown("""
    * **No Manual Data Entry:** Staff are **not** sitting at desks typing addresses. The engine runs as an automated API filter connected to Dhaga’s Unicommerce platform.
    * **72% of Orders are Zero-Touch:** Legitimate, clean addresses pass through in under 100 milliseconds and print shipping labels automatically.
    * **Customer Self-Resolution via WhatsApp:** For the 23% ambiguous addresses, the system sends an automated WhatsApp message asking the customer to confirm their location on a map or add their door number. The customer fixes their own address!
    * **Only 2% Reach the Exception Desk:** Warehouse operators only see the tiny fraction of orders that are completely unresolvable, resolving them with a single click.
    """)

    st.markdown("---")
    st.markdown("#### 2️⃣ The Rupee Arithmetic (How to Convince Faizan & Ritu)")
    st.markdown("""
    | Metric | Current Reality | With COD Shield | What It Means to Dhaga |
    | :--- | :---: | :---: | :--- |
    | **Weekly COD Orders** | 29,280 | 29,280 | 61% of all 48k orders are COD |
    | **COD RTO Rate** | **26%** | **21%** | 5 percentage point drop |
    | **Failed Deliveries / Week** | **7,613 orders** | **6,149 orders** | **1,464 parcels saved from returning** |
    | **Weekly Dead Logistics Burn** | **₹9.13 Lakhs** | **₹7.38 Lakhs** | **₹1.76 Lakhs saved every single week** |
    | **Annual Cash Retained** | ₹0 | **₹91.3 Lakhs / yr** | Direct EBITDA addition |
    | **Weekly AI Compute Cost** | ₹0 | **₹1,350 / week** | ~$16 USD/week |
    | **Net Return on Investment** | — | **130x ROI** | For every ₹1 spent on AI, Dhaga saves ₹130 in freight |
    """)

    st.markdown("---")
    st.markdown("#### 3️⃣ Boardroom Pushback: How to Answer Live in Under 30 Seconds")
    
    with st.expander("Q1: Dev (CTO) asks: '16 engineers, 0 ML engineers. Who runs this on Monday?'", expanded=True):
        st.markdown("""
        **Your Answer:**  
        *"Dev, that's why we deliberately built this with zero ML models hosted on-premise. There is no PyTorch, no CUDA, and no GPU servers to manage. It's a lightweight Python service that consumes standard REST APIs and validates schemas with Pydantic. Any backend engineer who can write a standard Unicommerce webhook can maintain this in under two hours."*
        """)

    with st.expander("Q2: Faizan asks: 'What if your system is wrong 1 in 20 times?'", expanded=True):
        st.markdown("""
        **Your Answer:**  
        *"Faizan, we never cancel an order arbitrarily. If the model is uncertain, it does not reject the parcel—it routes to a polite, automated WhatsApp confirmation. Even if the customer ignores WhatsApp, the order fails visibly on screen for a 1-click human decision. Silent errors are zero."*
        """)

    with st.expander("Q3: Ritu (CEO) asks: 'What if customers just don't have money when the courier arrives?'", expanded=True):
        st.markdown("""
        **Your Answer:**  
        *"Ritu, that is exactly why the WhatsApp pre-dispatch confirmation is so powerful. An impulse buyer who ordered on a whim will ignore the WhatsApp message or click 'Cancel Order'. Intercepting that cancellation before the package leaves Bhiwandi saves the ₹120 freight and keeps that kurti in active inventory instead of trapped in a 14-day return cycle."*
        """)


# ==============================================================================
# TAB 4: Technical Architecture & Rubric Notes
# ==============================================================================
with tab_economics:
    st.markdown("#### 📐 Rubric Compliance & Ground Rules")
    st.markdown("""
    This tab documents the explicit technical choices demanded by the project rubric:
    """)

    st.markdown("##### The Code versus Model Boundary")
    arch_table = pd.DataFrame([
        {
            "Step": "1. PIN Regex Validation",
            "Mechanism": "Deterministic Python",
            "Model / Tool": "Regex `^[1-9][0-9]{5}$`",
            "Temperature": "N/A",
            "Why It Belongs Here": "Runs in <0.01 ms with 100% precision. Never ask an LLM to count 6 digits."
        },
        {
            "Step": "2. Postal Circle Verification",
            "Mechanism": "Deterministic Python",
            "Model / Tool": "India Post 2-Digit Prefix Table",
            "Temperature": "N/A",
            "Why It Belongs Here": "Guarantees zero geographic hallucinations (e.g. 400001 is Mumbai, not Jaipur)."
        },
        {
            "Step": "3. High-Risk Phrase Flagging",
            "Mechanism": "Deterministic Python",
            "Model / Tool": "Keyword Pattern Matching",
            "Temperature": "N/A",
            "Why It Belongs Here": "Catches 'phone pe baat', 'kahi bhi de do' for 0 token cost."
        },
        {
            "Step": "4. Address Parsing & Normalization",
            "Mechanism": "Fast LLM",
            "Model / Tool": "Gemini 1.5/2.5 Flash",
            "Temperature": "0.1",
            "Why It Belongs Here": "Normalizes colloquial Hinglish landmarks ('shankar talkies ke peeche') and spelling drift."
        },
        {
            "Step": "5. RTO Risk Scorer",
            "Mechanism": "Model + Rules Boundary",
            "Model / Tool": "Hybrid Pydantic Function",
            "Temperature": "0.1",
            "Why It Belongs Here": "Synthesizes deterministic postal checks with linguistic confidence into calibrated 0-100 score."
        },
        {
            "Step": "6. WhatsApp Empathy Outreach",
            "Mechanism": "Judgment LLM",
            "Model / Tool": "Gemini 1.5/2.5 Pro",
            "Temperature": "0.3",
            "Why It Belongs Here": "Synthesizes warm, non-accusatory Hinglish copy with 1-click interactive buttons."
        },
    ])
    st.table(arch_table)

    st.markdown("---")
    st.markdown("##### The Three Patterns Chosen on Purpose")
    st.markdown("""
    1. **Prompt Chaining:** Separating address entity extraction from risk evaluation prevents landmark hallucination.
    2. **Routing:** Over 65% of orders are low-risk and bypass the heavier judgment model, slashing weekly compute cost by 4.5x.
    3. **Evaluator-Optimizer:** Evaluates precise missing attributes and optimizes conversational WhatsApp copy to maximize customer response.
    """)

st.markdown("---")
st.caption("Dhaga & Co. COD Shield · FDE Academy Cohort 4 · Group 10 · Deployed on Streamlit Community Cloud")
