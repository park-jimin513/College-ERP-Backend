from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class Examination(Base):
    __tablename__ = "examinations"

    id = Column(String(50), primary_key=True, index=True)  # e.g. EXM-901
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    semester = Column(String(50), nullable=False)
    type = Column(String(50), default="Internal")  # Internal, Semester End, Supplementary
    startDate = Column(String(50), nullable=True)
    endDate = Column(String(50), nullable=True)
    status = Column(String(50), default="Scheduled")  # Scheduled, Ongoing, Completed
    subjects = Column(String(255), nullable=True)
    rooms = Column(String(255), nullable=True)
    invigilators = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExamResult(Base):
    __tablename__ = "exam_results"

    id = Column(String(50), primary_key=True, index=True)  # Student ID
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    semester = Column(String(50), nullable=False)
    sgpa = Column(String(20), default="0.0")
    cgpa = Column(String(20), default="0.0")
    backlogs = Column(Integer, default=0)
    result = Column(String(50), default="Pass")  # Pass, Backlog
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
