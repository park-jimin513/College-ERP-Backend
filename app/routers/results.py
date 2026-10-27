from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.examination import ExamResult
from app.schemas.examination import ExamResultCreate, ExamResultResponse

router = APIRouter(prefix="/results", tags=["Results"])


@router.get("", response_model=List[ExamResultResponse])
def get_results(
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    department: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ExamResult)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                ExamResult.name.ilike(s),
                ExamResult.id.ilike(s),
                ExamResult.department.ilike(s)
            )
        )
    if department:
        query = query.filter(ExamResult.department == department)
    if semester:
        query = query.filter(ExamResult.semester == semester)
    if result:
        query = query.filter(ExamResult.result == result)

    return query.order_by(ExamResult.id.asc()).all()


@router.post("", response_model=ExamResultResponse, status_code=status.HTTP_201_CREATED)
def publish_result(payload: ExamResultCreate, db: Session = Depends(get_db)):
    if not payload.id:
        raise HTTPException(status_code=400, detail="Student ID is required.")

    existing = db.query(ExamResult).filter(ExamResult.id == payload.id).first()
    if existing:
        for field, value in payload.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_result = ExamResult(**payload.model_dump())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    sync_to_mongodb('exam_results', new_result.__dict__.copy())
    return new_result
