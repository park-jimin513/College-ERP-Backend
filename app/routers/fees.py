from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import (
    delete_document,
    get_document,
    insert_document,
    list_documents,
    update_document,
)
from app.schemas.fee import FeeRecordCreate, FeeRecordResponse, FeeRecordUpdate

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("", response_model=List[FeeRecordResponse])
def get_fee_records(
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    department: Optional[str] = Query(None),
    feeType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "fee_records",
        filters={"department": department, "feeType": feeType, "status": status},
        search=search,
        search_fields=("name", "id", "department"),
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=FeeRecordResponse)
def get_fee_record_by_id(id: str, db: Database = Depends(get_db)):
    record = get_document(db, "fee_records", id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Fee record for '{id}' not found.")
    return record


@router.post("", response_model=FeeRecordResponse, status_code=status.HTTP_201_CREATED)
def record_fee(payload: FeeRecordCreate, db: Database = Depends(get_db)):
    if not payload.id:
        raise HTTPException(status_code=400, detail="Student ID / Record ID is required.")

    if get_document(db, "fee_records", payload.id):
        return update_document(db, "fee_records", payload.id, payload.model_dump())
    return insert_document(db, "fee_records", payload.model_dump())


@router.put("/{id}", response_model=FeeRecordResponse)
def update_fee_record(id: str, payload: FeeRecordUpdate, db: Database = Depends(get_db)):
    record = update_document(db, "fee_records", id, payload.model_dump(exclude_unset=True))
    if not record:
        raise HTTPException(status_code=404, detail=f"Fee record for '{id}' not found.")
    return record


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_fee_record(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "fee_records", id):
        raise HTTPException(status_code=404, detail=f"Fee record for '{id}' not found.")
    return {"message": f"Fee record '{id}' deleted successfully."}
