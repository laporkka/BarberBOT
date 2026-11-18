from pydantic import BaseModel, Field, ConfigDict


class ManagerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    tg_id: str 
    is_active: bool = Field(True)


class ManagerResponse(BaseModel):
    id: int
    name: str
    tg_id: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)