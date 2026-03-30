import datetime

from sqlalchemy import Boolean, Date, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    birth_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON 列表
    allergy_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    wx_openid: Mapped[str | None] = mapped_column(String(100), nullable=True)  # V2 预留
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    histories: Mapped[list["PatientHistory"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    visits: Mapped[list["Visit"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    lab_results: Mapped[list["LabResult"]] = relationship(back_populates="patient")