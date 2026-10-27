<<<<<<< HEAD
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
=======
import re
import logging
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import quote
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from gridfs import GridFSBucket
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile
from pymongo.errors import PyMongoError
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
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])
logger = logging.getLogger(__name__)
MAX_STUDENT_DOCUMENT_SIZE = 5 * 1024 * 1024
ALLOWED_STUDENT_DOCUMENT_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}


def _matches_document_type(content: bytes, content_type: str) -> bool:
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "application/pdf": content.startswith(b"%PDF-"),
    }
    return signatures.get(content_type, False)


def generate_next_student_id(db: Database) -> str:
    max_num = max(
        (
            int(match.group(1))
            for row in mongo_collection("students", db).find({}, {"id": 1})
            if (match := re.fullmatch(r"STU(\d+)", str(row.get("id", ""))))
        ),
        default=1000,
    )
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
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
<<<<<<< HEAD
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
=======
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "students",
        filters={"department": department, "batch": batch, "status": status, "feeStatus": feeStatus},
        search=search,
        search_fields=("name", "id", "email", "department"),
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=StudentResponse)
def get_student_by_id(id: str, db: Database = Depends(get_db)):
    student = get_document(db, "students", id)
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")
    return student


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
<<<<<<< HEAD
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
=======
def create_student(payload: StudentCreate, db: Database = Depends(get_db)):
    student_id = payload.id or generate_next_student_id(db)
    if get_document(db, "students", student_id):
        raise HTTPException(status_code=400, detail=f"Student ID '{student_id}' already exists.")
    student_data = payload.model_dump()
    student_data["id"] = student_id
    student_data["studentId"] = payload.studentId or student_id
    return insert_document(db, "students", student_data)


@router.post("/{student_id}/documents", response_model=StudentResponse)
async def upload_student_document(
    student_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
):
    student = get_document(db, "students", student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    if document_type not in {
        "photo",
        "idProof",
        "tenth",
        "twelfth",
        "transferCert",
        "migrationCert",
        "communityCert",
        "incomeCert",
        "allotmentLetter",
    }:
        raise HTTPException(status_code=400, detail="Unsupported student document type.")
    if file.content_type not in ALLOWED_STUDENT_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Student documents must be JPG, PNG, or PDF files.",
        )

    content = await file.read(MAX_STUDENT_DOCUMENT_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded document is empty.")
    if len(content) > MAX_STUDENT_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Student documents must be 5 MB or smaller.",
        )
    if not _matches_document_type(content, file.content_type):
        raise HTTPException(
            status_code=415,
            detail="The uploaded file content does not match its declared type.",
        )

    bucket = GridFSBucket(db, bucket_name="student_documents")
    filename = file.filename or f"{document_type}"
    file_id = bucket.upload_from_stream(
        filename,
        BytesIO(content),
        metadata={
            "student_id": student_id,
            "document_type": document_type,
            "content_type": file.content_type,
        },
    )
    stored_documents = student.get("documents")
    previous = stored_documents.get(document_type) if isinstance(stored_documents, dict) else None
    metadata = {
        "fileId": str(file_id),
        "filename": filename,
        "contentType": file.content_type,
        "size": len(content),
        "uploadedAt": datetime.now(timezone.utc).isoformat(),
    }
    document_update = (
        {f"documents.{document_type}": metadata}
        if isinstance(stored_documents, dict)
        else {"documents": {document_type: metadata}}
    )
    try:
        result = mongo_collection("students", db).update_one(
            {"id": student_id},
            {"$set": {**document_update, "updated_at": datetime.now(timezone.utc)}},
        )
    except PyMongoError:
        bucket.delete(file_id)
        raise
    if result.matched_count == 0:
        bucket.delete(file_id)
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    if isinstance(previous, dict) and previous.get("fileId"):
        try:
            bucket.delete(ObjectId(previous["fileId"]))
        except NoFile:
            logger.info("Replacing missing stored student document %s for student %s.", document_type, student_id)
        except (InvalidId, TypeError, ValueError):
            logger.warning("Could not remove invalid prior document reference for student %s.", student_id)
    return get_document(db, "students", student_id)


@router.get("/{student_id}/documents/{document_type}")
def download_student_document(
    student_id: str,
    document_type: str,
    db: Database = Depends(get_db),
):
    student = get_document(db, "students", student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    documents = student.get("documents")
    metadata = documents.get(document_type) if isinstance(documents, dict) else None
    if not isinstance(metadata, dict) or not metadata.get("fileId"):
        raise HTTPException(status_code=404, detail="Student document not found.")

    try:
        file_id = ObjectId(metadata["fileId"])
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(status_code=404, detail="Student document not found.")
    try:
        stream = GridFSBucket(db, bucket_name="student_documents").open_download_stream(file_id)
    except NoFile as exc:
        raise HTTPException(status_code=404, detail="Student document not found.") from exc

    filename = quote(metadata.get("filename", "student-document"))
    return StreamingResponse(
        stream,
        media_type=metadata.get("contentType", "application/octet-stream"),
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{filename}"},
    )


@router.delete("/{student_id}/documents/{document_type}", response_model=StudentResponse)
def delete_student_document(
    student_id: str,
    document_type: str,
    db: Database = Depends(get_db),
):
    student = get_document(db, "students", student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    documents = student.get("documents")
    metadata = documents.get(document_type) if isinstance(documents, dict) else None
    if not isinstance(metadata, dict) or not metadata.get("fileId"):
        raise HTTPException(status_code=404, detail="Student document not found.")

    try:
        file_id = ObjectId(metadata["fileId"])
    except (InvalidId, TypeError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Student document not found.") from exc

    bucket = GridFSBucket(db, bucket_name="student_documents")
    try:
        bucket.delete(file_id)
    except NoFile as exc:
        raise HTTPException(status_code=404, detail="Student document file not found.") from exc

    try:
        result = mongo_collection("students", db).update_one(
            {"id": student_id},
            {
                "$unset": {f"documents.{document_type}": ""},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )
    except PyMongoError:
        logger.exception("Failed to remove student document metadata for %s.", student_id)
        raise

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    return get_document(db, "students", student_id)


@router.put("/{id}", response_model=StudentResponse)
def update_student(id: str, payload: StudentUpdate, db: Database = Depends(get_db)):
    student = update_document(db, "students", id, payload.model_dump(exclude_unset=True))
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return student


@router.delete("/{id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def delete_student(id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")

    db.delete(student)
    db.commit()
    sync_to_mongodb('students', {"id": id}, delete=True)
=======
def delete_student(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "students", id):
        raise HTTPException(status_code=404, detail=f"Student with ID '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Student '{id}' deleted successfully."}
