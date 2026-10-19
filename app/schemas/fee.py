from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator


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

    @model_validator(mode="before")
    @classmethod
    def derive_legacy_record_name(cls, value):
        if isinstance(value, dict) and not value.get("name"):
            value = dict(value)
            value["name"] = value.get("studentName") or value.get("studentId") or value.get("id")
        return value
