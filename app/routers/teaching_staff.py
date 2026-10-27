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
    if not staff:
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")
    return staff


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
    return staff


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_teaching_staff(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "teaching_staff", id):
        raise HTTPException(status_code=404, detail=f"Faculty member with ID '{id}' not found.")
    return {"message": f"Faculty '{id}' deleted successfully."}
