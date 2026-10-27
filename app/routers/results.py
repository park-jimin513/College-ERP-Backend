from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import get_document, insert_document, list_documents, update_document
from app.schemas.examination import ExamResultCreate, ExamResultResponse

router = APIRouter(prefix="/results", tags=["Results"])


@router.get("", response_model=List[ExamResultResponse])
def get_results(
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    department: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
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
