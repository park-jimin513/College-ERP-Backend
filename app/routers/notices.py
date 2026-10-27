<<<<<<< HEAD
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.notice import Notice
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
from app.schemas.notice import NoticeCreate, NoticeResponse

router = APIRouter(prefix="/notices", tags=["Notices"])


@router.get("", response_model=List[NoticeResponse])
def get_notices(
    search: Optional[str] = Query(None, description="Search notices by title or content"),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    audienceType: Optional[str] = Query(None),
<<<<<<< HEAD
    db: Session = Depends(get_db)
):
    query = db.query(Notice)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Notice.title.ilike(s),
                Notice.content.ilike(s)
            )
        )
    if category:
        query = query.filter(Notice.category == category)
    if priority:
        query = query.filter(Notice.priority == priority)
    if audienceType:
        query = query.filter(Notice.audienceType == audienceType)

    return query.order_by(Notice.created_at.desc()).all()


@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(payload: NoticeCreate, db: Session = Depends(get_db)):
    notice = Notice(**payload.model_dump())
    db.add(notice)
    db.commit()
    db.refresh(notice)
    sync_to_mongodb('notices', notice.__dict__.copy())
    return notice


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_notice(id: int, db: Session = Depends(get_db)):
    notice = db.query(Notice).filter(Notice.id == id).first()
    if not notice:
        raise HTTPException(status_code=404, detail=f"Notice '{id}' not found.")

    db.delete(notice)
    db.commit()
    sync_to_mongodb('notices', {"id": id}, delete=True)
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Notice '{id}' deleted successfully."}
