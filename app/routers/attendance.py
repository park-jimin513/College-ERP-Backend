from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import insert_document, list_documents
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
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "attendance_records",
        filters={"department": department, "section": section, "status": status},
        search=search,
        search_fields=("name", "studentId", "subject"),
        sort_by="studentId",
    )


@router.post("", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
def mark_attendance(payload: AttendanceRecordCreate, db: Database = Depends(get_db)):
    conducted = payload.conducted or 1
    attended = payload.attended or 0
    percentage = round((attended / conducted) * 100) if conducted > 0 else 0
    data = payload.model_dump()
    data["id"] = payload.id or f"ATT-{payload.studentId}-{payload.subject[:3].upper()}"
    data["attendance"] = percentage
    data["status"] = compute_status(percentage)
    return insert_document(db, "attendance_records", data)
