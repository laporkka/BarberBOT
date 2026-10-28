from pydantic import BaseModel, Field, ConfigDict


class ServiceCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    price: int = Field(..., gt=0)
    duration_min: int = Field(..., gt=0)


class ServiceResponse(BaseModel):
    id: int
    title: str
    price: int
    duration_min: int

    model_config = ConfigDict(from_attributes=True)