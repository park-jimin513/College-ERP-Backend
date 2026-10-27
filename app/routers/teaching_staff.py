<<<<<<< HEAD
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
=======
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import (
    delete_document,
    get_document,
    insert_document,
    list_documents,
    mongo_collection,
    update_document,
)
from app.schemas.staff import TeachingStaffCreate, TeachingStaffResponse, TeachingStaffUpdate
from app.routers.staff_documents import delete_staff_document, download_staff_document, upload_staff_document

router = APIRouter(prefix="/teaching-staff", tags=["Teaching Staff"])
TEACHING_DOCUMENT_TYPES = {
    "photo",
    "idProof",
    "resume",
    "degreeCert",
    "experienceCert",
    "appointmentLetter",
}


def generate_next_teaching_staff_id(db: Database) -> str:
    max_num = max(
        (
            int(match.group(1))
            for row in mongo_collection("teaching_staff", db).find({}, {"id": 1})
            if (match := re.fullmatch(r"EMP(\d+)", str(row.get("id", ""))))
        ),
        default=2000,
    )
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
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
<<<<<<< HEAD
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
=======
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "teaching_staff",
        filters={
            "department": department,
            "designation": designation,
            "employmentType": employmentType,
            "status": status,
        },
        search=search,
        search_fields=("name", "id", "department", "subjects"),
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=TeachingStaffResponse)
def get_teaching_staff_by_id(id: str, db: Database = Depends(get_db)):
    staff = get_document(db, "teaching_staff", id)
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")
    return staff


<<<<<<< HEAD
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
=======
@router.post("/{staff_id}/documents", response_model=TeachingStaffResponse)
async def upload_teaching_staff_document(
    staff_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
):
    return await upload_staff_document(
        db, "teaching_staff", staff_id, document_type, file, TEACHING_DOCUMENT_TYPES
    )


@router.get("/{staff_id}/documents/{document_type}")
def get_teaching_staff_document(
    staff_id: str,
    document_type: str,
    db: Database = Depends(get_db),
):
    return download_staff_document(
        db, "teaching_staff", staff_id, document_type, TEACHING_DOCUMENT_TYPES
    )


@router.delete("/{staff_id}/documents/{document_type}", response_model=TeachingStaffResponse)
def delete_teaching_staff_document(
    staff_id: str,
    document_type: str,
    db: Database = Depends(get_db),
):
    return delete_staff_document(
        db, "teaching_staff", staff_id, document_type, TEACHING_DOCUMENT_TYPES
    )


@router.post("", response_model=TeachingStaffResponse, status_code=status.HTTP_201_CREATED)
def create_teaching_staff(payload: TeachingStaffCreate, db: Database = Depends(get_db)):
    staff_id = payload.id or generate_next_teaching_staff_id(db)
    if get_document(db, "teaching_staff", staff_id):
        raise HTTPException(status_code=400, detail=f"Faculty ID '{staff_id}' already exists.")
    data = payload.model_dump()
    data["id"] = staff_id
    return insert_document(db, "teaching_staff", data)


@router.put("/{id}", response_model=TeachingStaffResponse)
def update_teaching_staff(id: str, payload: TeachingStaffUpdate, db: Database = Depends(get_db)):
    staff = update_document(db, "teaching_staff", id, payload.model_dump(exclude_unset=True))
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return staff


@router.delete("/{id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def delete_teaching_staff(id: str, db: Session = Depends(get_db)):
    staff = db.query(TeachingStaff).filter(TeachingStaff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")

    db.delete(staff)
    db.commit()
    sync_to_mongodb('teaching_staff', {"id": id}, delete=True)
=======
def delete_teaching_staff(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "teaching_staff", id):
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Faculty '{id}' deleted successfully."}
