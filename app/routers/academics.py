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
from app.schemas.academic import (
    AcademicProgramCreate,
    AcademicProgramResponse,
    AcademicProgramUpdate,
)

router = APIRouter(prefix="/academics", tags=["Academics"])


@router.get("/programs", response_model=List[AcademicProgramResponse])
def get_academic_programs(
    search: Optional[str] = Query(None, description="Search programs by name or code"),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "academic_programs",
        filters={"department": department, "level": level, "status": status},
        search=search,
        search_fields=("name", "id", "department"),
        sort_by="name",
    )


@router.get("/programs/{id}", response_model=AcademicProgramResponse)
def get_academic_program_by_id(id: str, db: Database = Depends(get_db)):
    program = get_document(db, "academic_programs", id)
    if not program:
        raise HTTPException(status_code=404, detail=f"Academic program '{id}' not found.")
    return program


@router.post("/programs", response_model=AcademicProgramResponse, status_code=status.HTTP_201_CREATED)
def create_academic_program(payload: AcademicProgramCreate, db: Database = Depends(get_db)):
    program_id = payload.id or f"PRG-{payload.department.upper()}-{payload.level[:2].upper()}"
    if get_document(db, "academic_programs", program_id):
        raise HTTPException(status_code=400, detail=f"Program ID '{program_id}' already exists.")
    data = payload.model_dump()
    data["id"] = program_id
    return insert_document(db, "academic_programs", data)


@router.put("/programs/{id}", response_model=AcademicProgramResponse)
def update_academic_program(id: str, payload: AcademicProgramUpdate, db: Database = Depends(get_db)):
    program = update_document(db, "academic_programs", id, payload.model_dump(exclude_unset=True))
    if not program:
        raise HTTPException(status_code=404, detail=f"Academic program '{id}' not found.")
    return program


@router.delete("/programs/{id}", status_code=status.HTTP_200_OK)
def delete_academic_program(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "academic_programs", id):
        raise HTTPException(status_code=404, detail=f"Academic program '{id}' not found.")
    return {"message": f"Academic program '{id}' deleted successfully."}
