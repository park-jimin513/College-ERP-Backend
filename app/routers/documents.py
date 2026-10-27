from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentStatusUpdate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponse])
def get_documents(
    search: Optional[str] = Query(None, description="Search by document name, owner or ID"),
    ownerType: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Document)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Document.name.ilike(s),
                Document.owner.ilike(s),
                Document.id.ilike(s)
            )
        )
    if ownerType:
        query = query.filter(Document.ownerType == ownerType)
    if category:
        query = query.filter(Document.category == category)
    if status:
        query = query.filter(Document.status == status)

    return query.order_by(Document.id.asc()).all()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    count = db.query(Document).count()
    doc_id = payload.id or f"DOC-{5001 + count}"
    
    data = payload.model_dump()
    data["id"] = doc_id
    if not data.get("uploadedOn"):
        data["uploadedOn"] = datetime.utcnow().strftime("%d %b %Y")

    doc = Document(**data)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    sync_to_mongodb('documents', doc.__dict__.copy())
    return doc


@router.patch("/{id}/status", response_model=DocumentResponse)
def update_document_status(id: str, payload: DocumentStatusUpdate, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{id}' not found.")

    doc.status = payload.status
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{id}' not found.")

    db.delete(doc)
    db.commit()
    sync_to_mongodb('documents', {"id": id}, delete=True)
    return {"message": f"Document '{id}' deleted successfully."}
