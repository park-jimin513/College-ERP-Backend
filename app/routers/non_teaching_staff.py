from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.staff import NonTeachingStaff
from app.schemas.staff import NonTeachingStaffCreate, NonTeachingStaffUpdate, NonTeachingStaffResponse

router = APIRouter(prefix="/non-teaching-staff", tags=["Non-Teaching Staff"])


def generate_next_non_teaching_id(db: Session) -> str:
    staff_members = db.query(NonTeachingStaff.id).all()
    max_num = 3000
    for (s_id,) in staff_members:
        if s_id and s_id.startswith("NTS"):
            try:
                num = int(s_id.replace("NTS", ""))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"NTS{max_num + 1}"


@router.get("", response_model=List[NonTeachingStaffResponse])
def get_non_teaching_staff(
    search: Optional[str] = Query(None, description="Search by name, ID, area or designation"),
    area: Optional[str] = Query(None),
    designation: Optional[str] = Query(None),
    employmentType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(NonTeachingStaff)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                NonTeachingStaff.name.ilike(s),
                NonTeachingStaff.id.ilike(s),
                NonTeachingStaff.area.ilike(s),
                NonTeachingStaff.designation.ilike(s)
            )
        )
    if area:
        query = query.filter(NonTeachingStaff.area == area)
    if designation:
        query = query.filter(NonTeachingStaff.designation == designation)
    if employmentType:
        query = query.filter(NonTeachingStaff.employmentType == employmentType)
    if status:
        query = query.filter(NonTeachingStaff.status == status)

    return query.order_by(NonTeachingStaff.id.asc()).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=NonTeachingStaffResponse)
def get_non_teaching_staff_by_id(id: str, db: Session = Depends(get_db)):
    staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member with ID '{id}' not found.")
    return staff


@router.post("", response_model=NonTeachingStaffResponse, status_code=status.HTTP_201_CREATED)
def create_non_teaching_staff(payload: NonTeachingStaffCreate, db: Session = Depends(get_db)):
    staff_id = payload.id or generate_next_non_teaching_id(db)
    
    existing = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == staff_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Staff ID '{staff_id}' already exists.")

    data = payload.model_dump()
    data["id"] = staff_id
    new_staff = NonTeachingStaff(**data)

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    sync_to_mongodb('non_teaching_staff', new_staff.__dict__.copy())
    return new_staff


@router.put("/{id}", response_model=NonTeachingStaffResponse)
def update_non_teaching_staff(id: str, payload: NonTeachingStaffUpdate, db: Session = Depends(get_db)):
    staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member with ID '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_non_teaching_staff(id: str, db: Session = Depends(get_db)):
    staff = db.query(NonTeachingStaff).filter(NonTeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member with ID '{id}' not found.")

    db.delete(staff)
    db.commit()
    sync_to_mongodb('non_teaching_staff', {"id": id}, delete=True)
    return {"message": f"Staff '{id}' deleted successfully."}
