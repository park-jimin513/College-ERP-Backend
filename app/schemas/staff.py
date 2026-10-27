<<<<<<< HEAD
from typing import Optional
=======
from typing import Any, Optional
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TeachingStaffBase(BaseModel):
    name: str
    department: str
    designation: Optional[str] = "Assistant Professor"
    employmentType: Optional[str] = "Permanent"
    status: Optional[str] = "Active"
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience: Optional[str] = None
    joiningDate: Optional[str] = None
    subjects: Optional[str] = None
    classes: Optional[str] = None
    workload: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
<<<<<<< HEAD
=======
    documents: Optional[dict[str, Any]] = None
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9


class TeachingStaffCreate(TeachingStaffBase):
    id: Optional[str] = None


class TeachingStaffUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    employmentType: Optional[str] = None
    status: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience: Optional[str] = None
    joiningDate: Optional[str] = None
    subjects: Optional[str] = None
    classes: Optional[str] = None
    workload: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
<<<<<<< HEAD
=======
    documents: Optional[dict[str, Any]] = None
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9


class TeachingStaffResponse(TeachingStaffBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NonTeachingStaffBase(BaseModel):
    name: str
    area: str
    designation: Optional[str] = "Office Assistant"
    employmentType: Optional[str] = "Permanent"
    status: Optional[str] = "Active"
    joiningDate: Optional[str] = None
    shift: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
<<<<<<< HEAD
=======
    documents: Optional[dict[str, Any]] = None
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9


class NonTeachingStaffCreate(NonTeachingStaffBase):
    id: Optional[str] = None


class NonTeachingStaffUpdate(BaseModel):
    name: Optional[str] = None
    area: Optional[str] = None
    designation: Optional[str] = None
    employmentType: Optional[str] = None
    status: Optional[str] = None
    joiningDate: Optional[str] = None
    shift: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
<<<<<<< HEAD


class NonTeachingStaffResponse(NonTeachingStaffBase):
=======
    documents: Optional[dict[str, Any]] = None


class NonTeachingStaffResponse(NonTeachingStaffBase):
    area: Optional[str] = None
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
