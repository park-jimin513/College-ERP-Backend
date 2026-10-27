from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import (
    delete_document,
    insert_document,
    list_documents,
    mongo_collection,
    update_document,
)
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentStatusUpdate

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponse])
def get_documents(
    search: Optional[str] = Query(None, description="Search by document name, owner or ID"),
    ownerType: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "documents",
        filters={"ownerType": ownerType, "category": category, "status": status},
        search=search,
        search_fields=("name", "owner", "id"),
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Database = Depends(get_db)):
    count = mongo_collection("documents", db).count_documents({})
    data = payload.model_dump()
    data["id"] = payload.id or f"DOC-{5001 + count}"
    if not data.get("uploadedOn"):
        data["uploadedOn"] = datetime.now(timezone.utc).strftime("%d %b %Y")
    return insert_document(db, "documents", data)


@router.patch("/{id}/status", response_model=DocumentResponse)
def update_document_status(id: str, payload: DocumentStatusUpdate, db: Database = Depends(get_db)):
    document = update_document(db, "documents", id, {"status": payload.status})
    if not document:
        raise HTTPException(status_code=404, detail=f"Document '{id}' not found.")
    return document


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_document_by_id(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "documents", id):
        raise HTTPException(status_code=404, detail=f"Document '{id}' not found.")
    return {"message": f"Document '{id}' deleted successfully."}
