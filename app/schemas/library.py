from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    author: str
    category: str
    copies: Optional[int] = 1
    available: Optional[int] = 1
    issuedTo: Optional[str] = "—"
    dueDate: Optional[str] = "—"
    status: Optional[str] = "Available"


class BookCreate(BookBase):
    id: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    copies: Optional[int] = None
    available: Optional[int] = None
    issuedTo: Optional[str] = None
    dueDate: Optional[str] = None
    status: Optional[str] = None


class BookResponse(BookBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
