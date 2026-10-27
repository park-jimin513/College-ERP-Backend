from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.academic import AcademicProgram
from app.schemas.academic import AcademicProgramCreate, AcademicProgramUpdate, AcademicProgramResponse

router = APIRouter(prefix="/academics", tags=["Academics"])


@router.get("/programs", response_model=List[AcademicProgramResponse])
def get_academic_programs(
    search: Optional[str] = Query(None, description="Search programs by name or code"),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(AcademicProgram)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                AcademicProgram.name.ilike(s),
                AcademicProgram.id.ilike(s),
                AcademicProgram.department.ilike(s)
            )
        )
    if department:
        query = query.filter(AcademicProgram.department == department)
    if level:
        query = query.filter(AcademicProgram.level == level)
    if status:
        query = query.filter(AcademicProgram.status == status)

    return query.order_by(AcademicProgram.name.asc()).all()


@router.get("/programs/{id}", response_model=AcademicProgramResponse)
def get_academic_program_by_id(id: str, db: Session = Depends(get_db)):
    prog = db.query(AcademicProgram).filter(AcademicProgram.id == id).first()
    if not prog:
        raise HTTPException(status_code=404, detail=f"Academic program '{id}' not found.")
    return prog


@router.post("/programs", response_model=AcademicProgramResponse, status_code=status.HTTP_201_CREATED)
def create_academic_program(payload: AcademicProgramCreate, db: Session = Depends(get_db)):
    prog_id = payload.id or f"PRG-{payload.department.upper()}-{payload.level[:2].upper()}"
    existing = db.query(AcademicProgram).filter(AcademicProgram.id == prog_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Program ID '{prog_id}' already exists.")

    data = payload.model_dump()
    data["id"] = prog_id
    prog = AcademicProgram(**data)

    db.add(prog)
    db.commit()
    db.refresh(prog)
    sync_to_mongodb('academic_programs', prog.__dict__.copy())
    return prog


@router.put("/programs/{id}", response_model=AcademicProgramResponse)
def update_academic_program(id: str, payload: AcademicProgramUpdate, db: Session = Depends(get_db)):
    prog = db.query(AcademicProgram).filter(AcademicProgram.id == id).first()
    if not prog:
        raise HTTPException(status_code=404, detail=f"Academic program '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prog, field, value)

    db.commit()
    db.refresh(prog)
    return prog


@router.delete("/programs/{id}", status_code=status.HTTP_200_OK)
def delete_academic_program(id: str, db: Session = Depends(get_db)):
    prog = db.query(AcademicProgram).filter(AcademicProgram.id == id).first()
    if not prog:
        raise HTTPException(status_code=404, detail=f"Academic program '{id}' not found.")

    db.delete(prog)
    db.commit()
    sync_to_mongodb('academic_programs', {"id": id}, delete=True)
    return {"message": f"Academic program '{id}' deleted successfully."}
