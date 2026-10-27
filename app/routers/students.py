from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


def generate_next_student_id(db: Session) -> str:
    students = db.query(Student.id).all()
    max_num = 1000
    for (s_id,) in students:
        if s_id and s_id.startswith("STU"):
            try:
                num = int(s_id.replace("STU", ""))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"STU{max_num + 1}"


@router.get("", response_model=List[StudentResponse])
def get_students(
    search: Optional[str] = Query(None, description="Search by name, ID, email, or department"),
    department: Optional[str] = Query(None),
    batch: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    feeStatus: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Student)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Student.name.ilike(s),
                Student.id.ilike(s),
                Student.email.ilike(s),
                Student.department.ilike(s)
            )
        )
    if department:
        query = query.filter(Student.department == department)
    if batch:
        query = query.filter(Student.batch == batch)
    if status:
        query = query.filter(Student.status == status)
    if feeStatus:
        query = query.filter(Student.feeStatus == feeStatus)

    return query.order_by(Student.id.asc()).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=StudentResponse)
def get_student_by_id(id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")
    return student


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    student_id = payload.id or generate_next_student_id(db)
    
    existing = db.query(Student).filter(Student.id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Student ID '{student_id}' already exists.")

    student_data = payload.model_dump()
    student_data["id"] = student_id
    new_student = Student(**student_data)
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    sync_to_mongodb('students', new_student.__dict__.copy())
    return new_student


@router.put("/{id}", response_model=StudentResponse)
def update_student(id: str, payload: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_student(id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")

    db.delete(student)
    db.commit()
    sync_to_mongodb('students', {"id": id}, delete=True)
    return {"message": f"Student '{id}' deleted successfully."}
