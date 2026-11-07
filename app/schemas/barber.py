from pydantic import BaseModel, Field, ConfigDict


class BarberCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    tg_id: str 
    is_active: bool


class BarberUpdate(BaseModel):
    name: str | None = None
    tg_id: str | None = None
    is_active: bool = True


class BarberResponse(BaseModel):
    id: int
    name: str
    tg_id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)