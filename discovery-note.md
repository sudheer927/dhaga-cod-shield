# Phase 1 Discovery Note: Dhaga & Co.

**Date:** 3 October 2026  
**Group:** Group 10 (Cohort 4, Tech Track)  
**Authors:** Venkata Sairam Sudheer Mallapureddy, Omita Thakur, Sheikh Habib, Rohit Yadav  
**Status:** Approved & Finalized (Pre-Commit Baseline)

---

### 1. The Problem in One Sentence (in the Client's Language)
*"More than one in every four cash-on-delivery parcels comes back to Bhiwandi, Gurugram, or Hyderabad uncollected because our courier partners can't decipher where the customer actually lives, burning ₹9.1 lakhs in dead freight every week before a single customer even opens the door."*

---

### 2. Who Owns It Today Inside the Company, and What They Currently Do Instead
* **Owner:** **Faizan, Head of Supply Chain** (with downstream friction landing on Arpita in CX and Neha in Merchandising).
* **What Faizan & Dhaga currently do instead:**
  * When an order is placed on the Android app, the raw customer address string is passed blindly via Unicommerce to logistics partners (Delhivery, Shiprocket, Ekart).
  * No pre-dispatch address sanity check or intent qualification is performed.
  * If a courier cannot locate the destination (e.g. landmark-heavy, missing house number, or inaccurate pin code in Tier-2/3 towns), the courier marks it as "Non-Delivery Report" (NDR) or triggers an automatic Return-to-Origin (RTO).
  * Dhaga absorbs the dead logistics cost, restocks the garment, and burns a delivery slot.

---

### 3. The Evidence from the Case Study That Took Us There
* **Volume & Payment Mix:** Dhaga operates at ₹310 crore GMV run-rate with **48,000 orders/week** (~6,857 orders/day). **61% of all orders are Cash on Delivery (COD)** = **29,280 COD orders/week**.
* **The RTO Spike:** Faizan directly stated: *"Return to origin on cash on delivery is twenty-six percent. Each one costs us about ₹120 in logistics and burns a delivery slot we could have used."*
* **Customer Demographics & Input Habits:** 64% of customers reside in **Tier-2 and Tier-3 cities**, ordering via low-end Android handsets on patchy connectivity. Addresses are entered in colloquial Hinglish, filled with relative landmarks (*"Patanjali dukaan ke samne"*, *"Purana railway phatak, gali 4"*) rather than structured street/door numbers.
* **Courier Reality:** Courier partners (Delhivery, Shiprocket, Ekart) take 4–7 days. Dispatching unverified, poorly structured addresses across multi-hop networks into semi-urban/rural clusters guarantees delivery failures.
* **Clean Data Foundation:** Section 04 confirms the **Orders table (11 million rows in Postgres)** contains full line items, payment mode, address, and status history, marked explicitly as **"Clean and trustworthy"**. The ground truth data already exists to train and evaluate this.

---

### 4. What It Costs Them
The financial damage is direct, recurring, and undisputed on Faizan’s P&L:
* **Weekly COD Orders:** $48{,}000 \times 61\% = 29{,}280\text{ orders/week}$
* **Weekly COD RTO Volume:** $29{,}280 \times 26\% = \mathbf{7{,}612.8\text{ failed orders/week}}$
* **Direct Logistics Burn:** $7{,}613 \times ₹120 = \mathbf{₹9{,}13{,}560\text{ per week}}$ in pure wasted shipping expense!
* **Annualized Cash Drain:** $\approx \mathbf{₹4.75\text{ Crore per year}}$ lost in dead freight alone.
* **Opportunity & Inventory Cost:** 7,613 delivery slots burned every week that could have serviced paying customers. Furthermore, fast-turning seasonal stock (Dhaga pulls inventory unsold in 6 weeks) is trapped in transit for 10–14 days round-trip, degrading sell-through and risking dead stock.

---

### 5. What Success Looks Like, and How to Measure It with Data They Already Hold
* **Primary Target:** Reduce Dhaga’s COD RTO rate from **26% down to 21%** within 90 days of deployment (a 5-percentage-point absolute reduction).
* **Weekly Financial Savings:** Preventing 1,464 RTOs/week yields **₹1,75,680/week in direct logistics savings** ($\approx \mathbf{₹91.3\text{ Lakhs/year}}$ bottom-line cash retained), at an AI inference cost of less than ₹2,000/week (ROI > 45x).
* **Measurement Methodology (Using Existing Data):**
  1. *Historical Benchmark:* Run historical 11M-row Postgres order status logs (`Delivered` vs `RTO`) against the address validation engine to prove that low-confidence addresses correlate with past RTOs.
  2. *Live Telemetry:* Track the `address_quality_score` and `rto_risk_tier` (`LOW`, `MEDIUM`, `HIGH`) at order creation.
  3. *Controlled Rollout:* A/B test pre-dispatch address resolution (automatic normalization for minor issues, automated low-friction WhatsApp prompt for ambiguous addresses) vs. unvalidated control orders across equivalent Tier-2/3 pincodes.

---

### 6. Ranked Shortlist of At Least Four Problems

| Rank | Problem & Owner | The Specific Case | Why It Sits Where It Does |
| :---: | :--- | :--- | :--- |
| **1** | **COD RTO Dead Logistics Bleed**<br>*(Faizan, Head of Supply Chain)* | 26% RTO on 29,280 weekly COD orders burns **₹9.13 Lakhs/week** in direct cash out the door at ₹120/order. Driven by unstructured Tier-2/3 Hinglish addresses. | **Top Pick:** Highest measurable, immediate cash bleed. Postgres Orders table is clean and trusted. Runs as a non-invasive pre-dispatch check requiring 0 ML engineers on staff. |
| **2** | **Cataloguing Sample-to-Live Delay**<br>*(Vivek, Listing Lead)* | 400 new SKUs/week takes 6–9 days from sample to live. Drop calendar slips, losing the critical **Tuesday traffic spike** on a ₹310 Cr business. | **Rank 2:** Massive commercial leverage, but harder to attribute direct lost rupee figures to a slipped Tuesday vs. Faizan's hard ₹9.1L logistics invoice. High operational dependency on photo studio handoffs. |
| **3** | **Unanalyzed Returns "Other" Box**<br>*(Neha, Category Head)* | 31% return rate; 44% land in "Other" free-text (~6,547 returns/week). Neha can only read a few hundred by hand. Most complain about fit and size differences across vendors. | **Rank 3:** Highly informative, but diagnostic rather than preventative. Categorizing why a customer returned a kurti last week doesn't prevent tomorrow's delivery failure unless vendors re-cut patterns and remeasure 14,000 live SKUs. |
| **4** | **Repetitive "Where Is My Order" (WISMO) Tickets**<br>*(Arpita, Head of CX)* | 58% of 9,000 weekly tickets are WISMO (~5,220 tickets). 34 agents copy-paste 4 canned responses with 9-hour first response times. | **Rank 4:** A classic downstream symptom. Customers spam WISMO tickets *because* multi-carrier logistics take 4–7 days and parcels get stuck on incorrect addresses. Fixing the chat doesn't deliver the parcel faster. |

---

### 7. Our Biggest Assumption, and What Evidence Would Prove It Wrong
* **Our Biggest Assumption:** A significant proportion ($\ge 40\%$) of COD RTOs are caused by **impaired courier reachability** (unlocatable addresses, missing landmarks, incorrect pin codes, or unrecognized contact info) that can be corrected or flagged before dispatch, rather than deliberate buyer malice (impulse COD ordering with zero intent to pay).
* **What Evidence Would Prove It Wrong:** 
  * If Faizan’s NDR (Non-Delivery Report) logs from Delhivery, Shiprocket, and Ekart show that >80% of COD RTO reasons are logged as *"Customer rejected at doorstep / Refused to pay"* or *"Buyer unavailable after 3 verified doorstep visits to a clear address"*, rather than *"Address unlocatable / Incomplete address / Wrong phone / Untraceable recipient"*. 
  * *Contingency Pivot:* Even if buyer remorse is higher than address flaws, an intelligent pre-dispatch RTO scoring engine that detects uncommitted buyer patterns and triggers upfront payment micro-incentives (e.g., "Pay ₹50 online now for free shipping") directly protects the same ₹9.1L weekly bleed.
