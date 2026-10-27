from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import (
    delete_document,
    get_document,
    insert_document,
    list_documents,
    mongo_collection,
    update_document,
)
from app.schemas.examination import ExaminationCreate, ExaminationResponse, ExaminationUpdate

router = APIRouter(prefix="/examinations", tags=["Examinations"])


@router.get("", response_model=List[ExaminationResponse])
def get_examinations(
    search: Optional[str] = Query(None, description="Search by exam name or department"),
    department: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "examinations",
        filters={"department": department, "type": type, "status": status},
        search=search,
        search_fields=("name", "department", "subjects"),
    )


@router.get("/{id}", response_model=ExaminationResponse)
def get_examination_by_id(id: str, db: Database = Depends(get_db)):
    examination = get_document(db, "examinations", id)
    if not examination:
        raise HTTPException(status_code=404, detail=f"Examination '{id}' not found.")
    return examination


@router.post("", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def create_examination(payload: ExaminationCreate, db: Database = Depends(get_db)):
    count = mongo_collection("examinations", db).count_documents({})
    examination_id = payload.id or f"EXM-{901 + count}"
    if get_document(db, "examinations", examination_id):
        raise HTTPException(status_code=400, detail=f"Exam ID '{examination_id}' already exists.")
    data = payload.model_dump()
    data["id"] = examination_id
    return insert_document(db, "examinations", data)


@router.put("/{id}", response_model=ExaminationResponse)
def update_examination(id: str, payload: ExaminationUpdate, db: Database = Depends(get_db)):
    examination = update_document(db, "examinations", id, payload.model_dump(exclude_unset=True))
    if not examination:
        raise HTTPException(status_code=404, detail=f"Examination '{id}' not found.")
    return examination


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_examination(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "examinations", id):
        raise HTTPException(status_code=404, detail=f"Examination '{id}' not found.")
    return {"message": f"Examination '{id}' deleted successfully."}
