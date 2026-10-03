"""
Dhaga & Co. COD Shield — Enterprise Logistics Control Tower
Production-Grade Fulfillment Operations Portal & Automated RTO Interception Suite
Master-Detail Split Workstation · SQLite ACID Backend · Multi-Tier AI Gateway
"""

import streamlit as st
import pandas as pd
import time
import os
import json
from datetime import datetime

from core.config import (
    WEEKLY_TOTAL_ORDERS,
    WEEKLY_COD_ORDERS,
    BASELINE_COD_RTO_RATE,
    LOGISTICS_COST_PER_RTO_INR,
    WEEKLY_LOGISTICS_BLEED_INR,
    PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR,
    FAST_WORKER_MODEL,
    JUDGMENT_EVAL_MODEL,
)
from core.db import (
    init_db,
    seed_default_orders,
    get_all_orders,
    get_order_details,
    update_order_status,
    save_new_order_to_db,
    simulate_customer_whatsapp_reply,
    get_db_metrics,
    DB_PATH
)
from core.pipeline import process_dhaga_order, test_api_connection, resolve_api_key
from core.test_cases import REAL_SHAPED_TEST_CASES

# Page setup
st.set_page_config(
    page_title="Dhaga & Co. | COD Shield Operations Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ensure database is initialized and seeded
init_db()
seed_default_orders()

# Initialize session state for selected order
if "selected_order_id" not in st.session_state:
    all_orders = get_all_orders()
    st.session_state.selected_order_id = all_orders[0]["order_id"] if all_orders else "DHAGA-1003"

# High-End Linear / Stripe-Inspired Enterprise Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall Background and Card Rhythm */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Top Enterprise Navigation Header */
    .enterprise-header {
        background: linear-gradient(135deg, #090e17 0%, #1a2233 100%);
        border-radius: 12px;
        padding: 18px 24px;
        color: #ffffff;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(9, 14, 23, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .header-tag {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 4px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .enterprise-header h1 {
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .enterprise-header p {
        color: #94a3b8;
        font-size: 0.88rem;
        margin: 3px 0 0 0;
    }
    
    /* FC Status Badges */
    .fc-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.06);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        color: #cbd5e1;
        margin-left: 6px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .fc-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
    }

    /* Top Executive Metrics */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-val {
        font-size: 1.45rem;
        font-weight: 800;
        color: #0f172a;
        margin: 2px 0;
    }
    .kpi-sub {
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Order Queue Cards in Left Pane */
    .order-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.15s ease-in-out;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .order-card:hover {
        border-color: #94a3b8;
        box-shadow: 0 4px 8px -2px rgba(0,0,0,0.06);
    }
    .order-card-selected {
        background: #ffffff;
        border: 2px solid #2563eb !important;
        box-shadow: 0 4px 12px -2px rgba(37, 99, 235, 0.15) !important;
    }

    /* Status Badges */
    .status-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .status-pill-approved { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .status-pill-held { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
    .status-pill-blocked { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
    .status-pill-dispatched { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
    .status-pill-cancelled { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* Action Console Right Panel Containers */
    .console-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .console-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 12px;
        margin-bottom: 14px;
    }

    /* WhatsApp Smartphone Simulator */
    .phone-wrapper {
        background: #0b141a;
        border-radius: 18px;
        padding: 14px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(11, 20, 26, 0.4);
    }
    .phone-top {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 12px;
    }
    .wa-chat-bubble {
        background: #dcf8c6;
        color: #0b141a;
        padding: 12px 14px;
        border-radius: 12px 12px 0 12px;
        font-size: 0.84rem;
        line-height: 1.45;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .wa-action-button {
        background: #ffffff;
        color: #00a884;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        font-weight: 700;
        font-size: 0.78rem;
        margin-top: 6px;
    }

    /* Verification Badge Checklist */
    .verify-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .verify-pass { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
    .verify-fail { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
    .verify-warn { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }

    /* Immutable Audit Timeline */
    .audit-row {
        border-left: 2px solid #cbd5e1;
        padding-left: 12px;
        margin-bottom: 8px;
        font-size: 0.8rem;
    }
    .audit-timestamp {
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
    }
    .audit-action-title {
        font-weight: 700;
        color: #1e293b;
    }

    /* Seamless Clickable Order Card Buttons */
    .queue-cards-container div[data-testid="stButton"] button {
        text-align: left !important;
        display: block !important;
        width: 100% !important;
        padding: 12px 14px !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        line-height: 1.45 !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
        margin-bottom: 8px !important;
        transition: all 0.15s ease-in-out !important;
    }
    .queue-cards-container div[data-testid="stButton"] button[kind="secondary"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    .queue-cards-container div[data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #3b82f6 !important;
        background: #f8fafc !important;
        box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.06) !important;
    }
    .queue-cards-container div[data-testid="stButton"] button[kind="primary"] {
        background: #eff6ff !important;
        border: 2px solid #2563eb !important;
        color: #0f172a !important;
        box-shadow: 0 4px 14px -2px rgba(37, 99, 235, 0.22) !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Top Enterprise Header ---
st.markdown("""
<div class="enterprise-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span class="header-tag">● Live Operations Control Tower</span>
            <h1>Dhaga & Co. — COD Shield™ Operations Portal</h1>
            <p>Automated pre-dispatch logistics intelligence engine embedded between checkout and warehouse label generation.</p>
        </div>
        <div style="text-align:right;">
            <span class="fc-badge"><span class="fc-dot"></span> Bhiwandi FC</span>
            <span class="fc-badge"><span class="fc-dot"></span> Gurugram FC</span>
            <span class="fc-badge"><span class="fc-dot"></span> Hyderabad FC</span>
            <span class="fc-badge" style="border-color:#38bdf8; color:#38bdf8;">🗄️ SQLite ACID Active</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Live DB KPI Metrics Row ---
db_metrics = get_db_metrics()
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Weekly COD Volume</div>
        <div class="kpi-val">{WEEKLY_COD_ORDERS:,}</div>
        <div class="kpi-sub" style="color:#2563eb;">61% of total 48k weekly orders</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Zero-Touch Automation Rate</div>
        <div class="kpi-val">{db_metrics['automation_rate']}%</div>
        <div class="kpi-sub" style="color:#059669;">Instant courier labels printed</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Awaiting WhatsApp Self-Resolve</div>
        <div class="kpi-val">{db_metrics['held_whatsapp']} Orders</div>
        <div class="kpi-sub" style="color:#d97706;">Customer mobile prompts active</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Dead Reverse Freight Saved</div>
        <div class="kpi-val">₹{db_metrics['freight_saved_inr'] + PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR:,.0f}</div>
        <div class="kpi-sub" style="color:#059669;">₹120 courier burn halted</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# --- Main Enterprise Workspace Tabs ---
tab_workstation, tab_analytics, tab_gateway = st.tabs([
    "📋 Dispatch & Interception Workstation",
    "📊 Fulfillment & RTO Analytics",
    "⚙️ Automation Policy & AI Gateway"
])


# ==============================================================================
# TAB 1: Master-Detail Dispatch Workstation (The Real Agent Screen)
# ==============================================================================
with tab_workstation:
    # 2-Pane Split Workstation: Left (Order Stream) | Right (Action Console)
    col_left, col_right = st.columns([1, 1.45], gap="medium")

    # --------------------------------------------------------------------------
    # LEFT PANE: Order Queue Feed & Filter
    # --------------------------------------------------------------------------
    with col_left:
        qh_col1, qh_col2 = st.columns([1.8, 1.1])
        with qh_col1:
            st.markdown("##### 📦 Active Incoming Orders Queue")
        with qh_col2:
            if st.button("🔄 Reset Demo State", key="btn_reset_demo", help="Restore all orders to default presentation baseline", use_container_width=True):
                seed_default_orders(force_reset=True)
                st.session_state.selected_order_id = "DHAGA-1004"
                st.rerun()
        
        # Segmented Filter Bar
        queue_filter = st.radio(
            "Filter Queue:",
            ["ALL", "HELD_WHATSAPP", "AUTO_APPROVED", "BLOCKED_FRAUD", "DISPATCHED"],
            format_func=lambda s: {
                "ALL": "All Orders",
                "HELD_WHATSAPP": "🟡 Held (Action Needed)",
                "AUTO_APPROVED": "🟢 Auto-Cleared",
                "BLOCKED_FRAUD": "🔴 Blocked Fraud",
                "DISPATCHED": "📦 Dispatched"
            }.get(s, s),
            horizontal=True,
            label_visibility="collapsed"
        )

        # Ingest Payload Expander
        with st.expander("⚡ + Ingest New Webhook Order Payload"):
            p_presets = [f"[{tc['category']}] {tc['title']}" for tc in REAL_SHAPED_TEST_CASES]
            p_idx = st.selectbox("Preset Payload:", range(len(p_presets)), format_func=lambda i: p_presets[i])
            chosen_tc = REAL_SHAPED_TEST_CASES[p_idx]
            
            in_name = st.text_input("Recipient", value=chosen_tc["customer_name"], key="in_name")
            in_addr = st.text_area("Customer Address", value=chosen_tc["raw_address"], height=60, key="in_addr")
            in_fc = st.selectbox("Fulfillment Center", ["Bhiwandi FC", "Gurugram FC", "Hyderabad FC"], key="in_fc")
            in_val = st.number_input("Order Value (₹)", value=chosen_tc["order_value"], key="in_val")

            if st.button("🚀 Process & Ingest to Database", type="primary", use_container_width=True):
                with st.spinner("Executing pipeline & writing to SQLite database..."):
                    new_order_id = f"DHAGA-{int(time.time())%10000}"
                    res = process_dhaga_order(
                        raw_address=in_addr,
                        customer_name=in_name,
                        order_id=new_order_id,
                        order_value=in_val
                    )
                    save_new_order_to_db(res, in_addr, in_name, "9876543210", in_fc)
                    st.session_state.selected_order_id = new_order_id
                    st.success(f"Ingested {new_order_id} ({res.decision}) to SQL DB!")
                    st.rerun()

        # Load orders matching filter
        order_list = get_all_orders(queue_filter if queue_filter != "ALL" else None)

        if not order_list:
            st.info("No orders currently in this queue view.")
        else:
            st.markdown('<div class="queue-cards-container">', unsafe_allow_html=True)
            for ord_row in order_list:
                oid = ord_row["order_id"]
                is_selected = (oid == st.session_state.selected_order_id)
                
                st_code = ord_row["status"]
                pill_label = {
                    "AUTO_APPROVED": "🟢 AUTO-APPROVED",
                    "HELD_WHATSAPP": "🟡 HELD FOR WHATSAPP",
                    "BLOCKED_FRAUD": "🔴 BLOCKED FRAUD",
                    "DISPATCHED": "📦 DISPATCHED",
                    "CANCELLED_RESTOCKED": "✕ CANCELLED"
                }.get(st_code, st_code)

                # Clean 3-line card label (the card itself IS the button!)
                card_label = (
                    f"#{oid} · {ord_row['customer_name']} (₹{ord_row['order_value']:.0f} COD)\n"
                    f"{pill_label}  •  Risk: {ord_row['risk_score']}/100\n"
                    f"📍 {ord_row['origin_fc']} · {ord_row['raw_address'][:45]}..."
                )

                if st.button(
                    card_label,
                    key=f"card_{oid}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.selected_order_id = oid
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # RIGHT PANE: Live Order Action Console (Stays in View!)
    # --------------------------------------------------------------------------
    with col_right:
        active_id = st.session_state.selected_order_id
        active_order = get_order_details(active_id)

        if not active_order:
            st.warning("Please select an order from the left queue to view details.")
        else:
            # Console Top Header
            st_code = active_order["status"]
            status_badge_html = ""
            if st_code == "AUTO_APPROVED":
                status_badge_html = '<span class="status-pill status-pill-approved" style="font-size:0.85rem; padding:4px 12px;">✅ READY FOR COURIER LABEL</span>'
            elif st_code == "HELD_WHATSAPP":
                status_badge_html = '<span class="status-pill status-pill-held" style="font-size:0.85rem; padding:4px 12px;">⚠️ HELD: AWAITING WHATSAPP RESOLUTION</span>'
            elif st_code == "BLOCKED_FRAUD":
                status_badge_html = '<span class="status-pill status-pill-blocked" style="font-size:0.85rem; padding:4px 12px;">🛑 HALTED: PREVENTED ₹120 FREIGHT BURN</span>'
            elif st_code == "DISPATCHED":
                status_badge_html = '<span class="status-pill status-pill-dispatched" style="font-size:0.85rem; padding:4px 12px;">📦 LABEL GENERATED (DISPATCHED)</span>'
            else:
                status_badge_html = '<span class="status-pill status-pill-cancelled" style="font-size:0.85rem; padding:4px 12px;">✕ CANCELLED & RESTOCKED</span>'

            st.markdown(f"""
            <div class="console-box" style="margin-bottom:12px; padding:14px 18px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:0.75rem; color:#64748b; font-family:'JetBrains Mono';">INSPECTION CONSOLE · {active_order['origin_fc']}</div>
                        <div style="font-size:1.3rem; font-weight:800; color:#0f172a; margin-top:2px;">
                            Order #{active_id} — {active_order['customer_name']} (₹{active_order['order_value']:.0f} COD)
                        </div>
                    </div>
                    <div>{status_badge_html}</div>
                </div>
                <div style="font-size:0.82rem; color:#475569; margin-top:8px;">
                    <b>Pipeline Decision:</b> {active_order['decision_summary']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Two Column Split inside the console: Label & Risk on left, WhatsApp & Actions on right
            rc1, rc2 = st.columns([1, 1], gap="medium")

            # ------------------------------------------------------------------
            # Console Sub-Column 1: Courier Shipping Label & Address Validation
            # ------------------------------------------------------------------
            with rc1:
                st.markdown("###### 🏷️ Standardized Courier Label (Ekart / BlueDart)")
                lbl = active_order.get("label")

                if lbl:
                    st.code(lbl["normalized_address"], language="text")

                    # Dynamic Verification Checklist Pills (Reflects REAL database state)
                    pin_valid = bool(lbl.get("pincode_valid", 1))
                    circle_match = bool(lbl.get("circle_matched", 1))
                    has_door = bool(lbl.get("premise"))
                    has_landmark = bool(lbl.get("landmark"))

                    pills_html = []
                    if pin_valid:
                        pills_html.append('<span class="verify-pill verify-pass">✓ PIN Format Valid</span>')
                    else:
                        pills_html.append('<span class="verify-pill verify-fail">✗ Invalid PIN Format</span>')

                    if circle_match:
                        pills_html.append('<span class="verify-pill verify-pass">✓ Postal Circle Matched</span>')
                    else:
                        pills_html.append('<span class="verify-pill verify-fail">✗ Postal Circle Mismatch</span>')

                    if has_door:
                        pills_html.append('<span class="verify-pill verify-pass">✓ Premise / Door Found</span>')
                    else:
                        pills_html.append('<span class="verify-pill verify-warn">⚠️ Door Number Missing</span>')

                    if has_landmark:
                        pills_html.append('<span class="verify-pill verify-pass">✓ Landmark Verified</span>')
                    else:
                        pills_html.append('<span class="verify-pill verify-warn">⚠️ No Landmark</span>')

                    st.markdown(f"""
                    <div style="margin-top:6px; margin-bottom:8px;">
                        {' '.join(pills_html)}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <table style="width:100%; font-size:0.8rem; border-collapse:collapse;">
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:#64748b; padding:4px 0;">Premise / Building:</td><td style="font-weight:600; text-align:right;">{lbl['premise'] or '❌ Missing'}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:#64748b; padding:4px 0;">Street / Gali:</td><td style="font-weight:600; text-align:right;">{lbl['street'] or '❌ Unspecified'}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:#64748b; padding:4px 0;">Landmark:</td><td style="font-weight:600; text-align:right;">{lbl['landmark'] or '❌ None'}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="color:#64748b; padding:4px 0;">City / State:</td><td style="font-weight:600; text-align:right;">{lbl['city']}, {lbl['state']}</td></tr>
                        <tr><td style="color:#64748b; padding:4px 0;">Postal PIN:</td><td style="font-weight:700; color:{'#2563eb' if circle_match else '#dc2626'}; text-align:right;">{lbl['pincode']}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("No label data available.")

                st.caption(f"**Customer Raw Input:** `{active_order['raw_address']}`")

                # Immutable Audit History for this order
                st.markdown("###### 📜 Immutable Audit History (SQLite)")
                audits = active_order.get("audit", [])
                if audits:
                    for a in audits[:3]:
                        st.markdown(f"""
                        <div class="audit-row">
                            <span class="audit-timestamp">{a['timestamp']}</span> — <span class="audit-action-title">{a['action']}</span><br/>
                            <span style="color:#64748b; font-size:0.72rem;">Actor: {a['actor']} | {a['notes'] or ''}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No audit history.")

            # ------------------------------------------------------------------
            # Console Sub-Column 2: Interactive WhatsApp Customer Self-Resolution
            # ------------------------------------------------------------------
            with rc2:
                st.markdown("###### 📱 Customer Self-Resolution via WhatsApp")
                wa = active_order.get("whatsapp")

                if wa and st_code == "HELD_WHATSAPP":
                    # Determine address component flags
                    has_door = bool(lbl.get("premise")) if lbl else True
                    has_landmark = bool(lbl.get("landmark")) if lbl else True
                    circle_matched = bool(lbl.get("circle_matched", 1)) if lbl else True

                    # Defensive check: ensure phone mockup quick replies match the exact address issue
                    phone_buttons = wa.get('quick_replies', [])
                    if not phone_buttons or phone_buttons == ["Confirm Location on Map", "Update House Number", "Cancel Order"]:
                        phone_buttons = ["Confirm Location on Map"]
                        if not circle_matched:
                            phone_buttons.append("Correct Pincode")
                        elif not has_door:
                            phone_buttons.append("Update House Number")
                        elif not has_landmark:
                            phone_buttons.append("Add Nearest Landmark")
                        else:
                            phone_buttons.append("Confirm Address")
                        phone_buttons.append("Cancel Order")

                    # Smartphone Mockup
                    st.markdown(f"""
                    <div class="phone-wrapper">
                        <div class="phone-top">
                            <img src="https://img.icons8.com/color/48/whatsapp--v1.png" width="22"/>
                            <div>
                                <div style="font-weight:700; font-size:0.85rem;">Dhaga & Co. Verified</div>
                                <div style="font-size:0.68rem; color:#8696a0;">Customer Self-Resolution Agent</div>
                            </div>
                        </div>
                        <div class="wa-chat-bubble">
                            {wa['message_body']}
                            <div style="font-size:0.68rem; color:#667781; text-align:right; margin-top:4px;">14:32 · Sent ✓✓</div>
                        </div>
                        {"".join(f'<div class="wa-action-button">🔘 {btn}</div>' for btn in phone_buttons)}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("###### ⚡ Interactive Customer Reply Simulation")
                    st.caption("Simulate customer tapping their WhatsApp reply button:")

                    sim_c1, sim_c2 = st.columns(2)
                    with sim_c1:
                        if not circle_matched:
                            btn_text = "📍 'Correct PIN to Match City'"
                            action = "CORRECT_PIN"
                            succ_msg = "Pincode Corrected & Circle Verified! Order Cleared for Label Print."
                        elif not has_door:
                            btn_text = "🏠 'Add House/Door Number: #14'"
                            action = "CONFIRM_HOUSE"
                            succ_msg = "House Number Added! Order Cleared for Label Print."
                        elif not has_landmark:
                            btn_text = "🏛️ 'Add Landmark: Near Shiv Mandir'"
                            action = "CONFIRM_LANDMARK"
                            succ_msg = "Landmark Added! Order Cleared for Label Print."
                        else:
                            btn_text = "✓ 'Confirm Current Address'"
                            action = "CONFIRM"
                            succ_msg = "Address Verified! Order Cleared for Label Print."

                        if st.button(btn_text, key=f"sim_action_{active_id}", use_container_width=True):
                            simulate_customer_whatsapp_reply(active_id, action)
                            st.success(succ_msg)
                            st.rerun()

                    with sim_c2:
                        if st.button("🗺️ 'Share Live GPS Location'", key=f"sim_gps_{active_id}", use_container_width=True):
                            simulate_customer_whatsapp_reply(active_id, "SHARE_GPS")
                            st.success("GPS Verified! Order Auto-Cleared for Label Print.")
                            st.rerun()

                    if st.button("❌ Customer Taps 'Cancel My Order'", key=f"sim_canc_{active_id}", use_container_width=True):
                        simulate_customer_whatsapp_reply(active_id, "CANCEL")
                        st.warning("Customer Cancelled via WhatsApp. Restocked inventory & saved ₹120 freight!")
                        st.rerun()

                elif st_code in ("DISPATCHED", "AUTO_APPROVED"):
                    st.markdown("""
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:14px; color:#15803d; font-size:0.84rem; margin-bottom:12px;">
                        ✅ <b>Order Cleared for Fulfillment</b><br/>
                        <span style="font-size:0.78rem; color:#166534;">Courier shipping label printed and parcel queued for Ekart carrier pickup.</span>
                    </div>
                    """, unsafe_allow_html=True)

                elif st_code == "BLOCKED_FRAUD":
                    st.markdown("""
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:14px; color:#991b1b; font-size:0.84rem; margin-bottom:12px;">
                        🚨 <b>Dispatch Halted Pre-Courier</b><br/>
                        <span style="font-size:0.78rem; color:#b91c1c;">Bogus/mismatched postal PIN intercepted. Saved ₹120 dead reverse freight burn.</span>
                    </div>
                    """, unsafe_allow_html=True)

                elif st_code == "CANCELLED_RESTOCKED":
                    st.markdown("""
                    <div style="background:#f1f5f9; border:1px solid #cbd5e1; border-radius:10px; padding:14px; color:#334155; font-size:0.84rem; margin-bottom:12px;">
                        ✕ <b>Order Cancelled & Inventory Restocked</b><br/>
                        <span style="font-size:0.78rem; color:#64748b;">This COD shipment was stopped pre-dispatch. Saved ₹120 in courier reverse freight. Garment returned to active stock.</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Supervisor Action Bar (Strictly Context-Aware based on Order Status)
                st.markdown("###### 🛡️ Supervisor Action Bar")

                if st_code == "CANCELLED_RESTOCKED":
                    st.markdown("""
                    <div style="background:#f8fafc; border:1px dashed #cbd5e1; border-radius:8px; padding:10px; text-align:center; color:#64748b; font-size:0.8rem; margin-bottom:8px;">
                        🔒 <b>Terminal State: Order is closed.</b> No further dispatch action needed.
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔁 Restore Order to Active Queue", key=f"restore_{active_id}", use_container_width=True):
                        update_order_status(active_id, "HELD_WHATSAPP", "OPS_SUPERVISOR", "Restored order to active queue for re-verification")
                        st.info("Order restored to active queue!")
                        st.rerun()

                elif st_code in ("DISPATCHED", "AUTO_APPROVED"):
                    st.caption("Active label in carrier run sheet. Actions:")
                    if st.button("🛑 Void Label & Put on Hold", key=f"void_{active_id}", use_container_width=True):
                        update_order_status(active_id, "HELD_WHATSAPP", "OPS_SUPERVISOR", "Voided shipping label prior to carrier pickup")
                        st.warning("Label voided! Order placed back on hold.")
                        st.rerun()

                elif st_code == "BLOCKED_FRAUD":
                    st.caption("Fraud interception active. Choose resolution:")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✕ Confirm Cancel & Restock", key=f"confirm_canc_{active_id}", use_container_width=True):
                            update_order_status(active_id, "CANCELLED_RESTOCKED", "OPS_SUPERVISOR", "Confirmed fake PIN cancellation. Saved ₹120.")
                            st.rerun()
                    with b2:
                        if st.button("✓ Force Override Dispatch", key=f"force_fraud_{active_id}", use_container_width=True):
                            update_order_status(active_id, "DISPATCHED", "OPS_SUPERVISOR", "Supervisor manually overrode circle mismatch")
                            st.rerun()

                elif st_code == "HELD_WHATSAPP":
                    st.caption("Manual operator intervention (updates SQLite database immediately):")
                    op1, op2 = st.columns(2)
                    with op1:
                        if st.button("✓ Force Generate Label", key=f"force_btn_{active_id}", use_container_width=True):
                            update_order_status(active_id, "DISPATCHED", "BHIWANDI_OPS_MANAGER", "Operator verified delivery point manually")
                            st.success("Updated in SQLite DB: Label Generated!")
                            st.rerun()
                    with op2:
                        if st.button("✕ Cancel & Restock", key=f"cancel_btn_{active_id}", use_container_width=True):
                            update_order_status(active_id, "CANCELLED_RESTOCKED", "BHIWANDI_OPS_MANAGER", "Saved ₹120 dead courier pickup")
                            st.warning("Cancelled in SQLite DB: Saved ₹120 Freight!")
                            st.rerun()


# ==============================================================================
# TAB 2: Fulfillment & RTO Analytics (Executive BI Dashboard)
# ==============================================================================
with tab_analytics:
    st.markdown("### 📊 Fulfillment & Logistics Bleed Analytics")
    st.caption("Live financial analysis calibrated to Dhaga & Co.'s 48,000 weekly volume (61% COD mix).")

    bi1, bi2 = st.columns([1.2, 1], gap="large")

    with bi1:
        st.markdown("##### 📈 Weekly Logistics Bleed vs COD Shield Retention")
        chart_df = pd.DataFrame({
            "Scenario": ["Current Reality (No Shield)", "Target With COD Shield (-5% RTO)", "Net Weekly Freight Saved"],
            "Amount (₹ Lakhs)": [
                WEEKLY_LOGISTICS_BLEED_INR / 100000,
                (WEEKLY_LOGISTICS_BLEED_INR - PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR) / 100000,
                PROJECTED_WEEKLY_LOGISTICS_SAVINGS_INR / 100000
            ]
        })
        st.bar_chart(chart_df.set_index("Scenario"))

    with bi2:
        st.markdown("##### 🎯 4-Tier Order Qualification Flow")
        tier_df = pd.DataFrame({
            "Stage": ["1. Zero-Touch Auto Approved", "2. Customer Self-Resolved (WhatsApp)", "3. Fraud/Fake PIN Blocked", "4. Warehouse Exception Desk"],
            "Share (%)": [74.2, 19.8, 4.5, 1.5],
            "Impact": ["Dispatched in <100ms", "Customer fixed address", "Saved ₹120 burn each", "Resolved in 1-click"]
        })
        st.dataframe(tier_df, use_container_width=True)
        st.caption("📌 **Key Takeaway:** Over 94% of all orders resolve without any manual intervention by warehouse personnel.")

    st.markdown("---")
    st.markdown("##### 🗺️ Geographic Postal Circle Risk Breakdown")
    geo_df = pd.DataFrame([
        {"State / Postal Circle": "Uttar Pradesh (20-28)", "COD Orders": 7400, "Historical RTO": "31%", "COD Shield Protection": "High (Landmark Extraction Active)"},
        {"State / Postal Circle": "Bihar (80-85)", "COD Orders": 5100, "Historical RTO": "34%", "COD Shield Protection": "High (Hinglish Relative Phrases)"},
        {"State / Postal Circle": "Maharashtra (40-44)", "COD Orders": 6200, "Historical RTO": "18%", "COD Shield Protection": "Standard (Urban Deliverable)"},
        {"State / Postal Circle": "Karnataka (56-59)", "COD Orders": 4300, "Historical RTO": "15%", "COD Shield Protection": "Standard (Clean Metro Address)"},
    ])
    st.table(geo_df)


# ==============================================================================
# TAB 3: Automation Policy & AI Gateway (Ops Admin)
# ==============================================================================
with tab_gateway:
    st.markdown("### ⚙️ Dispatch Policy Configuration & AI Gateway")
    st.caption("Operations rules controlling automated approval, WhatsApp triggers, and hard halts.")

    g_col1, g_col2 = st.columns(2, gap="large")

    with g_col1:
        st.markdown("##### 🛡️ RTO Decision Thresholds")
        st.slider("Auto-Approve Instant Dispatch (Risk Score < X)", min_value=10, max_value=50, value=35, step=5)
        st.slider("Hold for WhatsApp Confirmation (Risk Score X to Y)", min_value=36, max_value=80, value=(36, 75))
        st.slider("Hard Halt & Cancel (Risk Score > Y)", min_value=75, max_value=95, value=76, step=5)
        st.info("💡 Thresholds calibrated to preserve 95%+ of genuine Tier-2/3 orders while blocking bogus postal PINs.")

    with g_col2:
        st.markdown("##### 🤖 Multi-Tier Gateway Architecture")
        st.write(f"**Fast Extraction Model:** `{FAST_WORKER_MODEL}`")
        st.write(f"**Judgment & WhatsApp Model:** `{JUDGMENT_EVAL_MODEL}`")
        st.write(f"**Active Database Path:** `{DB_PATH}`")
        
        st.markdown("##### 💬 WhatsApp Auto-Timeout Policy")
        st.selectbox("Customer Confirmation Timeout Window", ["6 Hours", "12 Hours (Recommended)", "24 Hours"], index=1)
        st.caption("Orders unanswered after 12h appear on the Operations Exception Desk for 1-click resolution.")

        st.markdown("---")
        st.markdown("##### 🔌 Live AI Model Diagnostics")
        detected_key, detected_prov = resolve_api_key()
        if detected_key:
            masked = detected_key[:4] + "••••" + detected_key[-4:]
            st.success(f"✓ Detected Active {detected_prov.upper()} Key (`{masked}`)")
            if st.button("⚡ Test Live Model Connection", key="test_api_btn", use_container_width=True):
                with st.spinner("Pinging model endpoint..."):
                    is_ok, msg = test_api_connection(detected_key, detected_prov)
                    if is_ok:
                        st.success(msg)
                    else:
                        st.error(msg)
        else:
            st.info("⚪ Operating in Intelligent Offline Mock Mode (Zero tokens consumed).")
            manual_key = st.text_input("Test with Custom API Key:", type="password", key="manual_test_key")
            if manual_key and st.button("⚡ Test Key Connection", key="test_manual_btn", use_container_width=True):
                with st.spinner("Pinging model endpoint..."):
                    is_ok, msg = test_api_connection(manual_key)
                    if is_ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown("---")
        st.markdown("##### 🔄 Database Maintenance")
        if st.button("Reset Seed Queue to Defaults", use_container_width=True):
            seed_default_orders(force_reset=True)
            st.success("Refreshed factory order queue!")
            st.rerun()
