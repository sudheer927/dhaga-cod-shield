"""
Dhaga & Co. COD Shield - Enterprise Logistics Database Layer
Production-grade SQLite relational database for order states, shipping labels,
WhatsApp logs, and operator audit trails. 100% Free, Zero-Cost, and Zero-Config.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dhaga_orders.db")


def get_db_connection() -> sqlite3.Connection:
    """Create and return a thread-safe SQLite connection with row dict access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize relational database schema with ACID tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        phone TEXT,
        origin_fc TEXT NOT NULL,
        order_value REAL NOT NULL,
        raw_address TEXT NOT NULL,
        status TEXT NOT NULL, -- 'AUTO_APPROVED', 'HELD_WHATSAPP', 'BLOCKED_FRAUD', 'DISPATCHED', 'CANCELLED_RESTOCKED'
        risk_score INTEGER NOT NULL,
        risk_tier TEXT NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        decision_summary TEXT NOT NULL,
        dead_freight_saved REAL DEFAULT 0.0,
        fast_model TEXT,
        judgment_model TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # 2. Standardized Courier Shipping Labels table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shipping_labels (
        order_id TEXT PRIMARY KEY,
        normalized_address TEXT NOT NULL,
        premise TEXT,
        street TEXT,
        landmark TEXT,
        locality TEXT,
        city TEXT,
        state TEXT,
        pincode TEXT,
        pincode_valid INTEGER DEFAULT 1,
        circle_matched INTEGER DEFAULT 1,
        FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
    )
    """)

    # 3. WhatsApp Interventions & Customer Replies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whatsapp_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        message_body TEXT NOT NULL,
        status TEXT NOT NULL, -- 'SENT', 'DELIVERED', 'CUSTOMER_CONFIRMED', 'AWAITING_REPLY', 'SKIPPED'
        quick_replies TEXT, -- JSON array
        missing_details TEXT, -- JSON array
        sent_at TEXT NOT NULL,
        resolved_at TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
    )
    """)

    # 4. Operator Audit Trail table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL, -- 'SYSTEM_AI_ENGINE', 'BHIWANDI_OPERATOR', 'GURUGRAM_OPERATOR', etc.
        timestamp TEXT NOT NULL,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_default_orders() -> None:
    """Pre-seed database with real Tier-2/3 Indian e-commerce orders if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM orders")
    count = cursor.fetchone()["count"]
    
    if count == 0:
        from core.test_cases import REAL_SHAPED_TEST_CASES
        from core.pipeline import process_dhaga_order
        
        fc_list = ["Bhiwandi FC", "Gurugram FC", "Hyderabad FC"]

        for i, tc in enumerate(REAL_SHAPED_TEST_CASES):
            order_id = tc["id"]
            fc = fc_list[i % len(fc_list)]
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Determine initial mock data based on test case
            res = process_dhaga_order(
                raw_address=tc["raw_address"],
                customer_name=tc["customer_name"],
                order_id=order_id,
                order_value=tc["order_value"],
                api_key=None,
                provider="mock"
            )

            status = "AUTO_APPROVED"
            if res.decision == "HOLD_WHATSAPP_CONFIRMATION":
                status = "HELD_WHATSAPP"
            elif res.decision == "REJECT_UNSERVICEABLE_ADDRESS":
                status = "BLOCKED_FRAUD"

            cursor.execute("""
            INSERT OR REPLACE INTO orders 
            (order_id, customer_name, phone, origin_fc, order_value, raw_address, status, risk_score, risk_tier, decision_summary, dead_freight_saved, fast_model, judgment_model, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                tc["customer_name"],
                tc.get("phone", "9876543210"),
                fc,
                tc["order_value"],
                tc["raw_address"],
                status,
                res.rto_assessment.risk_score,
                res.rto_assessment.risk_tier,
                res.decision_summary,
                res.logistics_loss_prevented_inr,
                res.fast_model,
                res.judgment_model or "None",
                now_iso,
                now_iso
            ))

            # Shipping label
            pa = res.parsed_address
            det = res.deterministic_checks
            cursor.execute("""
            INSERT OR REPLACE INTO shipping_labels
            (order_id, normalized_address, premise, street, landmark, locality, city, state, pincode, pincode_valid, circle_matched)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                pa.normalized_formatted_address,
                pa.house_or_building or "",
                pa.street_or_road or "",
                pa.landmark or "",
                pa.locality_area or "",
                pa.city or "",
                pa.state or "",
                pa.pincode or "",
                1 if det.pincode_valid_format else 0,
                1 if det.pincode_zone_verified else 0
            ))

            # WhatsApp log
            if res.whatsapp_intervention:
                wi = res.whatsapp_intervention
                cursor.execute("""
                INSERT INTO whatsapp_logs
                (order_id, message_body, status, quick_replies, missing_details, sent_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    wi.customer_message_hinglish,
                    "AWAITING_REPLY",
                    json.dumps(wi.quick_reply_suggestions),
                    json.dumps(wi.missing_fields_highlighted),
                    now_iso
                ))

            # Audit trail
            cursor.execute("""
            INSERT INTO audit_log (order_id, action, actor, timestamp, notes)
            VALUES (?, ?, ?, ?, ?)
            """, (
                order_id,
                f"ORDER_INGESTED_{status}",
                "SYSTEM_COD_SHIELD",
                now_iso,
                f"Initial qualification: {res.decision_summary}"
            ))

        conn.commit()

    conn.close()


def get_all_orders(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve orders from SQL DB with optional status filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if status_filter and status_filter != "ALL":
        cursor.execute("SELECT * FROM orders WHERE status = ? ORDER BY updated_at DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY updated_at DESC")

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_order_details(order_id: str) -> Optional[Dict[str, Any]]:
    """Fetch complete order data including shipping label and WhatsApp logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        return None

    data = dict(order_row)

    # Shipping label
    cursor.execute("SELECT * FROM shipping_labels WHERE order_id = ?", (order_id,))
    label_row = cursor.fetchone()
    data["label"] = dict(label_row) if label_row else None

    # WhatsApp log
    cursor.execute("SELECT * FROM whatsapp_logs WHERE order_id = ? ORDER BY id DESC LIMIT 1", (order_id,))
    wa_row = cursor.fetchone()
    if wa_row:
        wa_dict = dict(wa_row)
        try:
            wa_dict["quick_replies"] = json.loads(wa_dict.get("quick_replies") or "[]")
        except Exception:
            wa_dict["quick_replies"] = []
        try:
            wa_dict["missing_details"] = json.loads(wa_dict.get("missing_details") or "[]")
        except Exception:
            wa_dict["missing_details"] = []
        data["whatsapp"] = wa_dict
    else:
        data["whatsapp"] = None

    # Audit history
    cursor.execute("SELECT * FROM audit_log WHERE order_id = ? ORDER BY id DESC", (order_id,))
    data["audit"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return data


def update_order_status(order_id: str, new_status: str, actor: str, notes: str = "") -> bool:
    """Execute ACID status update and append to immutable audit log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update order
    cursor.execute("""
    UPDATE orders 
    SET status = ?, updated_at = ?
    WHERE order_id = ?
    """, (new_status, now_iso, order_id))

    # Append audit trail
    cursor.execute("""
    INSERT INTO audit_log (order_id, action, actor, timestamp, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (order_id, f"STATUS_CHANGE_TO_{new_status}", actor, now_iso, notes))

    # If resolved, update WhatsApp status
    if new_status in ("DISPATCHED", "AUTO_APPROVED"):
        cursor.execute("""
        UPDATE whatsapp_logs 
        SET status = 'CUSTOMER_CONFIRMED', resolved_at = ?
        WHERE order_id = ? AND status = 'AWAITING_REPLY'
        """, (now_iso, order_id))
    elif new_status == "CANCELLED_RESTOCKED":
        cursor.execute("""
        UPDATE whatsapp_logs 
        SET status = 'CUSTOMER_CANCELLED', resolved_at = ?
        WHERE order_id = ? AND status = 'AWAITING_REPLY'
        """, (now_iso, order_id))

    conn.commit()
    conn.close()
    return True


def save_new_order_to_db(order_res: Any, raw_address: str, customer_name: str, phone: str, fc: str = "Bhiwandi FC") -> str:
    """Persist a live pipeline processed order directly into SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = "AUTO_APPROVED"
    if order_res.decision == "HOLD_WHATSAPP_CONFIRMATION":
        status = "HELD_WHATSAPP"
    elif order_res.decision == "REJECT_UNSERVICEABLE_ADDRESS":
        status = "BLOCKED_FRAUD"

    cursor.execute("""
    INSERT OR REPLACE INTO orders 
    (order_id, customer_name, phone, origin_fc, order_value, raw_address, status, risk_score, risk_tier, decision_summary, dead_freight_saved, fast_model, judgment_model, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_res.order_id,
        customer_name,
        phone,
        fc,
        order_res.order_value_inr,
        raw_address,
        status,
        order_res.rto_assessment.risk_score,
        order_res.rto_assessment.risk_tier,
        order_res.decision_summary,
        order_res.logistics_loss_prevented_inr,
        order_res.fast_model,
        order_res.judgment_model or "None",
        now_iso,
        now_iso
    ))

    # Label
    pa = order_res.parsed_address
    det = order_res.deterministic_checks
    cursor.execute("""
    INSERT OR REPLACE INTO shipping_labels
    (order_id, normalized_address, premise, street, landmark, locality, city, state, pincode, pincode_valid, circle_matched)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_res.order_id,
        pa.normalized_formatted_address,
        pa.house_or_building or "",
        pa.street_or_road or "",
        pa.landmark or "",
        pa.locality_area or "",
        pa.city or "",
        pa.state or "",
        pa.pincode or "",
        1 if det.pincode_valid_format else 0,
        1 if det.pincode_zone_verified else 0
    ))

    # WhatsApp
    if order_res.whatsapp_intervention:
        wi = order_res.whatsapp_intervention
        cursor.execute("""
        INSERT INTO whatsapp_logs
        (order_id, message_body, status, quick_replies, missing_details, sent_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            order_res.order_id,
            wi.customer_message_hinglish,
            "AWAITING_REPLY",
            json.dumps(wi.quick_reply_suggestions),
            json.dumps(wi.missing_fields_highlighted),
            now_iso
        ))

    # Audit
    cursor.execute("""
    INSERT INTO audit_log (order_id, action, actor, timestamp, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (
        order_res.order_id,
        f"LIVE_INGEST_{status}",
        "OPERATOR_TEST_CONSOLE",
        now_iso,
        f"Live ingest result: {order_res.decision_summary}"
    ))

    conn.commit()
    conn.close()
    return order_res.order_id


def get_db_metrics() -> Dict[str, Any]:
    """Calculate live database metrics for the executive dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM orders")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as auto_approved FROM orders WHERE status in ('AUTO_APPROVED', 'DISPATCHED')")
    auto_approved = cursor.fetchone()["auto_approved"]

    cursor.execute("SELECT COUNT(*) as held FROM orders WHERE status = 'HELD_WHATSAPP'")
    held = cursor.fetchone()["held"]

    cursor.execute("SELECT COUNT(*) as blocked FROM orders WHERE status in ('BLOCKED_FRAUD', 'CANCELLED_RESTOCKED')")
    blocked = cursor.fetchone()["blocked"]

    cursor.execute("SELECT COALESCE(SUM(dead_freight_saved), 0.0) as freight_saved FROM orders WHERE status in ('BLOCKED_FRAUD', 'CANCELLED_RESTOCKED')")
    freight_saved = cursor.fetchone()["freight_saved"]

    conn.close()

    return {
        "total_orders": total,
        "auto_approved": auto_approved,
        "held_whatsapp": held,
        "blocked_saved": blocked,
        "freight_saved_inr": freight_saved,
        "automation_rate": round((auto_approved / total * 100), 1) if total > 0 else 0.0
    }
