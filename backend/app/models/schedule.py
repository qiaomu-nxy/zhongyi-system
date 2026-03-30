import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int | None] = mapped_column(
        ForeignKey("doctors.id"), nullable=True
    )  # V2 多医师预留
    weekday: Mapped[int] = mapped_column(Integer)  # 0=周一 … 6=周日
    is_working: Mapped[bool] = mapped_column(Boolean, default=True)
    morning_start: Mapped[str | None] = mapped_column(String(10), nullable=True)   # "08:00"
    morning_end: Mapped[str | None] = mapped_column(String(10), nullable=True)
    afternoon_start: Mapped[str | None] = mapped_column(String(10), nullable=True)
    afternoon_end: Mapped[str | None] = mapped_column(String(10), nullable=True)
    slot_duration: Mapped[int] = mapped_column(Integer, default=30)  # 分钟
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())