from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(String(50), primary_key=True, index=True)  # e.g. DEP-CSE
    name = Column(String(150), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    hod = Column(String(100), nullable=True)
    status = Column(String(50), default="Active")
    faculty = Column(Integer, default=0)
    students = Column(Integer, default=0)
    programs = Column(String(150), nullable=True)
    established = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(50), primary_key=True, index=True)  # e.g. CS101
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    year = Column(String(50), nullable=False)
    semester = Column(String(50), nullable=False)
    type = Column(String(50), default="Core")
    credits = Column(Integer, default=3)
    hours = Column(String(100), nullable=True)
    faculty = Column(String(100), nullable=True)
    status = Column(String(50), default="Active")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AcademicProgram(Base):
    __tablename__ = "academic_programs"

    id = Column(String(50), primary_key=True, index=True)  # e.g. PRG-BTCSE
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    level = Column(String(50), default="Undergraduate")
    duration = Column(String(50), default="4 Years")
    regulation = Column(String(50), default="R-2023")
    status = Column(String(50), default="Active")
    intake = Column(Integer, default=120)
    currentStudents = Column(Integer, default=0)
    semesters = Column(Integer, default=8)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
