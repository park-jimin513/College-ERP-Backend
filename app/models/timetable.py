from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base


class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    department = Column(String(100), nullable=False, index=True)
    section = Column(String(20), default="A", index=True)
    day = Column(String(30), nullable=False, index=True)  # Monday, Tuesday, etc.
    periodIndex = Column(Integer, default=0)
    periodTime = Column(String(50), nullable=False)
    subject = Column(String(150), nullable=False)
    faculty = Column(String(150), nullable=True)
    room = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
