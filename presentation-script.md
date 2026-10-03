# 🎤 Dhaga & Co. — Group 10 Presentation Script & Speaker Notes

**Event:** FDE Academy Cohort 4 · Mini Project 1 (Tech Track)  
**Slot:** Sunday, 4 October 2026 | 5:45 PM – 6:00 PM IST (15–20 Minutes total)  
**Reviewer / Panelist:** Ruthvik  
**Presentation File:** [`dhaga-cod-shield-presentation.pptx`](file:///e:/fde_learn/cohort-4-mini-project-1-group-10/dhaga-cod-shield-presentation.pptx)  

---

### Speaker Assignment & Time Breakdown

| Segment | Allocated Time | Speaker | Topic & Mandate |
| :--- | :---: | :--- | :--- |
| **Segment 1: The Problem** | 3 min | **Omita Thakur** | Name it in their language; cite case study evidence; define who loses what. |
| **Segment 2: Why It Matters** | 3 min | **Sheikh Habib** | The weekly P&L bleed arithmetic (₹9.13L/wk); savings targets; 130x ROI. |
| **Segment 3: Architecture** | 3 min | **Venkata Sairam Sudheer** | The Code vs. Model Line; Prompt Chaining, Routing, and Evaluator-Optimizer. |
| **Segment 4: Live Demo** | 6 min | **Rohit Yadav** | Drive live deployed MVP; show real cases; **demonstrate intentional failure mode**. |
| **Segment 5: What Next & Q&A**| 5 min | **All Members** | Roadmap for Monday morning; handle pushback from Dev, Faizan, and Ritu. |

---

## 🎙️ Segment 1: The Problem (3 Minutes)
**Speaker:** Omita Thakur  
**Slide:** Slide 2

> *"Good evening Ruthvik and the panel. If you sit inside Dhaga & Co. for your first week, you hear eight different people complaining about eight different things.*
>
> *Ritu says retention is bad. Vivek says drops slip. But when you sit with Faizan, Head of Supply Chain, you find the single biggest cash bleed in the entire company.*
>
> *In Faizan’s own words: 'Return to origin on cash on delivery is twenty-six percent. Each one costs us about ₹120 in logistics and burns a delivery slot we could have used.'*
>
> *Let’s look at why this happens. Dhaga is doing 48,000 orders a week at an ₹840 average basket size. 61% of all orders are Cash on Delivery—that’s 29,280 COD orders every single week.*
>
> *64% of our customers live in Tier-2 and Tier-3 towns like Motihari, Deoria, and Gopalganj. They order on low-end Android handsets with patchy networks. They don’t have municipal door numbers or postal street signs. They write addresses in colloquial Hinglish filled with relative landmarks: 'shankar talkies ke peeche', 'shiv mandir ke pass, phone pe baat kar lena'.*
>
> *When that raw string gets passed blindly to Delhivery or Ekart, the delivery boy cannot find the door. The order is tagged as a Non-Delivery Report, returned to origin, and Dhaga burns ₹120 in dead freight.*
>
> *Dhaga has 11 million rows of clean, trustworthy order data in Postgres. The data exists. The problem is clear: we are dispatching parcels blind."*

---

## 🎙️ Segment 2: Why It Matters & Economics (3 Minutes)
**Speaker:** Sheikh Habib  
**Slide:** Slide 3

> *"Thank you, Omita. Let’s talk about the hard rupee cost on Faizan’s P&L.*
>
> *At 29,280 COD orders a week and a 26% RTO rate, Dhaga has 7,613 failed deliveries every single week. At ₹120 in courier fees per RTO, Dhaga is literally burning ₹9,13,560 every week—over ₹4.75 Crore a year—in pure dead logistics.*
>
> *And it’s worse than just the shipping bill. Dhaga pulls unsold catalogue items after six weeks. When a parcel takes 10 to 14 days round trip in transit, that seasonal dress degrades in sell-through and ends up being written off.*
>
> *Our goal is not an abstract percentage. We set a realistic target of reducing COD RTO by just 5 percentage points—from 26% down to 21% within 90 days.*
>
> *What does that do? It saves 1,464 orders from returning every week. That retains ₹1,75,680 in hard cash every week—over ₹91.3 Lakhs a year directly back into Dhaga’s EBITDA.*
>
> *And how much does the AI cost to run this? At Dhaga's full scale, our multi-model pipeline costs ₹1,350 per week (~$16 USD). That is a net weekly profit of +₹1.74 Lakhs, or an ROI of 130x. Now Sudheer will show you how we engineered this to run with zero ML engineers on staff."*

---

## 🎙️ Segment 3: Technical Judgment & Architecture (3 Minutes)
**Speaker:** Venkata Sairam Sudheer Mallapureddy  
**Slide:** Slide 4

> *"Thanks, Sheikh. When looking at Dev’s constraints as CTO, Dhaga has 16 engineers and zero ML engineers. Whatever we build has to run on Monday morning without an ML research team.*
>
> *To achieve this, we drew a strict Code versus Model boundary:*
>
> *Rule 1: Models earn their place on messy language interpretation and human judgment. Math, regular expressions, and database lookups stay in pure Python.*
>
> *Step 1 is deterministic: Python regex `^[1-9][0-9]{5}$` validates the 6-digit PIN code. We built an offline India Post circle lookup table that maps 2-digit prefixes to states in <0.01 ms with zero tokens.*
>
> *Step 2 is our Fast Model (Gemini 1.5 Flash at temperature 0.1): It parses colloquial Hinglish, separates relative landmarks from door numbers, and outputs a validated Pydantic schema.*
>
> *Step 3 is our Routing Pattern: Over 65% of orders are clean, low-risk orders. They get instant automated approval and never touch our heavier model, keeping Dhaga's weekly compute bill under ₹1,400.*
>
> *Step 4 is our Evaluator-Optimizer (Gemini 1.5 Pro at temperature 0.3): When an address is ambiguous or missing a premise, it evaluates what is missing and synthesizes an empathetic, culturally respectful Hinglish WhatsApp message with 1-click confirmation buttons.*
>
> *Now Rohit will drive the deployed system live."*

---

## 🎙️ Segment 4: Live Demo & Intentional Failure Case (6 Minutes)
**Speaker:** Rohit Yadav  
**Slide:** Slide 5 & Live Browser Demo

> *(Switch to the live browser tab at `http://localhost:8501` or deployed URL)*
>
> *"Thank you, Sudheer. Let’s look at the live COD Shield Control Tower in action.*
>
> **Demo 1 (Clean Urban Order):**
> *Let’s start with a standard metro order in Bellandur, Bengaluru. When we qualify this order, the deterministic engine validates the 560103 PIN code, the Fast Model structures the apartment and street, and the risk score is 15 (LOW). Result: Instant Auto-Approved for Unicommerce label generation in under 100 milliseconds.*
>
> **Demo 2 (Real-Shaped Hinglish Landmark):**
> *Now let’s look at how real Tier-2/3 India orders: 'shankar talkies ke peeche wali gali, ward no 14, Motihari, Bihar 845401'. Notice that there is no building name or door plate. Our engine normalizes the address, preserves the 'Shankar talkies ke peeche' landmark on the courier run sheet, and approves it for delivery.*
>
> **Demo 3 (INTENTIONAL FAILURE CASE — Mandatory Rubric):**
> *A demo with no failure case is a demo nobody has tested. Watch what happens here:*
> *A customer inputs: 'Plot 24, Civil Lines, Jaipur, Rajasthan - 400001'.*
> *Notice what happened! The system does not hallucinate or silently guess. It FAILS VISIBLY with a red banner:*
> *'CRITICAL FAILURE: Geographic Postal Mismatch: Pincode 400001 belongs to Maharashtra, but order specifies Rajasthan.'*
> *The dispatch is halted immediately. We just prevented a guaranteed RTO and saved Dhaga ₹120 before the box was packed.*
>
> **Demo 4 (Evaluator-Optimizer WhatsApp Intervention):**
> *In Case 3 ('Dr. Verma clinic ke samne, shiv mandir road, Deoria'), there are conflicting landmarks and no house number. The Evaluator-Optimizer generates a warm Hinglish WhatsApp prompt on screen with 1-click buttons: 'Namaste! Delivery partner ko address dhoondhne me dikkat na ho, kripya apna house number confirm kijiye.'*
>
> *Let’s also run our Batch Simulation tab to show 7 real Dhaga orders evaluated simultaneously, showing aggregate logistics loss prevented and sub-rupee API costs."*

---

## 🎙️ Segment 5: What We Would Build Next & Boardroom Q&A (5 Minutes)
**Speaker:** All Members  
**Slide:** Slides 6 & 7

> **Sudheer:**
> *"To wrap up, here is an honest read of what we did not build, and what we would do next on Monday:*
> 1. *Direct Unicommerce Webhook Integration: Intercept order webhooks at the warehouse level so hold/dispatch tags are applied automatically without human intervention.*
> 2. *Dynamic Carrier Routing: Route high-risk Tier-3 PIN codes to whichever courier—Delhivery, Ekart, or Shiprocket—has the highest first-attempt delivery completion in that specific postal circle.*
> 3. *Pre-Dispatch UPI Conversion: Offer an instant ₹50 discount via WhatsApp if a high-risk COD buyer converts to prepaid UPI before dispatch, eliminating 100% of RTO risk.*
>
> *We are now open for questions from the panel."*

---

### Expected Questions & Tactical Responses

* **If Dev (CTO) asks:** *"Sixteen engineers, none of them an ML engineer. Who runs this on Monday?"*
  * **Sudheer's Answer:** *"This is built in standard Python with Pydantic and REST APIs. There is zero local model hosting, zero PyTorch, and zero CUDA. Any backend engineer comfortable with a standard API can maintain this in under an hour."*

* **If Faizan asks:** *"What if your model is wrong 1 in 20 times?"*
  * **Sheikh's Answer:** *"We never cancel an order arbitrarily. An address that has doubts is routed to WhatsApp confirmation. If the customer confirms, it ships. It fails visibly, never silently."*

* **If Ritu asks:** *"What if people just don't have cash when the courier arrives?"*
  * **Omita's Answer:** *"That is why our WhatsApp confirmation requires active buyer engagement before dispatch. Uncommitted impulse buyers who ignore the WhatsApp message are held before we burn the ₹120 courier fee."*
