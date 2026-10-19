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
from app.schemas.hostel import HostelRoomCreate, HostelRoomResponse, HostelRoomUpdate

router = APIRouter(prefix="/hostel", tags=["Hostel"])


@router.get("", response_model=List[HostelRoomResponse])
def get_hostel_rooms(
    search: Optional[str] = Query(None, description="Search by room number or block"),
    block: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "hostel_rooms",
        filters={"block": block, "status": status},
        search=search,
        search_fields=("room", "block", "id"),
        sort_by="room",
    )


@router.get("/{id}", response_model=HostelRoomResponse)
def get_hostel_room_by_id(id: str, db: Database = Depends(get_db)):
    room = get_document(db, "hostel_rooms", id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")
    return room


@router.post("", response_model=HostelRoomResponse, status_code=status.HTTP_201_CREATED)
def create_hostel_room(payload: HostelRoomCreate, db: Database = Depends(get_db)):
    room_id = payload.id or f"RM-{payload.room.replace(' ', '').upper()}"
    if get_document(db, "hostel_rooms", room_id):
        raise HTTPException(status_code=400, detail=f"Room ID '{room_id}' already exists.")
    data = payload.model_dump()
    data["id"] = room_id
    return insert_document(db, "hostel_rooms", data)


@router.put("/{id}", response_model=HostelRoomResponse)
def update_hostel_room(id: str, payload: HostelRoomUpdate, db: Database = Depends(get_db)):
    room = update_document(db, "hostel_rooms", id, payload.model_dump(exclude_unset=True))
    if not room:
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")
    return room


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_hostel_room(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "hostel_rooms", id):
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")
    return {"message": f"Hostel room '{id}' deleted successfully."}
