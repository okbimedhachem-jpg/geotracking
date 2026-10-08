from pydantic import BaseModel, Field
from datetime import datetime


class LocationPayload(BaseModel):
    user_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: float | None = None
    speed: float | None = None
    heading: float | None = None
    timestamp: datetime


class LocationResponse(BaseModel):
    status: str
    message: str
