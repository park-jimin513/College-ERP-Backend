from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import (
    delete_document,
    insert_document,
    list_documents,
    next_sequence,
)
from app.schemas.notice import NoticeCreate, NoticeResponse

router = APIRouter(prefix="/notices", tags=["Notices"])


@router.get("", response_model=List[NoticeResponse])
def get_notices(
    search: Optional[str] = Query(None, description="Search notices by title or content"),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    audienceType: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "notices",
        filters={
            "category": category,
            "priority": priority,
            "audienceType": audienceType,
        },
        search=search,
        search_fields=("title", "content"),
        sort_by="created_at",
        descending=True,
    )


@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(payload: NoticeCreate, db: Database = Depends(get_db)):
    data = payload.model_dump()
    data["id"] = next_sequence(db, "notices")
    data["created_at"] = datetime.now(timezone.utc)
    return insert_document(db, "notices", data)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_notice(id: int, db: Database = Depends(get_db)):
    if not delete_document(db, "notices", id):
        raise HTTPException(status_code=404, detail=f"Notice '{id}' not found.")
    return {"message": f"Notice '{id}' deleted successfully."}
