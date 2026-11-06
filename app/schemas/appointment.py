from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.models.appointments import AppointmentStatus

class AppointmentCreate(BaseModel):
    customer_tg_id: str = Field(..., max_length=255)
    customer_name: str = Field(..., min_length=2, max_length=50)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    barber_id: int
    service_id: int
    start_at: datetime
    status: AppointmentStatus = AppointmentStatus.PENDING


class AppointmentResponse(BaseModel):
    id: int
    customer_tg_id: str
    customer_name: str
    customer_phone: str
    barber_id: int
    service_id: int
    start_at: datetime
    end_at: datetime 
    status: AppointmentStatus

    model_config = ConfigDict(from_attributes=True)