from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from app.schemas.library import BookCreate, BookResponse, BookUpdate

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("", response_model=List[BookResponse])
def get_books(
    search: Optional[str] = Query(None, description="Search by title, author, or book ID"),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "library_books",
        filters={"category": category, "status": status},
        search=search,
        search_fields=("title", "author", "id"),
    )


@router.get("/{id}", response_model=BookResponse)
def get_book_by_id(id: str, db: Database = Depends(get_db)):
    book = get_document(db, "library_books", id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")
    return book


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Database = Depends(get_db)):
    count = mongo_collection("library_books", db).count_documents({})
    book_id = payload.id or f"LIB-{1001 + count}"
    if get_document(db, "library_books", book_id):
        raise HTTPException(status_code=400, detail=f"Book ID '{book_id}' already exists.")
    data = payload.model_dump()
    data["id"] = book_id
    return insert_document(db, "library_books", data)


@router.put("/{id}", response_model=BookResponse)
def update_book(id: str, payload: BookUpdate, db: Database = Depends(get_db)):
    book = update_document(db, "library_books", id, payload.model_dump(exclude_unset=True))
    if not book:
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")
    return book


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_book(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "library_books", id):
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")
    return {"message": f"Book '{id}' deleted successfully."}
