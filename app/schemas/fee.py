from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FeeRecordBase(BaseModel):
    name: str
    department: str
    feeType: Optional[str] = "Tuition"
    totalFee: Optional[str] = "₹0"
    paid: Optional[str] = "₹0"
    pending: Optional[str] = "₹0"
    dueDate: Optional[str] = None
    status: Optional[str] = "Pending"


class FeeRecordCreate(FeeRecordBase):
    id: Optional[str] = None


class FeeRecordUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    feeType: Optional[str] = None
    totalFee: Optional[str] = None
    paid: Optional[str] = None
    pending: Optional[str] = None
    dueDate: Optional[str] = None
    status: Optional[str] = None


class FeeRecordResponse(FeeRecordBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
