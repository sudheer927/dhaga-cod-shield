# 🛡️ Dhaga & Co. — COD RTO Shield
### Pre-Dispatch Address Intelligence & RTO Interception Control Tower
**FDE Academy Cohort 4 · Mini Project 1 (Tech Track) · Group 10**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://github.com/sudheer927/dhaga-cod-shield)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 📌 1. What It Does

Dhaga & Co. operates at a ₹310 crore GMV run-rate with **48,000 orders/week**, where **61% of all orders are Cash on Delivery (COD)**. 

Every single week, **26% of COD parcels return to origin (RTO)** because couriers (Delhivery, Ekart, Shiprocket) cannot locate colloquial, landmark-heavy addresses entered by Tier-2/3 mobile shoppers on low-end handsets. At ₹120 in dead logistics per failed delivery, Dhaga burns **₹9.13 Lakhs every week (~₹4.75 Crore/year)** in pure cash waste before a customer ever opens the door.

**Dhaga COD Shield** is an automated, pre-dispatch intelligence engine that:
1. **Parses & Normalizes Messy Hinglish Addresses:** Extracts relative landmarks (*"shankar talkies ke peeche"*), villages, and wards into clean courier labels.
2. **Executes Deterministic Postal Verification:** Validates 6-digit PIN format and cross-references India Post postal circle circles against declared states in <0.01 ms with zero LLM tokens.
3. **Predicts RTO Risk (0–100):** Classifies orders into `LOW`, `MEDIUM`, or `HIGH` risk before physical dispatch.
4. **Optimizes Customer Pre-Dispatch Intervention:** Deploys an Evaluator-Optimizer to generate localized, empathetic Hinglish WhatsApp messages with 1-click confirmation buttons for ambiguous orders.
5. **Halts Fraudulent / Unserviceable Orders:** Prevents burning ₹120 in reverse freight by holding unresolvable orders before generating shipping labels on Unicommerce.

---

## ⚡ 2. Cold Start in Five Minutes (How to Run Locally)

Any stranger can clone this repository and run the working application in under 5 minutes:

### Step 1: Clone the Repository
```bash
git clone https://github.com/sudheer927/dhaga-cod-shield.git
cd dhaga-cod-shield
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Launch the Streamlit Control Tower
```bash
streamlit run app.py
```
*The app will automatically open in your default browser at `http://localhost:8501`.*

> [!NOTE]
> **No API Key Required to Test:** The application features a built-in **Offline Intelligent Mock Engine** with realistic Dhaga & Co. test cases pre-loaded. If you have a `GEMINI_API_KEY` or `OPENAI_API_KEY`, you can enter it in the sidebar to activate live LLM inference.

---

## 📥 3. What It Expects (Inputs)

The engine accepts raw order payloads directly from Dhaga's Postgres Orders table or checkout webhook:

| Input Field | Type | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | String | `DHAGA-1002` | Unique order identifier |
| `order_value` | Float | `840.0` | Cart total in INR (Dhaga average is ₹840) |
| `customer_name` | String | `Rameshwar Singh` | Recipient name |
| `raw_address` | String | *"shankar talkies ke peeche, ward 14, motihari 845401"* | Unstructured, free-text address entered on mobile |

---

## 🚨 4. What It Does When Something Goes Wrong (Fails Visibly)

Silent hallucinations and quiet failures destroy trust. In accordance with the project rubric, **COD Shield fails visibly**:

1. **Invalid PIN Code Format:** If a customer enters `000000` or a 5-digit PIN, the deterministic engine halts dispatch with a red alert banner: `CRITICAL FAILURE: Invalid Postal Pincode`. 0 LLM tokens are consumed.
2. **Geographic Circle Mismatch:** If a customer inputs *"Plot 24, Civil Lines, Jaipur, Rajasthan"* with a Mumbai PIN (`400001`), the engine flags: `CRITICAL FAILURE: Geographic Postal Mismatch: Pincode 400001 belongs to Maharashtra, but order specifies Rajasthan`. The dispatch is held, saving ₹120.
3. **Ambiguous Landmark / Missing House Number:** If an address has no house number and vague landmarks, the order is routed to the Evaluator-Optimizer to send a polite WhatsApp clarification prompt.
4. **API Provider Outage:** If the LLM provider experiences a timeout or quota error, the pipeline catches the exception and falls back to deterministic rule scoring without crashing.

---

## 🏗️ 5. Technical Architecture & Ground Rules

### The Code versus Model Boundary
- **Deterministic Code (Python):** PIN regex validation, Indian postal circle database lookups, high-risk phrase search, financial arithmetic, and threshold gating.
- **Fast Model (`gemini-1.5-flash` / `gpt-4o-mini`, Temp `0.1`):** High-throughput address normalization, landmark extraction, language detection.
- **Judgment Model (`gemini-1.5-pro` / `gpt-4o`, Temp `0.3`):** High-reasoning evaluation of delivery feasibility and localized Hinglish WhatsApp synthesis.

### Workflow Patterns Implemented
1. **Prompt Chaining:** Separates address parsing from risk classification to prevent landmark hallucination.
2. **Routing:** Fast-tracks low-risk orders (>65%) for instant label printing; routes ambiguous orders to the optimizer.
3. **Evaluator-Optimizer:** Evaluates exact missing attributes and optimizes customer-facing conversational copy.

### Business & Cost Arithmetic (Dhaga Weekly Scale)
* **Weekly COD Orders:** 29,280 orders/week
* **Fast Model Compute (100% orders):** ₹152.26 / week
* **Judgment Model Compute (30% flagged orders):** ₹1,198.02 / week
* **Total Weekly AI Bill:** **₹1,350.28 / week** (~$16 USD)
* **Weekly Logistics Saved (5% RTO reduction):** **₹1,75,680 / week** (1,464 parcels $\times$ ₹120)
* **Net Profit to Dhaga:** **+₹1,74,330 / week (~₹90.6 Lakhs/year)**
* **Return on Investment (ROI):** **130x**

---

## 📁 6. Repository Structure

```
dhaga-cod-shield/
├── README.md               # 5-minute cold start guide and architecture
├── discovery-note.md       # Phase 1 Discovery Note (dated 3 Oct 2026, pre-commit)
├── build-note.md           # Phase 2 Build Note (Code vs Model table, cost line, failure mode)
├── requirements.txt        # Minimal Python dependencies
├── app.py                  # Full interactive Streamlit control tower
└── core/
    ├── __init__.py
    ├── config.py           # Dhaga business constants, pricing models, temperatures
    ├── schemas.py          # Pydantic structured schemas with validation
    ├── deterministic.py    # Regex, postal circle tables, keyword matching
    ├── pipeline.py         # Multi-model workflow (Chaining, Routing, Evaluator-Optimizer)
    └── test_cases.py       # Real-shaped Indian e-commerce test dataset
```

---

## 👥 7. Team Members & Contributions (Group 10)

Presented live to **Ruthvik** on **Sunday, 4 October 2026 (5:45 PM – 6:00 PM IST)**:

1. **Venkata Sairam Sudheer Mallapureddy** — Problem discovery, pipeline architecture & code vs. model boundary, GitHub repository management.
2. **Omita Thakur** — Presentation Segment: *The Problem & Client Ground Truth* (Slides 1–4).
3. **Sheikh Habib** — Presentation Segment: *Why It Matters & Economics* (Slides 5–7).
4. **Rohit Yadav** — Presentation Segment: *Live Demo & Intentional Failure Case* (Slides 8–10).

---

## 📄 License
This project is licensed under the MIT License.
