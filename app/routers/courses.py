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
from app.schemas.academic import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=List[CourseResponse])
def get_courses(
    search: Optional[str] = Query(None, description="Search by name or code"),
    department: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "courses",
        filters={
            "department": department,
            "year": year,
            "semester": semester,
            "type": type,
            "status": status,
        },
        search=search,
        search_fields=("name", "id", "faculty"),
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=CourseResponse)
def get_course_by_id(id: str, db: Database = Depends(get_db)):
    course = get_document(db, "courses", id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")
    return course


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Database = Depends(get_db)):
    if not payload.id:
        raise HTTPException(status_code=400, detail="Course code / ID is required (e.g. CS101).")
    if get_document(db, "courses", payload.id):
        raise HTTPException(status_code=400, detail=f"Course ID '{payload.id}' already exists.")
    return insert_document(db, "courses", payload.model_dump())


@router.put("/{id}", response_model=CourseResponse)
def update_course(id: str, payload: CourseUpdate, db: Database = Depends(get_db)):
    course = update_document(db, "courses", id, payload.model_dump(exclude_unset=True))
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")
    return course


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_course(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "courses", id):
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")
    return {"message": f"Course '{id}' deleted successfully."}
