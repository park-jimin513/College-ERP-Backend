from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttendanceRecordBase(BaseModel):
    studentId: str
    name: str
    department: str
    section: Optional[str] = "A"
    subject: str
    conducted: Optional[int] = 0
    attended: Optional[int] = 0
    attendance: Optional[int] = 0
    status: Optional[str] = "Good"


class AttendanceRecordCreate(AttendanceRecordBase):
    id: Optional[str] = None


class AttendanceRecordResponse(AttendanceRecordBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
