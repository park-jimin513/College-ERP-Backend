from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime
from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(String(50), primary_key=True, index=True)  # e.g. STU1024
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    batch = Column(String(50), nullable=False, index=True)
    year = Column(String(50), default="1st Year")
    semester = Column(String(50), default="Semester 1")
    section = Column(String(20), default="A")
    gender = Column(String(20), default="Male")
    admissionType = Column(String(50), default="Regular")
    attendance = Column(Integer, default=0)
    feeStatus = Column(String(50), default="Pending")
    status = Column(String(50), default="Active")
    
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    dob = Column(String(50), nullable=True)
    bloodGroup = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    
    father = Column(String(100), nullable=True)
    mother = Column(String(100), nullable=True)
    guardianPhone = Column(String(50), nullable=True)
    
    totalFee = Column(String(50), default="₹0")
    paidFee = Column(String(50), default="₹0")
    pendingFee = Column(String(50), default="₹0")
    cgpa = Column(String(20), default="0.0")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
