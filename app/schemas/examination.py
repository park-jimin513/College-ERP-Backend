from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ExaminationBase(BaseModel):
    name: str
    department: str
    semester: str
    type: Optional[str] = "Internal"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    status: Optional[str] = "Scheduled"
    subjects: Optional[str] = None
    rooms: Optional[str] = None
    invigilators: Optional[str] = None


class ExaminationCreate(ExaminationBase):
    id: Optional[str] = None


class ExaminationUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    type: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    status: Optional[str] = None
    subjects: Optional[str] = None
    rooms: Optional[str] = None
    invigilators: Optional[str] = None


class ExaminationResponse(ExaminationBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExamResultBase(BaseModel):
    name: str
    department: str
    semester: str
    sgpa: Optional[str] = "0.0"
    cgpa: Optional[str] = "0.0"
    backlogs: Optional[int] = 0
    result: Optional[str] = "Pass"


class ExamResultCreate(ExamResultBase):
    id: Optional[str] = None


class ExamResultResponse(ExamResultBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
