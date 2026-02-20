from fastapi import FastAPI
from app.config import get_settings
from app.models.schemas import (
    DosageRequest,
    DosageResponse,
    MedicineInfoRequest,
    MedicineInfoResponse,
    WarningSignsRequest,
    WarningSignsResponse,
    EmergencyInfoRequest,
    EmergencyInfoResponse,
    InteractionRequest,
    InteractionResponse,
)
from app.services.ai_service import AIService
from app.exceptions.handlers import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

register_exception_handlers(app)

ai_service = AIService()


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "endpoints": {
            "dosage_calculator": "POST /api/v1/medicine/dosage",
            "medicine_info": "POST /api/v1/medicine/info",
            "warning_signs": "POST /api/v1/medicine/warnings",
            "emergency_info": "POST /api/v1/medicine/emergency",
            "interactions": "POST /api/v1/medicine/interactions",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/medicine/dosage")
async def dosage_calculator(request: DosageRequest):
    result = await ai_service.calculate_dosage(
        medicine_name=request.medicine_name,
        child_weight_kg=request.child_weight_kg,
        child_age_years=request.child_age_years,
        condition=request.condition,
    )

    return DosageResponse(
        medicine_name=request.medicine_name,
        child_weight_kg=request.child_weight_kg,
        child_age_years=request.child_age_years,
        forms=result["forms"],
        max_daily_dose_mg=result["max_daily_dose_mg"],
        notes=result["notes"],
    )


@app.post("/api/v1/medicine/info")
async def medicine_info(request: MedicineInfoRequest):
    result = await ai_service.get_medicine_info(
        medicine_name=request.medicine_name,
        child_age_years=request.child_age_years,
    )

    return MedicineInfoResponse(
        medicine_name=request.medicine_name,
        advantages=result["advantages"],
        disadvantages=result["disadvantages"],
        summary=result["summary"],
    )


@app.post("/api/v1/medicine/warnings")
async def warning_signs(request: WarningSignsRequest):
    result = await ai_service.get_warning_signs(
        medicine_name=request.medicine_name,
        child_age_years=request.child_age_years,
    )

    return WarningSignsResponse(
        medicine_name=request.medicine_name,
        warning_signs=result["warning_signs"],
        call_doctor_immediately=result["call_doctor_immediately"],
        stop_medication_if=result["stop_medication_if"],
    )


@app.post("/api/v1/medicine/emergency")
async def emergency_info(request: EmergencyInfoRequest):
    result = await ai_service.get_emergency_info(
        medicine_name=request.medicine_name,
        child_age_years=request.child_age_years,
        child_weight_kg=request.child_weight_kg,
    )

    return EmergencyInfoResponse(
        medicine_name=request.medicine_name,
        overdose_signs=result["overdose_signs"],
        immediate_steps=result["immediate_steps"],
        emergency_contacts=result["emergency_contacts"],
    )


@app.post("/api/v1/medicine/interactions")
async def check_interactions(request: InteractionRequest):
    result = await ai_service.check_interactions(
        medicines=request.medicines,
        child_age_years=request.child_age_years,
    )

    return InteractionResponse(
        medicines=request.medicines,
        can_take_together=result["can_take_together"],
        explanation=result["explanation"],
        precautions=result["precautions"],
        alternative_timing=result["alternative_timing"],
    )
