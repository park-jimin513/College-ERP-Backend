from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.library import Book
from app.schemas.library import BookCreate, BookUpdate, BookResponse
=======

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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("", response_model=List[BookResponse])
def get_books(
    search: Optional[str] = Query(None, description="Search by title, author, or book ID"),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
<<<<<<< HEAD
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(s),
                Book.author.ilike(s),
                Book.id.ilike(s)
            )
        )
    if category:
        query = query.filter(Book.category == category)
    if status:
        query = query.filter(Book.status == status)

    return query.order_by(Book.id.asc()).all()


@router.get("/{id}", response_model=BookResponse)
def get_book_by_id(id: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    if not book:
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")
    return book


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
<<<<<<< HEAD
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    count = db.query(Book).count()
    book_id = payload.id or f"LIB-{1001 + count}"

    existing = db.query(Book).filter(Book.id == book_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Book ID '{book_id}' already exists.")

    data = payload.model_dump()
    data["id"] = book_id
    book = Book(**data)

    db.add(book)
    db.commit()
    db.refresh(book)
    sync_to_mongodb('library_books', book.__dict__.copy())
    return book


@router.put("/{id}", response_model=BookResponse)
def update_book(id: str, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return book


@router.delete("/{id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def delete_book(id: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")

    db.delete(book)
    db.commit()
    sync_to_mongodb('library_books', {"id": id}, delete=True)
=======
def delete_book(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "library_books", id):
        raise HTTPException(status_code=404, detail=f"Book '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Book '{id}' deleted successfully."}
