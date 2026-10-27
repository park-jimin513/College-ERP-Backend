from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.examination import Examination
from app.schemas.examination import ExaminationCreate, ExaminationUpdate, ExaminationResponse

router = APIRouter(prefix="/examinations", tags=["Examinations"])


@router.get("", response_model=List[ExaminationResponse])
def get_examinations(
    search: Optional[str] = Query(None, description="Search by exam name or department"),
    department: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
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
    return {"message": f"Examination '{id}' deleted successfully."}
