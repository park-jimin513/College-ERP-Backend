import logging
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import quote

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from gridfs import GridFSBucket
from gridfs.errors import NoFile
from pymongo.errors import PyMongoError
from pymongo.database import Database

from app.core.mongo import get_document, mongo_collection

logger = logging.getLogger(__name__)
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}


def _matches_file_signature(content: bytes, content_type: str) -> bool:
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "application/pdf": content.startswith(b"%PDF-"),
    }
    return signatures.get(content_type, False)


async def upload_staff_document(
    db: Database,
    collection_name: str,
    staff_id: str,
    document_type: str,
    file: UploadFile,
    allowed_document_types: set[str],
):
    staff = get_document(db, collection_name, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found.")
    if document_type not in allowed_document_types:
        raise HTTPException(status_code=400, detail="Unsupported staff document type.")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Staff documents must be JPG, PNG, or PDF files.")

    content = await file.read(MAX_DOCUMENT_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded document is empty.")
    if len(content) > MAX_DOCUMENT_SIZE:
        raise HTTPException(status_code=413, detail="Staff documents must be 5 MB or smaller.")
    if not _matches_file_signature(content, file.content_type):
        raise HTTPException(status_code=415, detail="The uploaded file content does not match its declared type.")

    bucket = GridFSBucket(db, bucket_name="staff_documents")
    filename = file.filename or document_type
    file_id = bucket.upload_from_stream(
        filename,
        BytesIO(content),
        metadata={
            "staff_id": staff_id,
            "staff_collection": collection_name,
            "document_type": document_type,
            "content_type": file.content_type,
        },
    )
    stored_documents = staff.get("documents")
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
        result = mongo_collection(collection_name, db).update_one(
            {"id": staff_id},
            {"$set": {**document_update, "updated_at": datetime.now(timezone.utc)}},
        )
    except PyMongoError:
        bucket.delete(file_id)
        raise
    if result.matched_count == 0:
        bucket.delete(file_id)
        raise HTTPException(status_code=404, detail="Staff record not found.")
    if isinstance(previous, dict) and previous.get("fileId"):
        try:
            bucket.delete(ObjectId(previous["fileId"]))
        except NoFile:
            logger.info("Replacing a missing stored staff document %s for %s.", document_type, staff_id)
        except (InvalidId, TypeError, ValueError):
            logger.warning("Could not remove an invalid prior document reference for %s.", staff_id)
    return get_document(db, collection_name, staff_id)


def download_staff_document(
    db: Database,
    collection_name: str,
    staff_id: str,
    document_type: str,
    allowed_document_types: set[str],
):
    staff = get_document(db, collection_name, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found.")
    if document_type not in allowed_document_types:
        raise HTTPException(status_code=400, detail="Unsupported staff document type.")

    documents = staff.get("documents")
    metadata = documents.get(document_type) if isinstance(documents, dict) else None
    if not isinstance(metadata, dict) or not metadata.get("fileId"):
        raise HTTPException(status_code=404, detail="Staff document not found.")
    try:
        file_id = ObjectId(metadata["fileId"])
        stream = GridFSBucket(db, bucket_name="staff_documents").open_download_stream(file_id)
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(status_code=404, detail="Staff document not found.")
    except NoFile as exc:
        raise HTTPException(status_code=404, detail="Staff document not found.") from exc

    filename = quote(metadata.get("filename", "staff-document"))
    return StreamingResponse(
        stream,
        media_type=metadata.get("contentType", "application/octet-stream"),
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{filename}"},
    )


def delete_staff_document(
    db: Database,
    collection_name: str,
    staff_id: str,
    document_type: str,
    allowed_document_types: set[str],
):
    staff = get_document(db, collection_name, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found.")
    if document_type not in allowed_document_types:
        raise HTTPException(status_code=400, detail="Unsupported staff document type.")

    documents = staff.get("documents")
    metadata = documents.get(document_type) if isinstance(documents, dict) else None
    if not isinstance(metadata, dict) or not metadata.get("fileId"):
        raise HTTPException(status_code=404, detail="Staff document not found.")
    try:
        file_id = ObjectId(metadata["fileId"])
    except (InvalidId, TypeError, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Staff document not found.") from exc

    bucket = GridFSBucket(db, bucket_name="staff_documents")
    try:
        bucket.delete(file_id)
    except NoFile as exc:
        raise HTTPException(status_code=404, detail="Staff document file not found.") from exc
    try:
        result = mongo_collection(collection_name, db).update_one(
            {"id": staff_id},
            {
                "$unset": {f"documents.{document_type}": ""},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )
    except PyMongoError:
        logger.exception("Failed to remove staff document metadata for %s.", staff_id)
        raise

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff record not found.")
    return get_document(db, collection_name, staff_id)
