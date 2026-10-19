from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# --- Departments ---
class DepartmentBase(BaseModel):
    name: str
    code: str
    hod: Optional[str] = None
    status: Optional[str] = "Active"
    faculty: Optional[int] = 0
    students: Optional[int] = 0
    programs: Optional[str] = None
    established: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    id: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    hod: Optional[str] = None
    status: Optional[str] = None
    faculty: Optional[int] = None
    students: Optional[int] = None
    programs: Optional[str] = None
    established: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Courses ---
class CourseBase(BaseModel):
    name: str
    department: str
    year: str
    semester: str
    type: Optional[str] = "Core"
    credits: Optional[int] = 3
    hours: Optional[str] = None
    faculty: Optional[str] = None
    status: Optional[str] = "Active"


class CourseCreate(CourseBase):
    id: Optional[str] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    semester: Optional[str] = None
    type: Optional[str] = None
    credits: Optional[int] = None
    hours: Optional[str] = None
    faculty: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(CourseBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Academic Programs ---
class AcademicProgramBase(BaseModel):
    name: str
    department: str
    level: Optional[str] = "Undergraduate"
    duration: Optional[str] = "4 Years"
    regulation: Optional[str] = "R-2023"
    status: Optional[str] = "Active"
    intake: Optional[int] = 120
    currentStudents: Optional[int] = 0
    semesters: Optional[int] = 8


class AcademicProgramCreate(AcademicProgramBase):
    id: Optional[str] = None


class AcademicProgramUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    regulation: Optional[str] = None
    status: Optional[str] = None
    intake: Optional[int] = None
    currentStudents: Optional[int] = None
    semesters: Optional[int] = None


class AcademicProgramResponse(AcademicProgramBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
