from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.attendance import AttendanceRecord
from app.schemas.attendance import AttendanceRecordCreate, AttendanceRecordResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def compute_status(percentage: int) -> str:
    if percentage >= 85:
        return "Good"
    if percentage >= 75:
        return "Warning"
    return "Shortage"


@router.get("", response_model=List[AttendanceRecordResponse])
def get_attendance_records(
    search: Optional[str] = Query(None, description="Search by student name, ID or subject"),
    department: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(AttendanceRecord)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                AttendanceRecord.name.ilike(s),
                AttendanceRecord.studentId.ilike(s),
                AttendanceRecord.subject.ilike(s)
            )
        )
    if department:
        query = query.filter(AttendanceRecord.department == department)
    if section:
        query = query.filter(AttendanceRecord.section == section)
    if status:
        query = query.filter(AttendanceRecord.status == status)

    return query.order_by(AttendanceRecord.studentId.asc()).all()


@router.post("", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
def mark_attendance(payload: AttendanceRecordCreate, db: Session = Depends(get_db)):
    conducted = payload.conducted or 1
    attended = payload.attended or 0
    pct = round((attended / conducted) * 100) if conducted > 0 else 0
    status_label = compute_status(pct)

    record_id = payload.id or f"ATT-{payload.studentId}-{payload.subject[:3].upper()}"
    
    data = payload.model_dump()
    data["id"] = record_id
    data["attendance"] = pct
    data["status"] = status_label

    record = AttendanceRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    sync_to_mongodb('attendance_records', record.__dict__.copy())
    return record
