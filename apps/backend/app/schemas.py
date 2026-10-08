from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None
    phone: str | None = None
    role: Literal["admin", "driver", "dispatcher"] = "driver"

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime


class VehicleBase(BaseModel):
    name: str
    plate_number: str
    status: str = "offline"

    model_config = ConfigDict(from_attributes=True)


class VehicleCreate(VehicleBase):
    pass


class VehicleRead(VehicleBase):
    id: int
    owner_id: int
    last_latitude: float | None = None
    last_longitude: float | None = None


class TrackingPointBase(BaseModel):
    user_id: int
    vehicle_id: int | None = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: float | None = None
    speed: float | None = None
    heading: float | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TrackingPointRead(TrackingPointBase):
    id: int


class TripBase(BaseModel):
    vehicle_id: int | None = None
    start_time: datetime
    end_time: datetime | None = None
    start_latitude: float = Field(..., ge=-90, le=90)
    start_longitude: float = Field(..., ge=-180, le=180)
    end_latitude: float | None = Field(default=None, ge=-90, le=90)
    end_longitude: float | None = Field(default=None, ge=-180, le=180)
    distance_km: float = 0.0
    avg_speed_km_h: float = 0.0
    duration_seconds: int = 0

    model_config = ConfigDict(from_attributes=True)


class TripCreate(TripBase):
    pass


class TripRead(TripBase):
    id: int
    user_id: int


class LocationPayload(TrackingPointBase):
    pass


class LocationResponse(BaseModel):
    status: str
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
