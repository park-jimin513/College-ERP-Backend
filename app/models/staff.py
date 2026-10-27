from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.core.database import Base


class TeachingStaff(Base):
    __tablename__ = "teaching_staff"

    id = Column(String(50), primary_key=True, index=True)  # e.g. EMP2001
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    designation = Column(String(100), default="Assistant Professor")
    employmentType = Column(String(50), default="Permanent")
    status = Column(String(50), default="Active")
    qualification = Column(String(150), nullable=True)
    specialization = Column(String(150), nullable=True)
    experience = Column(String(50), nullable=True)
    joiningDate = Column(String(50), nullable=True)
    subjects = Column(String(255), nullable=True)
    classes = Column(String(255), nullable=True)
    workload = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NonTeachingStaff(Base):
    __tablename__ = "non_teaching_staff"

    id = Column(String(50), primary_key=True, index=True)  # e.g. NTS3001
    name = Column(String(150), nullable=False, index=True)
    area = Column(String(100), nullable=False, index=True)
    designation = Column(String(100), default="Office Assistant")
    employmentType = Column(String(50), default="Permanent")
    status = Column(String(50), default="Active")
    joiningDate = Column(String(50), nullable=True)
    shift = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
