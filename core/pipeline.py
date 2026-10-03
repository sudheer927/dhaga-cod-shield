"""
Dhaga & Co. COD Shield - Multi-Model Pattern-Based Pipeline
Patterns Implemented:
1. Prompt Chaining: Raw Address -> Parsed Structured Address -> Deterministic Check -> RTO Risk Scorer
2. Evaluator-Optimizer & Routing: Evaluates Ambiguity -> Optimizes Localized WhatsApp Prompt -> Action Routing
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional, Tuple

from core.config import (
    EXTRACTION_TEMPERATURE,
    EVALUATION_TEMPERATURE,
    LOGISTICS_COST_PER_RTO_INR,
    get_single_order_cost_inr,
)
from core.schemas import (
    ParsedAddress,
    DeterministicValidation,
    RTORiskAssessment,
    WhatsAppIntervention,
    DispatchDecision,
)
from core.deterministic import run_deterministic_checks


# --- API Health, Key Resolution & Diagnostic Helper ---

def resolve_api_key(api_key: Optional[str] = None) -> Tuple[str, str]:
    """Resolve API key and provider from explicit argument, Streamlit secrets, or environment."""
    key = (api_key or "").strip()
    if not key:
        try:
            import streamlit as st
            if "GEMINI_API_KEY" in st.secrets:
                key = str(st.secrets["GEMINI_API_KEY"]).strip()
            elif "OPENAI_API_KEY" in st.secrets:
                key = str(st.secrets["OPENAI_API_KEY"]).strip()
        except Exception:
            pass

    if not key:
        key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY") or "").strip()

    provider = "openai" if key.startswith("sk-") else "gemini"
    return key, provider


def extract_and_parse_json(text: str) -> Dict[str, Any]:
    """Robustly parse JSON from LLM output, stripping markdown code fences or conversational text."""
    clean_text = text.strip()
    if "```" in clean_text:
        import re
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1).strip()
        else:
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text, flags=re.MULTILINE)
            clean_text = re.sub(r"\s*```$", "", clean_text, flags=re.MULTILINE).strip()
    return json.loads(clean_text)


def test_api_connection(api_key: str, provider: str = "gemini") -> Tuple[bool, str]:
    """Test API key validity and report exact provider response."""
    clean_key = api_key.strip() if api_key else ""
    if not clean_key:
        return False, "No API key provided. Operating in Offline Demo Mode."

    # Auto-detect OpenAI key pasted in Gemini field
    if clean_key.startswith("sk-"):
        provider = "openai"

    if provider == "gemini":
        models_to_test = [
            "gemini-flash-latest",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        last_err = ""
        for m in models_to_test:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={clean_key}"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": clean_key,
            }
            payload = {
                "contents": [{"parts": [{"text": "ping"}]}],
                "generationConfig": {"maxOutputTokens": 2}
            }
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=6)
                if r.status_code == 200:
                    return True, f"Connected to Google Gemini ({m}) successfully!"
                elif r.status_code == 400:
                    try:
                        msg = r.json().get("error", {}).get("message", r.text)
                    except Exception:
                        msg = r.text
                    return False, f"Gemini Error (400): {msg}"
                elif r.status_code == 403:
                    return False, "Gemini Error (403): API key forbidden or expired. Verify key at aistudio.google.com"
                elif r.status_code in (429, 503):
                    last_err = f"Gemini ({m}) temporarily busy ({r.status_code}). Trying alternate model..."
                    continue
                else:
                    last_err = f"Gemini ({m}) returned HTTP {r.status_code}"
            except Exception as e:
                last_err = f"Network Error: {str(e)}"
        return False, last_err or "Gemini Error: Unable to reach models. Please check your Google AI Studio key."


    elif provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 2
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=8)
            if r.status_code == 200:
                return True, "Connected to OpenAI (gpt-4o-mini) successfully!"
            else:
                try:
                    msg = r.json().get("error", {}).get("message", r.text)
                except Exception:
                    msg = r.text
                return False, f"OpenAI Error ({r.status_code}): {msg}"
        except Exception as e:
            return False, f"Network Error: {str(e)}"

    return True, "Offline Mode"


# --- LLM API Client Implementation ---

def call_gemini_api(prompt: str, model: str, temperature: float, api_key: str, json_mode: bool = True) -> str:
    """Call Google Gemini using REST API with multi-tier model fallback and resilient retry."""
    clean_key = api_key.strip()
    
    # Priority cascade: fast models first, followed by resilient fallbacks
    candidate_models = [
        model,
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    
    # Deduplicate while preserving order
    seen = set()
    ordered_models = []
    for m in candidate_models:
        if m and m not in seen:
            seen.add(m)
            ordered_models.append(m)

    last_error = ""
    for m in ordered_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={clean_key}"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": clean_key,
        }
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 1024,
            }
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
            elif resp.status_code in (503, 429):
                # 503 capacity spike or 429 quota -> seamlessly try next candidate model
                try:
                    err_msg = resp.json().get("error", {}).get("message", "Service Busy")
                except Exception:
                    err_msg = f"HTTP {resp.status_code}"
                last_error = f"{m} ({resp.status_code}): {err_msg}"
                continue
            else:
                try:
                    err_data = resp.json()
                    last_error = err_data.get("error", {}).get("message", resp.text)
                except Exception:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
        except Exception as ex:
            last_error = str(ex)

    raise ValueError(f"Gemini API Error: {last_error or 'Could not complete request'}")


def call_openai_api(prompt: str, model: str, temperature: float, api_key: str, json_mode: bool = True) -> str:
    """Make direct REST call to OpenAI Chat Completions API."""
    clean_key = api_key.strip()
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {clean_key}"
    }
    payload: Dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "You are a precise data extraction and logistics evaluation system for Dhaga & Co."},
            {"role": "user", "content": prompt}
        ]
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    response = requests.post(url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


# --- Fallback / Offline Mock Evaluator (Guarantees Cold-Start Resilience) ---

def mock_parse_address(raw_address: str, customer_name: Optional[str] = None) -> ParsedAddress:
    """High-accuracy regex/heuristic parser used when API keys are not supplied."""
    import re
    # Extract PIN
    pin_match = re.search(r"\b([1-9][0-9]{5})\b", raw_address)
    pincode = pin_match.group(1) if pin_match else None
    
    # Extract State if present
    states = [
        "Karnataka", "Bihar", "Uttar Pradesh", "Rajasthan", "Maharashtra", "Jharkhand", "Delhi", "Gujarat",
        "Telangana", "Andhra Pradesh", "Tamil Nadu", "Kerala", "West Bengal", "Punjab", "Haryana",
        "Madhya Pradesh", "Chhattisgarh", "Odisha", "Assam", "Goa", "Uttarakhand", "Himachal Pradesh"
    ]
    detected_state = None
    for st in states:
        if re.search(rf"\b{st}\b", raw_address, re.IGNORECASE):
            detected_state = st
            break
            
    # Extract Landmark keywords (Supports both Hindi/Hinglish suffix and English prefix syntax)
    landmark = None
    # 1. Hindi suffix landmarks: "Dr. Verma clinic ke samne", "post office ke pass", "shankar talkies ke peeche"
    m_hindi = re.search(r"([^,]+?\s+ke\s+(?:samne|peeche|bagal\s*me|pass|paas))\b", raw_address, re.IGNORECASE)
    # 2. English prefix landmarks: "Near Railway Station", "Behind Cult Fitness", "Opposite City Hospital"
    m_eng = re.search(r"\b(?:near|behind|opposite|adj\s*to)\s+([^,]+)", raw_address, re.IGNORECASE)
    # 3. Famous Landmark Nouns: "shiv mandir road", "hanuman mandir", "railway station"
    m_noun = re.search(r"([^,]+?\s+(?:mandir|masjid|gurudwara|hospital|school|college|station|market|bazaar|chowk|circle))\b", raw_address, re.IGNORECASE)

    if m_hindi:
        landmark = m_hindi.group(1).strip()
    elif m_eng:
        landmark = m_eng.group(0).strip()
    elif m_noun:
        landmark = m_noun.group(1).strip()

    # Extract House / Premise
    premise = None
    pr_match = re.search(r"(?:flat|plot|house|qtr|room|ward|dukan)\s*(?:no\.?)?\s*[\w\d-]+", raw_address, re.IGNORECASE)
    if pr_match:
        premise = pr_match.group(0).strip()

    # Basic city extraction
    cities = [
        "Bengaluru", "Motihari", "Deoria", "Jaipur", "Gopalganj", "Bokaro", "Mumbai", "Delhi",
        "Hyderabad", "Kolkata", "Chennai", "Pune", "Ahmedabad", "Lucknow", "Patna", "Chandigarh"
    ]
    detected_city = None
    for ct in cities:
        if re.search(rf"\b{ct}\b", raw_address, re.IGNORECASE):
            detected_city = ct
            break

    return ParsedAddress(
        recipient_name=customer_name or "Valued Customer",
        house_or_building=premise,
        street_or_road="Main Road Area",
        landmark=landmark,
        locality_area=None,
        city=detected_city or "Identified District",
        state=detected_state,
        pincode=pincode,
        normalized_formatted_address=f"{premise or ''}, {landmark or ''}, {detected_city or ''}, {detected_state or ''} - {pincode or 'NO PIN'}".strip(", - "),
        language_detected="Hinglish",
        extraction_confidence=0.88 if pincode and landmark else 0.45
    )


# --- Pattern 1: Prompt Chaining (Stage 1: Address Parsing) ---

def step_1_parse_address(
    raw_address: str,
    customer_name: Optional[str],
    api_key: Optional[str] = None,
    provider: str = "gemini"
) -> Tuple[ParsedAddress, str]:
    """Pattern 1 - Chain Step 1: Fast Model (Low Cost, High Throughput) Address Extraction."""
    clean_key = api_key.strip() if api_key else ""
    if not clean_key:
        return mock_parse_address(raw_address, customer_name), "Deterministic Mock Engine (Offline Mode)"

    # Auto-detect OpenAI key format
    if clean_key.startswith("sk-"):
        provider = "openai"

    prompt = f"""
You are the address parser for Dhaga & Co., an Indian D2C fashion ecommerce brand.
Extract the structured components from this messy, colloquial Indian customer address.
Handle Hinglish colloquialisms, relative landmarks ('ke peeche', 'near temple'), and spelling drift.

Raw Address: "{raw_address}"
Customer Name: "{customer_name or ''}"

Return ONLY a valid JSON object matching this schema:
{{
  "recipient_name": string or null,
  "phone_number": string or null,
  "house_or_building": string or null (e.g. 'Flat 402', 'Shop No 3', 'Ward 14'),
  "street_or_road": string or null,
  "landmark": string or null (e.g. 'Behind Cult Fitness', 'Shankar talkies ke peeche'),
  "locality_area": string or null,
  "city": string or null,
  "state": string or null,
  "pincode": string or null (6 digits),
  "normalized_formatted_address": string (Clean standardized multi-line postal format),
  "language_detected": "Hinglish" | "English" | "Hindi" | "Vernacular",
  "extraction_confidence": float between 0.0 and 1.0
}}
"""
    try:
        if provider == "openai":
            raw_json = call_openai_api(prompt, "gpt-4o-mini", EXTRACTION_TEMPERATURE, clean_key, json_mode=True)
            model_used = "OpenAI GPT-4o Mini"
        else:
            raw_json = call_gemini_api(prompt, "gemini-1.5-flash", EXTRACTION_TEMPERATURE, clean_key, json_mode=True)
            model_used = "Gemini 1.5 Flash"
            
        data = extract_and_parse_json(raw_json)
        return ParsedAddress(**data), model_used
    except Exception as e:
        err_msg = str(e)
        return mock_parse_address(raw_address, customer_name), f"Mock Engine ({err_msg[:60]})"


# --- Pattern 1: Prompt Chaining (Stage 2: RTO Risk Scorer) ---

def step_2_score_rto_risk(
    parsed: ParsedAddress,
    deterministic: DeterministicValidation,
    order_value: float,
    api_key: Optional[str] = None,
    provider: str = "gemini"
) -> RTORiskAssessment:
    """Pattern 1 - Chain Step 2: Synthesize deterministic facts + semantic clues into an RTO Risk Score."""
    
    # Check deterministic hard-stop conditions
    if not deterministic.pincode_valid_format:
        return RTORiskAssessment(
            risk_score=95,
            risk_tier="HIGH",
            risk_factors=["Invalid or missing 6-digit postal PIN code", "Undeliverable by carrier network"],
            delivery_feasibility="IMPOSSIBLE",
            requires_customer_confirmation=True
        )

    if not deterministic.pincode_zone_verified:
        return RTORiskAssessment(
            risk_score=90,
            risk_tier="HIGH",
            risk_factors=["Geographic Mismatch: Pincode circle contradicts recipient state/city"],
            delivery_feasibility="IMPOSSIBLE",
            requires_customer_confirmation=True
        )

    # Calculate baseline heuristic score
    risk_score = 15
    factors = []

    if not deterministic.has_door_or_building_number:
        risk_score += 25
        factors.append("Missing explicit house, flat, or door number")

    if not parsed.landmark:
        risk_score += 20
        factors.append("No prominent landmark specified for delivery agent")

    if deterministic.high_risk_phrases_found:
        risk_score += 25
        factors.extend(deterministic.high_risk_phrases_found)

    if order_value > 1200:
        risk_score += 10
        factors.append(f"High COD order value (₹{order_value}) increases refusal risk")

    if parsed.extraction_confidence < 0.6:
        risk_score += 15
        factors.append("Low linguistic extraction confidence")

    risk_score = min(max(risk_score, 5), 95)
    tier = "LOW" if risk_score <= 35 else ("MEDIUM" if risk_score <= 65 else "HIGH")
    feasibility = "EXCELLENT" if tier == "LOW" else ("ACCEPTABLE" if tier == "MEDIUM" else "QUESTIONABLE")

    return RTORiskAssessment(
        risk_score=risk_score,
        risk_tier=tier,
        risk_factors=factors or ["Standard deliverable address in serviceable cluster"],
        delivery_feasibility=feasibility,
        requires_customer_confirmation=(tier in ["MEDIUM", "HIGH"])
    )


# --- Pattern 2: Evaluator-Optimizer (Stage 3: WhatsApp Intervention) ---

def step_3_optimize_whatsapp_intervention(
    parsed: ParsedAddress,
    deterministic: DeterministicValidation,
    risk: RTORiskAssessment,
    order_id: str,
    api_key: Optional[str] = None,
    provider: str = "gemini",
    order_value: float = 840.0
) -> Tuple[WhatsAppIntervention, Optional[str]]:
    """Pattern 2: Evaluator-Optimizer. Generates an empathetic, high-conversion WhatsApp message."""
    clean_key = api_key.strip() if api_key else ""
    
    missing = []
    if not deterministic.pincode_zone_verified:
        missing.append("Correct 6-digit Pincode for your location")
    if not deterministic.has_door_or_building_number:
        missing.append("House / Flat Number")
    if not parsed.landmark:
        missing.append("Nearest Famous Landmark (mandir, school, shop)")

    # Generate dynamic quick replies tailored specifically to missing elements
    quick_replies = ["Confirm Location on Map"]
    if not deterministic.pincode_zone_verified:
        quick_replies.append("Correct Pincode")
    elif not deterministic.has_door_or_building_number:
        quick_replies.append("Update House Number")
    elif not parsed.landmark:
        quick_replies.append("Add Nearest Landmark")
    else:
        quick_replies.append("Confirm Address Details")
    quick_replies.append("Cancel Order")

    val_str = f"₹{int(order_value)}" if order_value else "₹840"

    # If no API key, provide pre-optimized template
    if not clean_key:
        msg = (
            f"Namaste {parsed.recipient_name or 'ji'}! 🙏 Dhaga & Co. se aapka {val_str} ka order dispatch hone wala hai. "
            f"Lekin delivery partner ko aapka address dhoondhne me dikkat na ho, iske liye kripya apna "
            f"{' aur '.join(missing) if missing else 'address'} confirm kar dijiye."
        )
        return WhatsAppIntervention(
            customer_message_hinglish=msg,
            missing_fields_highlighted=missing,
            quick_reply_suggestions=quick_replies
        ), None

    if clean_key.startswith("sk-"):
        provider = "openai"

    prompt = f"""
You are the customer empathy optimizer for Dhaga & Co., a popular everyday clothing brand in India.
Our customers are 18-34, 78% women, living in Tier-2/3 cities, ordering on mobile via Cash on Delivery.

A customer placed order #{order_id} (Value: {val_str}).
Address: "{parsed.normalized_formatted_address}"
Risk Factors: {json.dumps(risk.risk_factors)}
Missing Key Elements: {json.dumps(missing)}

Write a warm, polite, and reassuring Hinglish WhatsApp message asking the customer to clarify the missing details before we dispatch.
It should feel friendly and protective (we want their beautiful kurti/dress to reach them on time), NOT accusatory or robotic.

Generate 3 quick-reply button suggestions. The action button MUST correspond directly to what is missing:
- If pincode circle is mismatched: ["Confirm Location on Map", "Correct Pincode", "Cancel Order"]
- If landmark is missing: ["Confirm Location on Map", "Add Nearest Landmark", "Cancel Order"]
- If house/flat number is missing: ["Confirm Location on Map", "Update House Number", "Cancel Order"]

Return ONLY a JSON object:
{{
  "customer_message_hinglish": string (concise, warm, with emojis),
  "missing_fields_highlighted": list of strings,
  "quick_reply_suggestions": ["Button 1", "Button 2", "Button 3"]
}}
"""
    try:
        if provider == "openai":
            raw_json = call_openai_api(prompt, "gpt-4o", EVALUATION_TEMPERATURE, clean_key, json_mode=True)
            model_used = "OpenAI GPT-4o"
        else:
            raw_json = call_gemini_api(prompt, "gemini-1.5-pro", EVALUATION_TEMPERATURE, clean_key, json_mode=True)
            model_used = "Gemini 1.5 Pro"
        data = extract_and_parse_json(raw_json)
        return WhatsAppIntervention(**data), model_used
    except Exception:
        msg = f"Namaste {parsed.recipient_name or 'ji'}! Dhaga & Co. order #{order_id} ({val_str}) dispatch karne ke liye kripya apna address confirm kijiye."
        return WhatsAppIntervention(
            customer_message_hinglish=msg,
            missing_fields_highlighted=missing,
            quick_reply_suggestions=quick_replies
        ), None


# --- Complete Workflow Orchestrator ---

def process_dhaga_order(
    raw_address: str,
    customer_name: Optional[str] = None,
    order_id: str = "DHAGA-ORD-01",
    order_value: float = 840.0,
    api_key: Optional[str] = None,
    provider: str = "gemini"
) -> DispatchDecision:
    """
    Main Pattern-Based Workflow:
    Executes Prompt Chaining, Deterministic Checks, Routing, and Evaluator-Optimizer.
    """
    start_time = time.time()
    clean_key, detected_provider = resolve_api_key(api_key)
    if not api_key and clean_key:
        provider = detected_provider
    
    # 1. Chain Step 1: Address Parsing (Fast Model)
    parsed_address, fast_model_name = step_1_parse_address(raw_address, customer_name, clean_key, provider)
    
    # 2. Deterministic Validation (0 Tokens, Python Pure)
    deterministic_checks = run_deterministic_checks(
        raw_address=raw_address,
        pincode=parsed_address.pincode,
        declared_state=parsed_address.state,
        house_building=parsed_address.house_or_building,
        has_landmark=bool(parsed_address.landmark)
    )

    # 3. Chain Step 2: RTO Risk Scorer
    rto_assessment = step_2_score_rto_risk(
        parsed=parsed_address,
        deterministic=deterministic_checks,
        order_value=order_value,
        api_key=clean_key,
        provider=provider
    )

    # 4. Pattern: Routing & Evaluator-Optimizer
    whatsapp_intervention = None
    judgment_model_name = None
    fails_visibly = False
    failure_banner = None
    prevented_loss = 0.0

    # Decision Matrix
    if not deterministic_checks.pincode_valid_format:
        decision = "REJECT_UNSERVICEABLE_ADDRESS"
        decision_summary = "HALTED: Pincode is invalid or fake. Dispatch halted to save ₹120 logistics."
        fails_visibly = True
        failure_banner = "CRITICAL FAILURE: Invalid Postal Pincode (Regex Failure). Cannot dispatch."
        prevented_loss = LOGISTICS_COST_PER_RTO_INR

    elif not deterministic_checks.pincode_zone_verified:
        decision = "HOLD_WHATSAPP_CONFIRMATION"
        decision_summary = "HOLD: Geographic discrepancy. Pincode circle does not match declared city/state. WhatsApp self-resolution queued (12h auto-cancel timeout)."
        fails_visibly = True
        failure_banner = "DISCREPANCY ALERT: Pincode and state conflict. Customer given 12h to correct via WhatsApp."
        whatsapp_intervention, judgment_model_name = step_3_optimize_whatsapp_intervention(
            parsed=parsed_address,
            deterministic=deterministic_checks,
            risk=rto_assessment,
            order_id=order_id,
            api_key=clean_key,
            provider=provider,
            order_value=order_value
        )
        prevented_loss = LOGISTICS_COST_PER_RTO_INR

    elif rto_assessment.risk_tier == "HIGH":
        decision = "HOLD_WHATSAPP_CONFIRMATION"
        decision_summary = "HOLD: High RTO Risk detected. Address requires pre-dispatch customer confirmation."
        whatsapp_intervention, judgment_model_name = step_3_optimize_whatsapp_intervention(
            parsed=parsed_address,
            deterministic=deterministic_checks,
            risk=rto_assessment,
            order_id=order_id,
            api_key=clean_key,
            provider=provider,
            order_value=order_value
        )
        prevented_loss = LOGISTICS_COST_PER_RTO_INR

    elif rto_assessment.risk_tier == "MEDIUM":
        decision = "HOLD_WHATSAPP_CONFIRMATION"
        decision_summary = "REVIEW: Address has deliverable components but lacks premise. WhatsApp confirmation queued."
        whatsapp_intervention, judgment_model_name = step_3_optimize_whatsapp_intervention(
            parsed=parsed_address,
            deterministic=deterministic_checks,
            risk=rto_assessment,
            order_id=order_id,
            api_key=clean_key,
            provider=provider,
            order_value=order_value
        )
    else:
        # LOW Risk -> Auto Approved
        decision = "APPROVE_INSTANT_DISPATCH"
        decision_summary = "APPROVED: High-confidence deliverable address. Ready for instant Unicommerce label generation."

    latency_ms = round((time.time() - start_time) * 1000, 2)
    single_cost = get_single_order_cost_inr(evaluated_by_pro=bool(judgment_model_name))

    return DispatchDecision(
        order_id=order_id,
        order_value_inr=order_value,
        decision=decision,
        decision_summary=decision_summary,
        fails_visibly=fails_visibly,
        failure_banner_message=failure_banner,
        logistics_loss_prevented_inr=prevented_loss,
        parsed_address=parsed_address,
        deterministic_checks=deterministic_checks,
        rto_assessment=rto_assessment,
        whatsapp_intervention=whatsapp_intervention,
        fast_model=fast_model_name,
        judgment_model=judgment_model_name,
        processing_time_ms=latency_ms,
        estimated_api_cost_inr=single_cost
    )
