from fastapi import APIRouter
from app.api import auth, users, patients, appointments, follow_ups, consultations, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(follow_ups.router, prefix="/follow-ups", tags=["follow-ups"])
api_router.include_router(consultations.router, prefix="/consultations", tags=["consultations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
