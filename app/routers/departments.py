from typing import List, Optional

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

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
def get_departments(
    search: Optional[str] = Query(None, description="Search by name or code"),
    status: Optional[str] = Query(None),
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
    return {"message": f"Department '{id}' deleted successfully."}
