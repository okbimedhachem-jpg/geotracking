from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, init_db
from app.models import TrackingPoint
from app.schemas import LocationPayload, LocationResponse
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


@app.post("/api/v1/location", response_model=LocationResponse)
async def receive_location(payload: LocationPayload) -> LocationResponse:
    db: Session = SessionLocal()

    point = TrackingPoint(
        user_id=payload.user_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        accuracy=payload.accuracy,
        speed=payload.speed,
        heading=payload.heading,
        timestamp=payload.timestamp,
    )

    db.add(point)
    db.commit()
    db.refresh(point)
    db.close()

    await manager.broadcast(
        {
            "user_id": payload.user_id,
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
