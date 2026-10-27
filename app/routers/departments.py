from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.academic import Department
from app.schemas.academic import DepartmentCreate, DepartmentUpdate, DepartmentResponse
=======

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import (
    delete_document,
    get_document,
    insert_document,
    list_documents,
    update_document,
)
from app.schemas.academic import DepartmentCreate, DepartmentResponse, DepartmentUpdate
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
def get_departments(
    search: Optional[str] = Query(None, description="Search by name or code"),
    status: Optional[str] = Query(None),
<<<<<<< HEAD
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
=======
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "departments",
        filters={"status": status},
        search=search,
        search_fields=("name", "code", "hod"),
        sort_by="name",
    )


@router.get("/{id}", response_model=DepartmentResponse)
def get_department_by_id(id: str, db: Database = Depends(get_db)):
    department = get_document(db, "departments", id)
    if not department:
        raise HTTPException(status_code=404, detail=f"Department '{id}' not found.")
    return department


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, db: Database = Depends(get_db)):
    department_id = payload.id or f"DEP-{payload.code.upper().replace(' ', '')}"
    if get_document(db, "departments", department_id):
        raise HTTPException(status_code=400, detail=f"Department ID '{department_id}' already exists.")
    data = payload.model_dump()
    data["id"] = department_id
    return insert_document(db, "departments", data)


@router.put("/{id}", response_model=DepartmentResponse)
def update_department(id: str, payload: DepartmentUpdate, db: Database = Depends(get_db)):
    department = update_document(db, "departments", id, payload.model_dump(exclude_unset=True))
    if not department:
        raise HTTPException(status_code=404, detail=f"Department '{id}' not found.")
    return department


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_department(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "departments", id):
        raise HTTPException(status_code=404, detail=f"Department '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Department '{id}' deleted successfully."}
