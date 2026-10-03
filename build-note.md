# Phase 2 Build Note: Dhaga & Co. COD Shield

**Group:** Group 10 (Cohort 4, Tech Track)  
**Authors:** Venkata Sairam Sudheer Mallapureddy, Omita Thakur, Sheikh Habib, Rohit Yadav  
**Target:** Pre-Dispatch Address Intelligence & RTO Interception Engine  

---

### 1. The Code versus Model Table

Every step in our pipeline is deliberately separated into deterministic code or an LLM call. Models earn their place strictly on messy language interpretation and judgment, never on arithmetic, regex, or table lookups.

| Pipeline Step | Execution Mechanism | Technology / Model | Stated Temperature | Rationale (Why This Belongs Here) |
| :--- | :--- | :--- | :---: | :--- |
| **1. PIN Code Format & Sanitization** | **Deterministic Code** | Python Regex `^[1-9][0-9]{5}$` | N/A | An LLM should never be used to count six digits. Runs in <0.01 ms with 100% mathematical precision. |
| **2. Postal Circle Verification** | **Deterministic Code** | India Post Circle 2-Digit Prefix Table | N/A | Lookup table maps postal circles to states (e.g., `40` = Maharashtra, `56` = Karnataka). Prevents geographic hallucinations. |
| **3. High-Risk Phrase Flagging** | **Deterministic Code** | Keyword Pattern Matching | N/A | Regex catches high-friction phrases (*"phone pe baat karna"*, *"kahi bhi de do"*, *"fake"*) for zero token cost. |
| **4. Messy Address Parsing & Normalization** | **Fast Model** | `gemini-1.5-flash` (or `gpt-4o-mini`) | `0.1` | Interprets unstructured Indian free text, extracts relative landmarks (*"shankar talkies ke peeche"*), handles spelling drift across 28 states. |
| **5. RTO Risk Scorer** | **Model + Rules Boundary** | Hybrid Pydantic Scoring Function | `0.1` | Fuses deterministic postal checks with linguistic confidence scores into a calibrated 0–100 risk score and tier. |
| **6. WhatsApp Pre-Dispatch Empathy Optimizer** | **Judgment Model** | `gemini-1.5-pro` (or `gpt-4o`) | `0.3` | Synthesizes warm, culturally respectful Hinglish messages with interactive buttons for Tier-2/3 female buyers. |
| **7. Financial & ROI Calculations** | **Deterministic Code** | Python Floating-Point Math | N/A | Arithmetic for order value, logistics loss prevention (₹120/order), and weekly aggregate P&L. |

---

### 2. Why Each Pattern Is There (and What Breaks Without It)

#### Pattern 1: Prompt Chaining (Parsing $\rightarrow$ Deterministic Verification $\rightarrow$ Risk Scoring)
* **Why it's there:** Isolates the messy entity extraction task from the risk evaluation task.
* **What breaks without it:** When a single prompt attempts to extract address components, validate PIN codes, and score RTO risk simultaneously, the model frequently hallucinates missing landmarks to satisfy the prompt, masks geographic PIN code mismatches, and fails structured Pydantic schema validation on edge cases.

#### Pattern 2: Routing (Tier-Based Decision Routing)
* **Why it's there:** Routes orders based on risk tier (`LOW`, `MEDIUM`, `HIGH`). Low-risk orders (>65% of volume) bypass the heavier judgment model and receive instant automated dispatch approval.
* **What breaks without it:** Without routing, running all 29,280 weekly COD orders through the Pro judgment model would inflate Dhaga's weekly AI compute bill by over 4.5x, adding unnecessary latency to fast-moving warehouse fulfillment lines at Bhiwandi and Gurugram.

#### Pattern 3: Evaluator-Optimizer (Ambiguity Evaluation $\rightarrow$ Tailored WhatsApp Synthesis)
* **Why it's there:** Evaluates what specific attributes make an address undeliverable, then synthesizes a targeted, conversational Hinglish WhatsApp message with 1-click confirmation buttons.
* **What breaks without it:** Sending generic, robotic SMS alerts (*"Your address is incomplete, please update"*) results in <8% customer response rates in Tier-2/3 cities, causing the parcel to either sit in warehouse limbo or get dispatched anyway, burning ₹120.

---

### 3. The Cost Line (Dhaga & Co. Scale Arithmetic)

All calculations use Dhaga’s verified business metrics: **48,000 orders/week**, **61% Cash-on-Delivery** ($29{,}280\text{ COD orders/week}$), **₹120 logistics cost per RTO**, and an exchange rate of ₹84 / USD.

#### Per-Order Run Arithmetic:
* **Fast Model (`gemini-1.5-flash`):**
  * Input: ~350 tokens $\times$ \$0.075 / 1M = \$0.00002625
  * Output: ~120 tokens $\times$ \$0.30 / 1M = \$0.00003600
  * Total Fast Run = \$0.00006225 $\approx$ **₹0.0052 per order**
* **Judgment Model (`gemini-1.5-pro`):**
  * Input: ~500 tokens $\times$ \$1.25 / 1M = \$0.000625
  * Output: ~200 tokens $\times$ \$5.00 / 1M = \$0.001000
  * Total Pro Run = \$0.001625 $\approx$ **₹0.1365 per order**

#### Weekly Scale Arithmetic at Dhaga & Co.:
* **100% of COD Orders Processed by Fast Model:**
  $$29{,}280 \times ₹0.0052 = \mathbf{₹152.26\text{ / week}}$$
* **30% Flagged Orders Routed to Evaluator-Optimizer:**
  $$8{,}784 \times ₹0.1365 = \mathbf{₹1{,}198.02\text{ / week}}$$
* **Total Weekly AI Infrastructure Bill:** $\mathbf{₹1{,}350.28\text{ / week}}$ ($\approx \$16.07\text{ USD/week}$)
* **Logistics Retained (5% Absolute RTO Reduction):**
  $$1{,}464\text{ prevented RTOs} \times ₹120 = \mathbf{₹1{,}75{,}680\text{ / week}}$$
* **Net Weekly Profit to Dhaga & Co.:**
  $$₹1{,}75{,}680 - ₹1{,}350 = \mathbf{+₹1{,}74{,}330\text{ / week}}\quad (\approx \mathbf{₹90.6\text{ Lakhs / year}})$$
* **Return on Investment (ROI):** **130x**

---

### 4. The Thing That Broke That We Did Not Expect

#### The "Landmark Premise Paradox" in Semi-Urban India
When testing our initial parser against colloquial Tier-2/3 Indian addresses (e.g., *"Shankar talkies ke peeche wali gali, ward no 14, Motihari, Bihar"*), the strict postal schema marked the order as `CRITICAL: Missing Premise / Door Number` and attempted to cancel the order.

* **The Reality:** Over 40% of residential structures in Tier-2/3 towns and rural clusters in Bihar, UP, and Rajasthan **do not possess municipal door numbers**. Residents rely entirely on relative landmarks (*"talkies ke peeche"*, *"mandir ke pass"*, *"ward no 14"*) that local delivery agents from Ekart or Delhivery recognize intuitively.
* **The Danger:** A naive Western-style address parser would reject almost half of Dhaga’s legitimate Tier-2/3 customers, destroying sales conversion and growth.
* **How We Resolved It:** We engineered a **relative-landmark preservation layer** in the deterministic engine. If an address lacks a numeric door number but possesses a verified PIN code, a matching state circle, and an actionable landmark, it is not rejected. Instead, it is classified as `ACCEPTABLE_LANDMARK`, the landmark is formatted with high visibility on the courier run sheet, and only a lightweight 1-click confirmation is requested from the buyer.
