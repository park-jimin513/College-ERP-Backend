from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NoticeBase(BaseModel):
    title: str
    category: Optional[str] = "General"
    priority: Optional[str] = "Normal"
    audienceType: Optional[str] = "Entire College"
    audienceValue: Optional[str] = None
    content: str
    publishOption: Optional[str] = "Publish Now"
    scheduleDate: Optional[str] = None
    attachmentUrl: Optional[str] = None
    publishedBy: Optional[str] = "Admin"


class NoticeCreate(NoticeBase):
    pass


class NoticeResponse(NoticeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
