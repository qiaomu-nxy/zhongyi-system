import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.models import (  # noqa: F401
    Appointment, Doctor, LabResult, MedicalRecord, Patient,
    PatientHistory, Schedule, ScheduleOverride, SymptomRecord, Visit,
)
from app.routers import (
    analysis, appointments, auth, backup, config,
    doctors, lab_results, medical_records, patients,
    schedules, symptoms, visits,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="中医问诊管理系统", description="单诊所单医师版 V1", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
Base.metadata.create_all(bind=engine)

for r in [auth, doctors, patients, visits, symptoms, medical_records,
          lab_results, schedules, appointments, analysis, backup, config]:
    app.include_router(r.router)


@app.get("/health", tags=["系统"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}