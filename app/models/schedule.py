from sqlalchemy import Time
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time

from app.core.database import Base


class WorkingSchedule(Base):
    __tablename__ = "work_schedules"

    day_of_week: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    start_at: Mapped[time] = mapped_column(Time, nullable=False)
    end_at: Mapped[time] = mapped_column(Time, nullable=False)
    is_working_day: Mapped[bool] = mapped_column(default=True, server_default="true", nullable=False)