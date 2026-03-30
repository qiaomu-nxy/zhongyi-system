import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id"), unique=True, index=True
    )
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id"), nullable=True
    )  # V2 多医师预留
    treatment_types: Mapped[str] = mapped_column(String(200), default="")  # JSON 列表
    tongue_diagnosis: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pulse_diagnosis: Mapped[str | None] = mapped_column(String(200), nullable=True)
    physical_signs: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    syndrome_differentiation: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    prescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    acupuncture_points: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 列表
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    visit: Mapped["Visit"] = relationship(back_populates="medical_record")