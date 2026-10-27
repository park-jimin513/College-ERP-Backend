from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.fee import FeeRecord
from app.schemas.fee import FeeRecordCreate, FeeRecordUpdate, FeeRecordResponse

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("", response_model=List[FeeRecordResponse])
def get_fee_records(
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    department: Optional[str] = Query(None),
    feeType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(FeeRecord)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                FeeRecord.name.ilike(s),
                FeeRecord.id.ilike(s),
                FeeRecord.department.ilike(s)
            )
        )
    if department:
        query = query.filter(FeeRecord.department == department)
    if feeType:
        query = query.filter(FeeRecord.feeType == feeType)
    if status:
        query = query.filter(FeeRecord.status == status)

    return query.order_by(FeeRecord.id.asc()).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=FeeRecordResponse)
def get_fee_record_by_id(id: str, db: Session = Depends(get_db)):
    record = db.query(FeeRecord).filter(FeeRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Fee record for '{id}' not found.")
    return record


@router.post("", response_model=FeeRecordResponse, status_code=status.HTTP_201_CREATED)
def record_fee(payload: FeeRecordCreate, db: Session = Depends(get_db)):
    if not payload.id:
        raise HTTPException(status_code=400, detail="Student ID / Record ID is required.")

    existing = db.query(FeeRecord).filter(FeeRecord.id == payload.id).first()
    if existing:
        for field, value in payload.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    record = FeeRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    sync_to_mongodb('fee_records', record.__dict__.copy())
    return record


@router.put("/{id}", response_model=FeeRecordResponse)
def update_fee_record(id: str, payload: FeeRecordUpdate, db: Session = Depends(get_db)):
    record = db.query(FeeRecord).filter(FeeRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Fee record for '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_fee_record(id: str, db: Session = Depends(get_db)):
    record = db.query(FeeRecord).filter(FeeRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Fee record for '{id}' not found.")

    db.delete(record)
    db.commit()
    sync_to_mongodb('fee_records', {"id": id}, delete=True)
    return {"message": f"Fee record '{id}' deleted successfully."}
