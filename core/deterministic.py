"""
Dhaga & Co. COD Shield - Deterministic Verification Engine
Rules: Arithmetic, comparisons, regular expressions, and postal database lookup.
LLMs earn their place on language and judgment; math and lookup belong in Python.
"""

import re
from typing import Dict, List, Optional, Tuple
from core.schemas import DeterministicValidation

# Indian Postal Circle Mapping (First 2 digits of 6-digit PIN code)
POSTAL_CIRCLE_PREFIXES: Dict[str, List[str]] = {
    "11": ["Delhi"],
    "12": ["Haryana"],
    "13": ["Haryana"],
    "14": ["Punjab"],
    "15": ["Punjab"],
    "16": ["Chandigarh", "Punjab", "Haryana"],
    "17": ["Himachal Pradesh"],
    "18": ["Jammu and Kashmir", "Ladakh"],
    "19": ["Jammu and Kashmir"],
    "20": ["Uttar Pradesh"],
    "21": ["Uttar Pradesh"],
    "22": ["Uttar Pradesh"],
    "23": ["Uttar Pradesh"],
    "24": ["Uttar Pradesh", "Uttarakhand"],
    "25": ["Uttar Pradesh"],
    "26": ["Uttar Pradesh", "Uttarakhand"],
    "27": ["Uttar Pradesh"],
    "28": ["Uttar Pradesh"],
    "30": ["Rajasthan"],
    "31": ["Rajasthan"],
    "32": ["Rajasthan"],
    "33": ["Rajasthan"],
    "34": ["Rajasthan"],
    "36": ["Gujarat"],
    "37": ["Gujarat"],
    "38": ["Gujarat"],
    "39": ["Gujarat"],
    "40": ["Maharashtra", "Goa"],
    "41": ["Maharashtra"],
    "42": ["Maharashtra"],
    "43": ["Maharashtra"],
    "44": ["Maharashtra"],
    "45": ["Madhya Pradesh"],
    "46": ["Madhya Pradesh"],
    "47": ["Madhya Pradesh"],
    "48": ["Madhya Pradesh", "Chhattisgarh"],
    "49": ["Chhattisgarh"],
    "50": ["Telangana", "Andhra Pradesh"],
    "51": ["Andhra Pradesh"],
    "52": ["Andhra Pradesh"],
    "53": ["Andhra Pradesh"],
    "56": ["Karnataka"],
    "57": ["Karnataka"],
    "58": ["Karnataka"],
    "59": ["Karnataka"],
    "60": ["Tamil Nadu"],
    "61": ["Tamil Nadu"],
    "62": ["Tamil Nadu"],
    "63": ["Tamil Nadu"],
    "64": ["Tamil Nadu"],
    "67": ["Kerala", "Lakshadweep"],
    "68": ["Kerala"],
    "69": ["Kerala"],
    "70": ["West Bengal"],
    "71": ["West Bengal"],
    "72": ["West Bengal"],
    "73": ["West Bengal", "Sikkim"],
    "74": ["West Bengal"],
    "75": ["Odisha"],
    "76": ["Odisha"],
    "77": ["Odisha"],
    "78": ["Assam"],
    "79": ["Meghalaya", "Mizoram", "Tripura", "Nagaland", "Arunachal Pradesh", "Manipur"],
    "80": ["Bihar"],
    "81": ["Bihar", "Jharkhand"],
    "82": ["Jharkhand"],
    "83": ["Jharkhand"],
    "84": ["Bihar"],
    "85": ["Bihar"],
}

# Regex for Indian Postal PIN code
PINCODE_REGEX = re.compile(r"^[1-9][0-9]{5}$")

# High-risk colloquial phrases in Indian COD delivery (impulse/fake indicators)
HIGH_RISK_COLLOQUIAL_PATTERNS = [
    (r"\b(phone\s*karna|call\s*karna|phone\s*pe\s*baat)\b", "Demands phone call before dispatch"),
    (r"\b(kahi\s*bhi|kisi\s*ko\s*bhi)\b", "Non-specific recipient instructions"),
    (r"\b(paisa\s*nahi\s*hai|dekh\s*ke\s*lunga)\b", "Reluctant COD payment intent"),
    (r"\b(fake|test\s*order|check\s*karna)\b", "Potential test / dummy order"),
]

# Common Premise Patterns (Door, Flat, Plot, House, Ward, Gali)
PREMISE_REGEX = re.compile(r"\b(no\.?|house|flat|plot|room|ward|gali|lane|quarter|bhavan|kothi|shop|d-?\d+|c-?\d+|b-?\d+|a-?\d+|\d{1,4}[a-z]?)\b", re.IGNORECASE)


def validate_pincode_format(pincode: Optional[str]) -> bool:
    """Deterministic regex check: 6 digits, non-zero starting digit."""
    if not pincode:
        return False
    clean_pin = pincode.strip()
    return bool(PINCODE_REGEX.match(clean_pin))


def verify_pincode_zone(pincode: Optional[str], declared_state: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Deterministic lookup: Check if pincode prefix matches the declared Indian state."""
    if not pincode or not validate_pincode_format(pincode):
        return False, "Invalid or missing 6-digit pincode format"
    
    prefix = pincode[:2]
    expected_states = POSTAL_CIRCLE_PREFIXES.get(prefix)
    
    if not expected_states:
        return False, f"Pincode prefix {prefix}xxx not recognized in official India Post routing table"
    
    if not declared_state or declared_state.strip() == "":
        return True, f"Pincode belongs to {', '.join(expected_states)} (state unspecified by user)"
    
    clean_state = declared_state.strip().lower()
    for state in expected_states:
        if state.lower() in clean_state or clean_state in state.lower():
            return True, f"Verified: Pincode {pincode} matches {state}"
            
    return False, f"Geographic Mismatch: Pincode {pincode} belongs to {', '.join(expected_states)}, but order specifies '{declared_state}'"


def check_premise_present(raw_address: str, house_building: Optional[str]) -> bool:
    """Deterministic check: Is there a specific house/flat/ward/door identifier?"""
    if house_building and len(house_building.strip()) > 1:
        return True
    return bool(PREMISE_REGEX.search(raw_address))


def check_high_risk_phrases(raw_address: str) -> List[str]:
    """Deterministic string search for known delivery-failure and fake-order keywords."""
    found = []
    text_lower = raw_address.lower()
    for pattern, description in HIGH_RISK_COLLOQUIAL_PATTERNS:
        if re.search(pattern, text_lower):
            found.append(description)
    return found


def run_deterministic_checks(
    raw_address: str,
    pincode: Optional[str],
    declared_state: Optional[str],
    house_building: Optional[str],
    has_landmark: bool
) -> DeterministicValidation:
    """Execute all rule-based validations in <1 millisecond with zero LLM tokens."""
    is_valid_format = validate_pincode_format(pincode)
    is_zone_valid, zone_msg = verify_pincode_zone(pincode, declared_state)
    has_premise = check_premise_present(raw_address, house_building)
    risk_phrases = check_high_risk_phrases(raw_address)
    
    flags = []
    if not is_valid_format:
        flags.append("CRITICAL: Invalid or missing 6-digit postal PIN code")
    if not is_zone_valid and zone_msg:
        flags.append(f"CRITICAL: {zone_msg}")
    if not has_premise and not has_landmark:
        flags.append("WARNING: Neither a house/flat number nor a landmark was provided")
    elif not has_premise:
        flags.append("NOTICE: No house or door number specified; relies entirely on local landmark")
    if risk_phrases:
        for phrase in risk_phrases:
            flags.append(f"RISK: {phrase}")
            
    return DeterministicValidation(
        pincode_valid_format=is_valid_format,
        pincode_zone_verified=is_zone_valid,
        has_door_or_building_number=has_premise,
        has_actionable_landmark=has_landmark,
        high_risk_phrases_found=risk_phrases,
        validation_flags=flags,
    )
