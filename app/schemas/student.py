from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StudentBase(BaseModel):
    name: str
    department: str
    batch: str
    year: Optional[str] = "1st Year"
    semester: Optional[str] = "Semester 1"
    section: Optional[str] = "A"
    gender: Optional[str] = "Male"
    admissionType: Optional[str] = "Regular"
    attendance: Optional[int] = 0
    feeStatus: Optional[str] = "Pending"
    status: Optional[str] = "Active"
    
    phone: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[str] = None
    bloodGroup: Optional[str] = None
    address: Optional[str] = None
    
    father: Optional[str] = None
    mother: Optional[str] = None
    guardianPhone: Optional[str] = None
    
    totalFee: Optional[str] = "₹0"
    paidFee: Optional[str] = "₹0"
    pendingFee: Optional[str] = "₹0"
    cgpa: Optional[str] = "0.0"


class StudentCreate(StudentBase):
    id: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    batch: Optional[str] = None
    year: Optional[str] = None
    semester: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    admissionType: Optional[str] = None
    attendance: Optional[int] = None
    feeStatus: Optional[str] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[str] = None
    bloodGroup: Optional[str] = None
    address: Optional[str] = None
    father: Optional[str] = None
    mother: Optional[str] = None
    guardianPhone: Optional[str] = None
    totalFee: Optional[str] = None
    paidFee: Optional[str] = None
    pendingFee: Optional[str] = None
    cgpa: Optional[str] = None


class StudentResponse(StudentBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
