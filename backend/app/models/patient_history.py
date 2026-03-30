import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PatientHistory(Base):
    __tablename__ = "patient_histories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    condition_name: Mapped[str] = mapped_column(String(100))
    treatment_institution: Mapped[str | None] = mapped_column(String(200), nullable=True)
    treatment_method: Mapped[str | None] = mapped_column(String(200), nullable=True)
    treatment_duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    treatment_effect: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="histories")