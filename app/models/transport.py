from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class TransportVehicle(Base):
    __tablename__ = "transport_vehicles"

    id = Column(String(50), primary_key=True, index=True)  # e.g. VEH-01
    vehicle = Column(String(100), nullable=False, index=True)
    route = Column(String(150), nullable=False, index=True)
    driver = Column(String(100), nullable=True)
    capacity = Column(Integer, default=30)
    occupied = Column(Integer, default=0)
    status = Column(String(50), default="Active")  # Active, Under Maintenance
    fitnessExpiry = Column(String(50), nullable=True)
    insuranceExpiry = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
