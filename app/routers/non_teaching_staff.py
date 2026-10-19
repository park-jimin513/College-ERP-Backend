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
from app.schemas.staff import (
    NonTeachingStaffCreate,
    NonTeachingStaffResponse,
    NonTeachingStaffUpdate,
)
from app.routers.staff_documents import delete_staff_document, download_staff_document, upload_staff_document

router = APIRouter(prefix="/non-teaching-staff", tags=["Non-Teaching Staff"])
NON_TEACHING_DOCUMENT_TYPES = {
    "photo",
    "idProof",
    "experienceLetter",
    "appointmentLetter",
}


def generate_next_non_teaching_id(db: Database) -> str:
    max_num = max(
        (
            int(match.group(1))
            for row in mongo_collection("non_teaching_staff", db).find({}, {"id": 1})
            if (match := re.fullmatch(r"NTS(\d+)", str(row.get("id", ""))))
        ),
        default=3000,
    )
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
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "non_teaching_staff",
        filters={
            "area": area,
            "designation": designation,
            "employmentType": employmentType,
            "status": status,
        },
        search=search,
        search_fields=("name", "id", "area", "designation"),
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=NonTeachingStaffResponse)
def get_non_teaching_staff_by_id(id: str, db: Database = Depends(get_db)):
    staff = get_document(db, "non_teaching_staff", id)
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member with ID '{id}' not found.")
    return staff


@router.post("/{staff_id}/documents", response_model=NonTeachingStaffResponse)
async def upload_non_teaching_staff_document(
    staff_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
):
    return await upload_staff_document(
        db, "non_teaching_staff", staff_id, document_type, file, NON_TEACHING_DOCUMENT_TYPES
    )


@router.get("/{staff_id}/documents/{document_type}")
def get_non_teaching_staff_document(
    staff_id: str,
    document_type: str,
    db: Database = Depends(get_db),
):
    return download_staff_document(
        db, "non_teaching_staff", staff_id, document_type, NON_TEACHING_DOCUMENT_TYPES
    )


@router.delete("/{staff_id}/documents/{document_type}", response_model=NonTeachingStaffResponse)
def delete_non_teaching_staff_document(
    staff_id: str,
    document_type: str,
    db: Database = Depends(get_db),
):
    return delete_staff_document(
        db, "non_teaching_staff", staff_id, document_type, NON_TEACHING_DOCUMENT_TYPES
    )


@router.post("", response_model=NonTeachingStaffResponse, status_code=status.HTTP_201_CREATED)
def create_non_teaching_staff(payload: NonTeachingStaffCreate, db: Database = Depends(get_db)):
    staff_id = payload.id or generate_next_non_teaching_id(db)
    if get_document(db, "non_teaching_staff", staff_id):
        raise HTTPException(status_code=400, detail=f"Staff ID '{staff_id}' already exists.")
    data = payload.model_dump()
    data["id"] = staff_id
    return insert_document(db, "non_teaching_staff", data)


@router.put("/{id}", response_model=NonTeachingStaffResponse)
def update_non_teaching_staff(id: str, payload: NonTeachingStaffUpdate, db: Database = Depends(get_db)):
    staff = update_document(db, "non_teaching_staff", id, payload.model_dump(exclude_unset=True))
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member with ID '{id}' not found.")
    return staff


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_non_teaching_staff(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "non_teaching_staff", id):
        raise HTTPException(status_code=404, detail=f"Staff member with ID '{id}' not found.")
    return {"message": f"Staff '{id}' deleted successfully."}
