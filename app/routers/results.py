from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.examination import ExamResult
=======

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import get_document, insert_document, list_documents, update_document
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
from app.schemas.examination import ExamResultCreate, ExamResultResponse

router = APIRouter(prefix="/results", tags=["Results"])


@router.get("", response_model=List[ExamResultResponse])
def get_results(
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    department: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
<<<<<<< HEAD
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
=======
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "exam_results",
        filters={"department": department, "semester": semester, "result": result},
        search=search,
        search_fields=("name", "id", "department"),
    )


@router.post("", response_model=ExamResultResponse, status_code=status.HTTP_201_CREATED)
def publish_result(payload: ExamResultCreate, db: Database = Depends(get_db)):
    if not payload.id:
        raise HTTPException(status_code=400, detail="Student ID is required.")

    existing = get_document(db, "exam_results", payload.id)
    if existing:
        return update_document(db, "exam_results", payload.id, payload.model_dump())

    return insert_document(db, "exam_results", payload.model_dump())
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
