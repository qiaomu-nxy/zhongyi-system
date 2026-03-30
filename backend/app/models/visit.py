import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id"), nullable=True
    )  # V2 多医师预留
    visit_date: Mapped[datetime.date] = mapped_column(Date, index=True)
    visit_number: Mapped[int] = mapped_column(Integer, default=1)  # 该患者第 N 次就诊
    status: Mapped[str] = mapped_column(
        String(20), default="待签到"
    )  # 待签到 / 待接诊 / 已完成 / 已作废
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptom_submitted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="visits")
    symptom_records: Mapped[list["SymptomRecord"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )
    medical_record: Mapped["MedicalRecord | None"] = relationship(
        back_populates="visit", uselist=False, cascade="all, delete-orphan"
    )
    lab_results: Mapped[list["LabResult"]] = relationship(back_populates="visit")