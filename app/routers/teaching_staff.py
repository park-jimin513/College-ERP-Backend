from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.staff import TeachingStaff
from app.schemas.staff import TeachingStaffCreate, TeachingStaffUpdate, TeachingStaffResponse

router = APIRouter(prefix="/teaching-staff", tags=["Teaching Staff"])


def generate_next_teaching_staff_id(db: Session) -> str:
    staff_members = db.query(TeachingStaff.id).all()
    max_num = 2000
    for (s_id,) in staff_members:
        if s_id and s_id.startswith("EMP"):
            try:
                num = int(s_id.replace("EMP", ""))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"EMP{max_num + 1}"


@router.get("", response_model=List[TeachingStaffResponse])
def get_teaching_staff(
    search: Optional[str] = Query(None, description="Search by name, ID, department or subject"),
    department: Optional[str] = Query(None),
    designation: Optional[str] = Query(None),
    employmentType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(TeachingStaff)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                TeachingStaff.name.ilike(s),
                TeachingStaff.id.ilike(s),
                TeachingStaff.department.ilike(s),
                TeachingStaff.subjects.ilike(s)
            )
        )
    if department:
        query = query.filter(TeachingStaff.department == department)
    if designation:
        query = query.filter(TeachingStaff.designation == designation)
    if employmentType:
        query = query.filter(TeachingStaff.employmentType == employmentType)
    if status:
        query = query.filter(TeachingStaff.status == status)

    return query.order_by(TeachingStaff.id.asc()).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=TeachingStaffResponse)
def get_teaching_staff_by_id(id: str, db: Session = Depends(get_db)):
    staff = db.query(TeachingStaff).filter(TeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")
    return staff


@router.post("", response_model=TeachingStaffResponse, status_code=status.HTTP_201_CREATED)
def create_teaching_staff(payload: TeachingStaffCreate, db: Session = Depends(get_db)):
    staff_id = payload.id or generate_next_teaching_staff_id(db)
    
    existing = db.query(TeachingStaff).filter(TeachingStaff.id == staff_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Faculty ID '{staff_id}' already exists.")

    data = payload.model_dump()
    data["id"] = staff_id
    new_staff = TeachingStaff(**data)

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    sync_to_mongodb('teaching_staff', new_staff.__dict__.copy())
    return new_staff


@router.put("/{id}", response_model=TeachingStaffResponse)
def update_teaching_staff(id: str, payload: TeachingStaffUpdate, db: Session = Depends(get_db)):
    staff = db.query(TeachingStaff).filter(TeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_teaching_staff(id: str, db: Session = Depends(get_db)):
    staff = db.query(TeachingStaff).filter(TeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")

    db.delete(staff)
    db.commit()
    sync_to_mongodb('teaching_staff', {"id": id}, delete=True)
    return {"message": f"Faculty '{id}' deleted successfully."}
