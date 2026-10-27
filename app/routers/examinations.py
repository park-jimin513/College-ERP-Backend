from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.examination import Examination
from app.schemas.examination import ExaminationCreate, ExaminationUpdate, ExaminationResponse
=======

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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

router = APIRouter(prefix="/examinations", tags=["Examinations"])


@router.get("", response_model=List[ExaminationResponse])
def get_examinations(
    search: Optional[str] = Query(None, description="Search by exam name or department"),
    department: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
<<<<<<< HEAD
    db: Session = Depends(get_db)
):
    query = db.query(Examination)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Examination.name.ilike(s),
                Examination.department.ilike(s),
                Examination.subjects.ilike(s)
            )
        )
    if department:
        query = query.filter(Examination.department == department)
    if type:
        query = query.filter(Examination.type == type)
    if status:
        query = query.filter(Examination.status == status)

    return query.order_by(Examination.id.asc()).all()


@router.get("/{id}", response_model=ExaminationResponse)
def get_examination_by_id(id: str, db: Session = Depends(get_db)):
    exam = db.query(Examination).filter(Examination.id == id).first()
    if not exam:
        raise HTTPException(status_code=404, detail=f"Examination '{id}' not found.")
    return exam


@router.post("", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def create_examination(payload: ExaminationCreate, db: Session = Depends(get_db)):
    count = db.query(Examination).count()
    exam_id = payload.id or f"EXM-{901 + count}"
    
    existing = db.query(Examination).filter(Examination.id == exam_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Exam ID '{exam_id}' already exists.")

    data = payload.model_dump()
    data["id"] = exam_id
    exam = Examination(**data)

    db.add(exam)
    db.commit()
    db.refresh(exam)
    sync_to_mongodb('examinations', exam.__dict__.copy())
    return exam


@router.put("/{id}", response_model=ExaminationResponse)
def update_examination(id: str, payload: ExaminationUpdate, db: Session = Depends(get_db)):
    exam = db.query(Examination).filter(Examination.id == id).first()
    if not exam:
        raise HTTPException(status_code=404, detail=f"Examination '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)

    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_examination(id: str, db: Session = Depends(get_db)):
    exam = db.query(Examination).filter(Examination.id == id).first()
    if not exam:
        raise HTTPException(status_code=404, detail=f"Examination '{id}' not found.")

    db.delete(exam)
    db.commit()
    sync_to_mongodb('examinations', {"id": id}, delete=True)
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Examination '{id}' deleted successfully."}
