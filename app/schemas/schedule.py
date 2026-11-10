from pydantic import BaseModel, ConfigDict
from datetime import time


class ScheduleResponse(BaseModel):
    day_of_week: int
    start_at: time
    end_at: time
    is_working_day: bool

    model_config = ConfigDict(from_attributes=True)


class ScheduleUpdateTime(BaseModel):
    start_at: time | None = None
    end_at: time | None = None


class ScheduleBulkUpdate(BaseModel):
    start_at: time
    end_at: time