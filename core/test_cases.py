"""
Dhaga & Co. COD Shield - Realistic Indian E-Commerce Test Dataset
Represents Tier-2/3 India, Hinglish colloquialisms, relative landmarks, and real failure modes.
"""

from typing import Dict, Any, List

REAL_SHAPED_TEST_CASES: List[Dict[str, Any]] = [
    {
        "id": "DHAGA-1001",
        "category": "Tier-1 Metro Clean",
        "title": "Clean Metro Apartment (Baseline Low Risk)",
        "order_value": 1299.0,
        "customer_name": "Pooja Hegde",
        "phone": "9845123456",
        "raw_address": "Flat 402, Green Glen Layout, Behind Cult Fitness, Bellandur, Bengaluru, Karnataka - 560103",
        "expected_tier": "LOW",
        "description": "Standard structured urban address with building, street, and matching postal PIN."
    },
    {
        "id": "DHAGA-1002",
        "category": "Tier-2/3 Hinglish Landmark",
        "title": "Hinglish Relative Landmark (Deliverable)",
        "order_value": 799.0,
        "customer_name": "Rameshwar Singh",
        "phone": "9431287654",
        "raw_address": "shankar talkies ke peeche wali gali, purana bypass road, ward no 14, Motihari, Bihar 845401",
        "expected_tier": "MEDIUM",
        "description": "Typical semi-urban Hinglish address. No official building name, but landmark & ward number are actionable for courier partner."
    },
    {
        "id": "DHAGA-1003",
        "category": "Tier-3 Ambiguous Landmark",
        "title": "Vague Landmark with No House Number (Needs WhatsApp Prompt)",
        "order_value": 840.0,
        "customer_name": "Anita Devi",
        "phone": "9935112233",
        "raw_address": "Dr. Verma clinic ke samne, shiv mandir road, post office ke pass, phone pe baat kar lena, Deoria, Uttar Pradesh 274001",
        "expected_tier": "HIGH",
        "description": "Contains multiple conflicting relative landmarks, zero house/door number, and requests phone call. High risk of NDR without WhatsApp confirmation."
    },
    {
        "id": "DHAGA-1004",
        "category": "Intentional Failure Case (Geographic Mismatch)",
        "title": "Geographic Pincode Mismatch (FAILS VISIBLY)",
        "order_value": 1499.0,
        "customer_name": "Suresh Choudhary",
        "phone": "9829012345",
        "raw_address": "Plot 24, Near Railway Station, Civil Lines, Jaipur, Rajasthan - 400001",
        "expected_tier": "HIGH",
        "description": "Intentional Failure Demo: 400001 is Mumbai (Maharashtra circle), but user specifies Jaipur, Rajasthan. System flags visible error and halts dispatch."
    },
    {
        "id": "DHAGA-1005",
        "category": "Bogus / High RTO Risk",
        "title": "Impulse / Bogus COD Order (FAILS VISIBLY)",
        "order_value": 399.0,
        "customer_name": "Vikram",
        "phone": "9123456789",
        "raw_address": "kahi bhi de dena aake call karna, ground ke samne, pincode yaad nahi, 000000",
        "expected_tier": "HIGH",
        "description": "Bogus input with invalid 000000 pincode and zero address detail. Intercepted instantly with zero wasted logistics."
    },
    {
        "id": "DHAGA-1006",
        "category": "Tier-3 Rural Hamlet",
        "title": "Village Panchayat Shop Order (Rural Cluster)",
        "order_value": 840.0,
        "customer_name": "Kavita Kumari",
        "phone": "9771567890",
        "raw_address": "Panchayat bhavan ke bagal me, sharma kirana dukan no 3, gao pipra khem, Gopalganj, Bihar 841428",
        "expected_tier": "LOW",
        "description": "Rural tier-3 order with unambiguous shop and panchayat landmark. Safe to route to Ekart/Delhivery rural hub."
    },
    {
        "id": "DHAGA-1007",
        "category": "Phonetic / Spelling Drift",
        "title": "Phonetic Spelling Variants & Typos",
        "order_value": 999.0,
        "customer_name": "Rajesh Mahato",
        "phone": "9832109876",
        "raw_address": "Qtr no B-12, Near Hanuman Mandir, Sector Fore, Bokaro Steel Cty, Jharkand 827004",
        "expected_tier": "LOW",
        "description": "Common typing mistakes ('Sector Fore', 'Steel Cty', 'Jharkand'). LLM normalizes into canonical courier format."
    }
]
