from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TransportVehicleBase(BaseModel):
    vehicle: str
    route: str
    driver: Optional[str] = None
    capacity: Optional[int] = 30
    occupied: Optional[int] = 0
    status: Optional[str] = "Active"
    fitnessExpiry: Optional[str] = None
    insuranceExpiry: Optional[str] = None


class TransportVehicleCreate(TransportVehicleBase):
    id: Optional[str] = None


class TransportVehicleUpdate(BaseModel):
    vehicle: Optional[str] = None
    route: Optional[str] = None
    driver: Optional[str] = None
    capacity: Optional[int] = None
    occupied: Optional[int] = None
    status: Optional[str] = None
    fitnessExpiry: Optional[str] = None
    insuranceExpiry: Optional[str] = None


class TransportVehicleResponse(TransportVehicleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
