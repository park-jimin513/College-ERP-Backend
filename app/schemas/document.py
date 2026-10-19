from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    name: str
    owner: str
    ownerType: Optional[str] = "Student"  # Student, Staff
    category: Optional[str] = "Academic"  # Identity, Academic, Admission, Transfer, HR
    uploadedOn: Optional[str] = None
    status: Optional[str] = "Pending"  # Verified, Pending, Rejected
    fileUrl: Optional[str] = None


class DocumentCreate(DocumentBase):
    id: Optional[str] = None


class DocumentStatusUpdate(BaseModel):
    status: str  # Verified, Pending, Rejected


class DocumentResponse(DocumentBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
