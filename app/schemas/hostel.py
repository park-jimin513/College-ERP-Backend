from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HostelRoomBase(BaseModel):
    room: str
    block: str
    floor: Optional[str] = "1st Floor"
    capacity: Optional[int] = 2
    occupied: Optional[int] = 0
    occupants: Optional[str] = "—"
    status: Optional[str] = "Vacant"


class HostelRoomCreate(HostelRoomBase):
    id: Optional[str] = None


class HostelRoomUpdate(BaseModel):
    room: Optional[str] = None
    block: Optional[str] = None
    floor: Optional[str] = None
    capacity: Optional[int] = None
    occupied: Optional[int] = None
    occupants: Optional[str] = None
    status: Optional[str] = None


class HostelRoomResponse(HostelRoomBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
