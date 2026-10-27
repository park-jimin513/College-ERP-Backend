from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.academic import Course
from app.schemas.academic import CourseCreate, CourseUpdate, CourseResponse
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
from app.schemas.academic import CourseCreate, CourseResponse, CourseUpdate
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

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
<<<<<<< HEAD
    db: Session = Depends(get_db)
):
    query = db.query(Course)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Course.name.ilike(s),
                Course.id.ilike(s),
                Course.faculty.ilike(s)
            )
        )
    if department:
        query = query.filter(Course.department == department)
    if year:
        query = query.filter(Course.year == year)
    if semester:
        query = query.filter(Course.semester == semester)
    if type:
        query = query.filter(Course.type == type)
    if status:
        query = query.filter(Course.status == status)

    return query.order_by(Course.id.asc()).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=CourseResponse)
def get_course_by_id(id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == id).first()
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")
    return course


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
<<<<<<< HEAD
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    if not payload.id:
        raise HTTPException(status_code=400, detail="Course code / ID is required (e.g. CS101).")

    existing = db.query(Course).filter(Course.id == payload.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Course ID '{payload.id}' already exists.")

    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    sync_to_mongodb('courses', course.__dict__.copy())
    return course


@router.put("/{id}", response_model=CourseResponse)
def update_course(id: str, payload: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return course


@router.delete("/{id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def delete_course(id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")

    db.delete(course)
    db.commit()
    sync_to_mongodb('courses', {"id": id}, delete=True)
=======
def delete_course(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "courses", id):
        raise HTTPException(status_code=404, detail=f"Course '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Course '{id}' deleted successfully."}
