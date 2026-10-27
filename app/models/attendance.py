from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(String(50), primary_key=True, index=True)
    studentId = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    section = Column(String(20), default="A")
    subject = Column(String(150), nullable=False)
    conducted = Column(Integer, default=0)
    attended = Column(Integer, default=0)
    attendance = Column(Integer, default=0)  # percentage
    status = Column(String(50), default="Good")  # Good, Warning, Shortage
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
