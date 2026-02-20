"""
Pydantic models (schemas) for request and response validation.
Think of these as "contracts" — they define exactly what data
comes in and what data goes out.
"""

from pydantic import BaseModel, Field
from typing import Optional


class DosageRequest(BaseModel):

    medicine_name: str = Field(
        ...,                          
        min_length=2,                 
        max_length=100,               
        description="Name of the medicine",
        examples=["Paracetamol"]
    )

    child_weight_kg: float = Field(
        ...,                          
        gt=0,                         
        le=90,                       
        description="Child's weight in kilograms",
        examples=[15.0]
    )

    child_age_years: float = Field(
        ...,                          
        ge=0,                         
        le=15,                        
        description="Child's age in years (e.g., 1.5 for 18 months)",
        examples=[5.0]
    )

    condition: Optional[str] = Field(
        None,                         
        max_length=200,
        description="Symptom like 'fever' or 'pain' (optional)",
        examples=["fever"]
    )


class MedicineInfoRequest(BaseModel):

    medicine_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the medicine",
        examples=["Amoxicillin"]
    )

    child_age_years: Optional[float] = Field(
        None,
        ge=0,
        le=15,
        description="Child's age (optional, for age-specific info)",
        examples=[3.0]
    )


MEDICAL_DISCLAIMER = (
    "⚠️ DISCLAIMER: This information is for educational purposes only "
    "and should NOT replace professional medical advice. Always consult "
    "your child's pediatrician before administering any medication."
)


class DosageForm(BaseModel):

    form: str = Field(description="Medicine form and concentration, e.g. 'Syrup (120mg/5mL)'")
    dose_mg: float = Field(description="Single dose in milligrams")
    dose_ml: Optional[float] = Field(None, description="Single dose in mL (for liquids)")
    dose_count: Optional[float] = Field(None, description="Number of tablets/capsules per dose")
    frequency: str = Field(description="How often to give, e.g. 'Every 4-6 hours'")
    max_doses_per_day: int = Field(description="Maximum number of doses in 24 hours")


class DosageResponse(BaseModel):

    medicine_name: str
    child_weight_kg: float
    child_age_years: float
    forms: list[DosageForm]
    max_daily_dose_mg: float
    notes: list[str]
    disclaimer: str = MEDICAL_DISCLAIMER


class MedicineInfoResponse(BaseModel):

    medicine_name: str
    advantages: list[str]             
    disadvantages: list[str]          
    summary: str                      
    disclaimer: str = MEDICAL_DISCLAIMER


class ErrorResponse(BaseModel):

    error: str
    message: str


class WarningSignsRequest(BaseModel):

    medicine_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the medicine",
        examples=["Ibuprofen"]
    )

    child_age_years: Optional[float] = Field(
        None,
        ge=0,
        le=18,
        description="Child's age (optional, for age-specific warnings)",
        examples=[4.0]
    )


class WarningSignsResponse(BaseModel):

    medicine_name: str
    warning_signs: list[str]
    call_doctor_immediately: list[str]
    stop_medication_if: list[str]
    disclaimer: str = MEDICAL_DISCLAIMER


class EmergencyInfoRequest(BaseModel):

    medicine_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the medicine",
        examples=["Paracetamol"]
    )

    child_age_years: Optional[float] = Field(
        None,
        ge=0,
        le=18,
        description="Child's age (optional, for age-specific emergency info)",
        examples=[3.0]
    )

    child_weight_kg: Optional[float] = Field(
        None,
        gt=0,
        le=90,
        description="Child's weight in kg (optional, helps assess severity)",
        examples=[14.0]
    )


class EmergencyInfoResponse(BaseModel):

    medicine_name: str
    overdose_signs: list[str]
    immediate_steps: list[str]
    emergency_contacts: dict[str, str]
    disclaimer: str = MEDICAL_DISCLAIMER


class InteractionRequest(BaseModel):

    medicines: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of 2–5 medicine names to check for interactions",
        examples=[["Paracetamol", "Ibuprofen"]]
    )

    child_age_years: Optional[float] = Field(
        None,
        ge=0,
        le=18,
        description="Child's age (optional, for age-specific interaction info)",
        examples=[5.0]
    )


class InteractionResponse(BaseModel):

    medicines: list[str]
    can_take_together: bool
    explanation: str
    precautions: list[str]
    alternative_timing: str
    disclaimer: str = MEDICAL_DISCLAIMER
