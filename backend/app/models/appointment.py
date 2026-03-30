import datetime

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("appointment_date", "time_slot", name="uq_date_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id"), nullable=True
    )  # V2 多医师预留
    appointment_date: Mapped[datetime.date] = mapped_column(Date, index=True)
    time_slot: Mapped[str] = mapped_column(String(10))  # "09:00"
    status: Mapped[str] = mapped_column(
        String(20), default="待就诊"
    )  # 待就诊 / 已完成 / 已取消 / 爽约
    cancel_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="appointments")