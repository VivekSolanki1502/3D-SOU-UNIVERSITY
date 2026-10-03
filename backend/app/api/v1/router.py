from fastapi import APIRouter
from app.api.v1.endpoints import admin, auth, campus, events, exams, health, sos

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(campus.router, prefix="/campus", tags=["Campus 3D & Directory"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(sos.router, prefix="/sos", tags=["SOS Emergency"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Dashboard"])
