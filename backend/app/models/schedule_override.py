import datetime

from sqlalchemy import Boolean, Date, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ScheduleOverride(Base):
    __tablename__ = "schedule_overrides"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id"), nullable=True
    )  # V2 多医师预留
    override_date: Mapped[datetime.date] = mapped_column(Date, index=True)
    is_working: Mapped[bool] = mapped_column(Boolean, default=False)
    morning_start: Mapped[str | None] = mapped_column(String(10), nullable=True)
    morning_end: Mapped[str | None] = mapped_column(String(10), nullable=True)
    afternoon_start: Mapped[str | None] = mapped_column(String(10), nullable=True)
    afternoon_end: Mapped[str | None] = mapped_column(String(10), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())