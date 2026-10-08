from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, init_db
from app.dependencies import get_current_user, get_db, require_roles
from app.models import TrackingPoint, Trip, User, Vehicle
from app.schemas import (
    LocationPayload,
    LocationResponse,
    TokenResponse,
    TripCreate,
    TripRead,
    UserCreate,
    UserLogin,
    UserRead,
    VehicleCreate,
    VehicleRead,
)
from app.security import create_access_token, get_password_hash, verify_password
from app.websocket_manager import ConnectionManager

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/api/v1/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.env}


@app.post("/api/v1/auth/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        phone=payload.phone,
        role=payload.role,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.email)
    return TokenResponse(access_token=token, token_type="bearer", user=UserRead.model_validate(user))


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token, token_type="bearer", user=UserRead.model_validate(user))


@app.get("/api/v1/auth/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.get("/api/v1/users", response_model=list[UserRead])
def list_users(
    current_user: User = Depends(require_roles("admin", "dispatcher")),
    db: Session = Depends(get_db),
):
    return db.query(User).all()


@app.post("/api/v1/vehicles", response_model=VehicleRead)
def create_vehicle(
    payload: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Vehicle:
    vehicle = Vehicle(
        name=payload.name,
        plate_number=payload.plate_number,
        status=payload.status,
        owner_id=current_user.id,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@app.get("/api/v1/vehicles", response_model=list[VehicleRead])
def list_vehicles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "admin":
        return db.query(Vehicle).all()
    return db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()


@app.post("/api/v1/location", response_model=LocationResponse)
async def receive_location(
    payload: LocationPayload,
    db: Session = Depends(get_db),
) -> LocationResponse:
    point = TrackingPoint(
        user_id=payload.user_id,
        vehicle_id=payload.vehicle_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        accuracy=payload.accuracy,
        speed=payload.speed,
        heading=payload.heading,
        timestamp=payload.timestamp,
    )
    db.add(point)
    db.commit()

    if payload.vehicle_id is not None:
        vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first()
        if vehicle:
            vehicle.last_latitude = payload.latitude
            vehicle.last_longitude = payload.longitude
            if vehicle.status != "online":
                vehicle.status = "online"
            db.commit()

    await manager.broadcast(
        {
            "user_id": payload.user_id,
            "vehicle_id": payload.vehicle_id,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "accuracy": payload.accuracy,
            "speed": payload.speed,
            "heading": payload.heading,
            "timestamp": payload.timestamp.isoformat(),
        }
    )

    return LocationResponse(
        status="success",
        message="Position enregistrée et diffusée en temps réel",
    )


@app.get("/api/v1/trips", response_model=list[TripRead])
def list_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "admin":
        return db.query(Trip).all()
    return db.query(Trip).filter(Trip.user_id == current_user.id).all()


@app.get("/api/v1/trips/{trip_id}", response_model=TripRead)
def read_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if current_user.role != "admin" and trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return trip


@app.post("/api/v1/trips", response_model=TripRead)
def create_trip(
    payload: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Trip:
    trip = Trip(
        user_id=current_user.id,
        vehicle_id=payload.vehicle_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        start_latitude=payload.start_latitude,
        start_longitude=payload.start_longitude,
        end_latitude=payload.end_latitude,
        end_longitude=payload.end_longitude,
        distance_km=payload.distance_km,
        avg_speed_km_h=payload.avg_speed_km_h,
        duration_seconds=payload.duration_seconds,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
