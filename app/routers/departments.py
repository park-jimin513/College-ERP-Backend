from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.academic import Department
from app.schemas.academic import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
def get_departments(
    search: Optional[str] = Query(None, description="Search by name or code"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Department)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Department.name.ilike(s),
                Department.code.ilike(s),
                Department.hod.ilike(s)
            )
        )
    if status:
        query = query.filter(Department.status == status)

    return query.order_by(Department.name.asc()).all()


@router.get("/{id}", response_model=DepartmentResponse)
def get_department_by_id(id: str, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department '{id}' not found.")
    return dept


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    dept_id = payload.id or f"DEP-{payload.code.upper().replace(' ', '')}"
    existing = db.query(Department).filter(Department.id == dept_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Department ID '{dept_id}' already exists.")

    data = payload.model_dump()
    data["id"] = dept_id
    dept = Department(**data)

    db.add(dept)
    db.commit()
    db.refresh(dept)
    sync_to_mongodb('departments', dept.__dict__.copy())
    return dept


@router.put("/{id}", response_model=DepartmentResponse)
def update_department(id: str, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dept, field, value)

    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_department(id: str, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department '{id}' not found.")

    db.delete(dept)
    db.commit()
    sync_to_mongodb('departments', {"id": id}, delete=True)
    return {"message": f"Department '{id}' deleted successfully."}
