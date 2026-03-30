import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SymptomRecord(Base):
    __tablename__ = "symptom_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), index=True)
    body_part: Mapped[str] = mapped_column(String(20))   # 12 个部位之一
    symptom_name: Mapped[str] = mapped_column(String(100))
    severity: Mapped[int] = mapped_column(Integer)       # 1-10
    duration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_detail: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    visit: Mapped["Visit"] = relationship(back_populates="symptom_records")