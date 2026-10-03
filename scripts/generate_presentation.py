"""
Generate professional PPTX presentation deck for Dhaga & Co. COD Shield
FDE Academy Cohort 4 · Mini Project 1 · Group 10
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme colors
    DARK_NAVY = RGBColor(15, 23, 42)      # #0f172a
    ACCENT_RED = RGBColor(239, 68, 68)     # #ef4444
    ACCENT_GREEN = RGBColor(16, 185, 129)  # #10b981
    SLATE_GRAY = RGBColor(71, 85, 105)    # #475569
    CARD_BG = RGBColor(241, 245, 249)      # #f1f5f9
    WHITE = RGBColor(255, 255, 255)

    def add_header(slide, title_text, category_text="DHAGA & CO. · MINI PROJECT 1 · GROUP 10"):
        # Header category
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_RED

        # Main Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = DARK_NAVY

    # --- SLIDE 1: Title Slide ---
    s1 = prs.slides.add_slide(blank_layout)
    
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "DHAGA & CO. ENGAGEMENT · TECH TRACK MINI PROJECT 1"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_RED
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "COD Shield: Pre-Dispatch Address Intelligence & RTO Interception Engine"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = DARK_NAVY
    p1.space_after = Pt(16)

    p2 = tf1.add_paragraph()
    p2.text = "Halting ₹9.13 Lakhs in weekly dead freight across Tier-2/3 India before parcels leave the fulfillment center."
    p2.font.size = Pt(17)
    p2.font.color.rgb = SLATE_GRAY
    p2.space_after = Pt(36)

    p3 = tf1.add_paragraph()
    p3.text = "Group 10: Venkata Sairam Sudheer Mallapureddy · Omita Thakur · Sheikh Habib · Rohit Yadav"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = DARK_NAVY
    
    p4 = tf1.add_paragraph()
    p4.text = "Panel Reviewer: Ruthvik | Presentation Date: Sunday, 4 October 2026 (5:45 PM – 6:00 PM IST)"
    p4.font.size = Pt(12)
    p4.font.color.rgb = SLATE_GRAY

    # --- SLIDE 2: The Problem (Omita, 3 min) ---
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Segment 1: The Problem — Who Loses What Today", "Segment 1 · Speaker: Omita Thakur (3 Min)")

    b2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf2 = b2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = 'The Client\'s Reality (In Faizan\'s Exact Words):'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(8)

    p = tf2.add_paragraph()
    p.text = '"Return to origin on cash on delivery is twenty-six percent. Each one costs us about ₹120 in logistics and burns a delivery slot we could have used."'
    p.font.size = Pt(18)
    p.font.italic = True
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(20)

    p = tf2.add_paragraph()
    p.text = "Ground Truth & Operational Root Cause:"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(8)

    bullets = [
        "Scale & Payment Mix: 48,000 orders/week @ ₹840 AOV. 61% Cash-on-Delivery (29,280 COD orders/week).",
        "Demographic Reality: 64% of customers reside in Tier-2 and Tier-3 towns (Motihari, Deoria, Gopalganj), ordering on patchy mobile connections.",
        "Address Chaos: Addresses lack municipal numbers, typed in Hinglish relative landmarks ('shankar talkies ke peeche', 'shiv mandir road').",
        "Multi-Hop Courier Failures: Delhivery, Shiprocket, and Ekart take 4–7 days. Courier run sheets receive unstructured strings, resulting in immediate Non-Delivery Reports (NDR) and RTO.",
        "Trusted Data Asset: Dhaga's 11-million-row Postgres Orders table is explicitly marked 'Clean and trustworthy'. The baseline truth already exists."
    ]
    for b in bullets:
        bp = tf2.add_paragraph()
        bp.text = f"•  {b}"
        bp.font.size = Pt(14)
        bp.font.color.rgb = SLATE_GRAY
        bp.space_after = Pt(6)

    # --- SLIDE 3: Why It Matters & Economics (Sheikh, 3 min) ---
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Segment 2: Why It Matters — The Hard Cash Bleed", "Segment 2 · Speaker: Sheikh Habib (3 Min)")

    b3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf3 = b3.text_frame
    tf3.word_wrap = True

    p = tf3.paragraphs[0]
    p.text = "The Weekly Bleed Arithmetic (No Estimates, Direct Case Numbers):"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(10)

    stats = [
        "Weekly COD Volume: 48,000 orders × 61% COD = 29,280 orders/week",
        "Weekly COD RTO Orders: 29,280 × 26% RTO = 7,613 failed deliveries every single week",
        "Weekly Logistics Burn: 7,613 RTOs × ₹120 reverse freight = ₹9,13,560 per week (~₹4.75 Crore / year) lost in dead freight",
        "Inventory Drag: Seasonal stock (Dhaga pulls unsold items in 6 weeks) is trapped in transit for 10–14 days round trip, degrading sell-through",
        "Target Metric: Reduce COD RTO from 26% to 21% (a 5 percentage point drop), saving 1,464 parcels/week",
        "Retained Bottom-Line Cash: 1,464 × ₹120 = ₹1,75,680 / week (₹91.3 Lakhs / year retained profit)",
        "AI Infrastructure Cost: ₹1,350 / week (~$16 USD/week) — Delivering an astronomical 130x Net ROI!"
    ]
    for s in stats:
        sp = tf3.add_paragraph()
        sp.text = f"✔  {s}"
        sp.font.size = Pt(14)
        sp.font.color.rgb = SLATE_GRAY
        sp.space_after = Pt(8)

    # --- SLIDE 4: Architecture & Code vs Model (Sudheer, 3 min) ---
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Segment 3: Architecture — The Code vs. Model Line", "Segment 3 · Speaker: Venkata Sairam Sudheer (3 Min)")

    b4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf4 = b4.text_frame
    tf4.word_wrap = True

    p = tf4.paragraphs[0]
    p.text = "Strict Rule: Models earn their place on language & judgment. Math & lookups stay in Python."
    p.font.size = Pt(15)
    p.font.italic = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(14)

    steps = [
        ("Deterministic Code (Python)", "PIN code regex (^[1-9][0-9]{5}$), India Post circle lookup table, keyword matching ('phone pe baat', 'kahi bhi'). Runs in <0.01 ms with 0 tokens."),
        ("Fast Model (Gemini 1.5 Flash, Temp 0.1)", "Extracts messy relative landmarks ('shankar talkies ke peeche'), normalizes spelling drift, and outputs structured Pydantic schema."),
        ("Model + Rule Risk Boundary", "Calculates calibrated 0–100 RTO Risk Score and assigns Tier: LOW (<=35), MEDIUM (36-65), HIGH (>65)."),
        ("Routing Pattern", "Over 65% of orders are LOW risk and get instantly auto-approved. Only flagged ambiguous orders route to the Pro model."),
        ("Evaluator-Optimizer (Gemini 1.5 Pro, Temp 0.3)", "Identifies precise missing attributes and generates warm, culturally respectful Hinglish WhatsApp messages with 1-click confirmation buttons.")
    ]
    for title, desc in steps:
        sp = tf4.add_paragraph()
        sp.text = f"•  {title}: {desc}"
        sp.font.size = Pt(13)
        sp.font.color.rgb = DARK_NAVY
        sp.space_after = Pt(6)

    # --- SLIDE 5: Live Demo & Intentional Failure (Rohit, 6 min) ---
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Segment 4: Live Demo & Intentional Failure Mode", "Segment 4 · Speaker: Rohit Yadav (6 Min)")

    b5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf5 = b5.text_frame
    tf5.word_wrap = True

    p = tf5.paragraphs[0]
    p.text = "Live Demonstration on Real Deployed URL (4 Key Scenarios):"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(12)

    demos = [
        ("Case 1: Clean Metro (Bellandur, BLR)", "Instant Auto-Approval (<100 ms). Standard label generated; 0 Pro tokens consumed."),
        ("Case 2: Hinglish Landmark (Motihari, Bihar)", "'shankar talkies ke peeche, ward 14' -> Landmark preserved on courier label. Low-medium risk; approved for Ekart dispatch."),
        ("Case 3: Missing Premise (Deoria, UP)", "'Dr. Verma clinic ke samne, shiv mandir road' -> Evaluator-Optimizer triggers Hinglish WhatsApp prompt with quick-reply buttons to verify door number."),
        ("Case 4: INTENTIONAL FAILURE CASE (Mandatory Rubric)", "'Plot 24, Civil Lines, Jaipur, Rajasthan - 400001' -> FAILS VISIBLY on screen! Red Banner: Geographic Circle Mismatch (400001 is Mumbai, not Rajasthan). Halts dispatch, saving ₹120 in dead logistics!"),
        ("The Unexpected Failure Solved", "Landmark Premise Paradox: In Tier-2/3 India, 40%+ of homes have no door numbers. Naive parsers reject them; our engine preserves verified landmarks for local delivery boys.")
    ]
    for title, desc in demos:
        dp = tf5.add_paragraph()
        dp.text = f"★  {title}: {desc}"
        dp.font.size = Pt(13)
        dp.font.color.rgb = DARK_NAVY
        dp.space_after = Pt(7)

    # --- SLIDE 6: What We Would Build Next (Sudheer, 2 min) ---
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Segment 5: What We Would Build Next", "Segment 5 · Speaker: Venkata Sairam Sudheer (2 Min)")

    b6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf6 = b6.text_frame
    tf6.word_wrap = True

    p = tf6.paragraphs[0]
    p.text = "Roadmap for Monday Morning (Honest Read of Future Scope):"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(12)

    next_items = [
        ("Unicommerce Webhook Integration", "Direct API middleware: intercept order creation webhooks and hold shipping label printing until address qualification passes."),
        ("Dynamic Carrier Routing", "Evaluate PIN-level performance across Delhivery, Shiprocket, and Ekart to route high-risk Tier-3 PINs to the carrier with highest local delivery completion rates."),
        ("Pre-Dispatch COD-to-Prepaid Conversion", "When high RTO risk is detected, offer ₹50 instant discount via WhatsApp if customer converts to UPI online payment, completely eliminating RTO risk."),
        ("What We Need From Dhaga & Co.", "Access to 6 months of historical courier NDR (Non-Delivery Report) status codes from Delhivery/Ekart to calibrate weights for Tier-3 clusters.")
    ]
    for title, desc in next_items:
        np = tf6.add_paragraph()
        np.text = f"➡  {title}: {desc}"
        np.font.size = Pt(14)
        np.font.color.rgb = DARK_NAVY
        np.space_after = Pt(8)

    # --- SLIDE 7: Handling Boardroom Pushback (All Members, 6 min) ---
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Boardroom Pushback: Anticipating Tough Questions", "Q&A Anchor · All Team Members Speaking (6 Min)")

    b7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf7 = b7.text_frame
    tf7.word_wrap = True

    qa = [
        ("Dev (CTO): '16 engineers, 0 ML engineers. Who runs this on Monday?'", "Answer: Built in pure Python + standard REST APIs. Zero PyTorch, zero CUDA, zero model hosting. A junior backend engineer can maintain this with standard FastAPI / Unicommerce webhooks."),
        ("Faizan: 'What if your model is wrong 1 in 20 times?'", "Answer: We never cancel a customer's order arbitrarily. High-risk orders are held for a polite, automated WhatsApp confirmation. Even if the customer ignores WhatsApp, human CX agents review it. It fails visibly, never silently."),
        ("Ritu (CEO): 'What if RTO is driven by buyer remorse, not addresses?'", "Answer: Our biggest assumption is stated explicitly in the Discovery Note. Pre-dispatch WhatsApp confirmation filters uncommitted impulse buyers before dispatch. If a buyer ignores WhatsApp, holding the parcel saves the ₹120 logistics burn.")
    ]
    for q, a in qa:
        qp = tf7.add_paragraph()
        qp.text = f"❓ {q}"
        qp.font.size = Pt(13)
        qp.font.bold = True
        qp.font.color.rgb = ACCENT_RED
        qp.space_after = Pt(2)
        
        ap = tf7.add_paragraph()
        ap.text = f"   💡 {a}"
        ap.font.size = Pt(12)
        ap.font.color.rgb = DARK_NAVY
        ap.space_after = Pt(10)

    # Output directory
    output_path = "e:/fde_learn/cohort-4-mini-project-1-group-10/dhaga-cod-shield-presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved to: {output_path}")

if __name__ == "__main__":
    create_deck()
