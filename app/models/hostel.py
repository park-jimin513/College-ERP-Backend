from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    id = Column(String(50), primary_key=True, index=True)  # e.g. RM-A101
    room = Column(String(50), nullable=False, index=True)
    block = Column(String(100), nullable=False, index=True)
    floor = Column(String(50), default="1st Floor")
    capacity = Column(Integer, default=2)
    occupied = Column(Integer, default=0)
    occupants = Column(String(255), default="—")
    status = Column(String(50), default="Vacant")  # Vacant, Occupied, Partially Filled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
