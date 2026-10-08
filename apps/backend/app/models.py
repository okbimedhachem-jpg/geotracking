from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="driver", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    vehicles = relationship("Vehicle", back_populates="owner")
    tracking_points = relationship("TrackingPoint", back_populates="user")
    trips = relationship("Trip", back_populates="user")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    plate_number = Column(String, unique=True, nullable=False)
    status = Column(String, default="offline", nullable=False)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="vehicles")
    tracking_points = relationship("TrackingPoint", back_populates="vehicle")
    trips = relationship("Trip", back_populates="vehicle")


class TrackingPoint(Base):
    __tablename__ = "tracking_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="tracking_points")
    vehicle = relationship("Vehicle", back_populates="tracking_points")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    start_latitude = Column(Float, nullable=False)
    start_longitude = Column(Float, nullable=False)
    end_latitude = Column(Float, nullable=True)
    end_longitude = Column(Float, nullable=True)
    distance_km = Column(Float, default=0.0, nullable=False)
    avg_speed_km_h = Column(Float, default=0.0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
