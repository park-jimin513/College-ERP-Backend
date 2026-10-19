from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TimetableSlotBase(BaseModel):
    department: str
    section: str = "A"
    day: str
    periodIndex: int
    periodTime: str
    subject: str
    faculty: Optional[str] = None
    room: Optional[str] = None


class TimetableSlotCreate(TimetableSlotBase):
    pass


class TimetableSlotResponse(TimetableSlotBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TimetablePeriodItem(BaseModel):
    subject: str
    faculty: str
    room: str


class TimetableGridResponse(BaseModel):
    department: str
    section: str
    days: List[str]
    periods: List[str]
    grid: Dict[str, List[TimetablePeriodItem]]
