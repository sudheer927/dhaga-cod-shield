"""
Dhaga & Co. COD Shield - Pydantic Structured Output Schemas
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ParsedAddress(BaseModel):
    """Structured extraction of customer-supplied Indian address."""
    recipient_name: Optional[str] = Field(None, description="Name of the parcel recipient")
    phone_number: Optional[str] = Field(None, description="10-digit Indian mobile number if detected")
    house_or_building: Optional[str] = Field(None, description="House, flat, plot, or shop number")
    street_or_road: Optional[str] = Field(None, description="Street name, lane, gali, or mohalla")
    landmark: Optional[str] = Field(None, description="Prominent local reference point (mandir, hospital, shop, etc.)")
    locality_area: Optional[str] = Field(None, description="Sub-locality, colony, or village name")
    city: Optional[str] = Field(None, description="City, town, or taluka")
    state: Optional[str] = Field(None, description="Indian state or union territory")
    pincode: Optional[str] = Field(None, description="6-digit Indian postal PIN code")
    normalized_formatted_address: str = Field(..., description="Clean standard courier label representation")
    language_detected: str = Field(default="Hinglish", description="Language mix: Hinglish, Hindi, English, Vernacular")
    extraction_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Model extraction certainty")


class DeterministicValidation(BaseModel):
    """Deterministic validation outputs computed solely in Python (0 model tokens)."""
    pincode_valid_format: bool = Field(..., description="Matches ^[1-9][0-9]{5}$")
    pincode_zone_verified: bool = Field(..., description="Pincode exists within declared state circle")
    has_door_or_building_number: bool = Field(..., description="Explicit premise identifier present")
    has_actionable_landmark: bool = Field(..., description="Clear relative landmark provided")
    high_risk_phrases_found: List[str] = Field(default_factory=list, description="Found phrases like 'phone karna', 'kahi bhi'")
    validation_flags: List[str] = Field(default_factory=list, description="Hard deterministic alerts")


class RTORiskAssessment(BaseModel):
    """LLM + Rule calibrated RTO Risk classification."""
    risk_score: int = Field(..., ge=0, le=100, description="0 (Zero Risk) to 100 (Guaranteed RTO)")
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="Classification category")
    risk_factors: List[str] = Field(default_factory=list, description="Specific reasons driving the score")
    delivery_feasibility: Literal["EXCELLENT", "ACCEPTABLE", "QUESTIONABLE", "IMPOSSIBLE"] = Field(
        ..., description="Likelihood a Delhivery/Ekart delivery partner finds this door"
    )
    requires_customer_confirmation: bool = Field(..., description="Whether pre-dispatch outreach is needed")


class WhatsAppIntervention(BaseModel):
    """Evaluator-Optimizer output for customer-facing Hinglish WhatsApp outreach."""
    customer_message_hinglish: str = Field(..., description="Warm, polite Hinglish clarification message")
    missing_fields_highlighted: List[str] = Field(default_factory=list, description="Exact missing pieces explained simply")
    quick_reply_suggestions: List[str] = Field(
        default_factory=lambda: ["Confirm Current Address", "Add House Number", "Cancel Order"],
        description="WhatsApp interactive button choices"
    )


class DispatchDecision(BaseModel):
    """Final unified decision payload passed to Unicommerce / Logistics API."""
    order_id: str
    order_value_inr: float
    decision: Literal["APPROVE_INSTANT_DISPATCH", "HOLD_WHATSAPP_CONFIRMATION", "REJECT_UNSERVICEABLE_ADDRESS"]
    decision_summary: str
    fails_visibly: bool = False
    failure_banner_message: Optional[str] = None
    logistics_loss_prevented_inr: float = 0.0
    
    parsed_address: ParsedAddress
    deterministic_checks: DeterministicValidation
    rto_assessment: RTORiskAssessment
    whatsapp_intervention: Optional[WhatsAppIntervention] = None

    # Audit & Engineering Telemetry
    fast_model: str
    judgment_model: Optional[str] = None
    processing_time_ms: float
    estimated_api_cost_inr: float
