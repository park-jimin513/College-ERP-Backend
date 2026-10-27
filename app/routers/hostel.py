from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.hostel import HostelRoom
from app.schemas.hostel import HostelRoomCreate, HostelRoomUpdate, HostelRoomResponse
=======

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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

router = APIRouter(prefix="/hostel", tags=["Hostel"])


@router.get("", response_model=List[HostelRoomResponse])
def get_hostel_rooms(
    search: Optional[str] = Query(None, description="Search by room number or block"),
    block: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
<<<<<<< HEAD
    db: Session = Depends(get_db)
):
    query = db.query(HostelRoom)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                HostelRoom.room.ilike(s),
                HostelRoom.block.ilike(s),
                HostelRoom.id.ilike(s)
            )
        )
    if block:
        query = query.filter(HostelRoom.block == block)
    if status:
        query = query.filter(HostelRoom.status == status)

    return query.order_by(HostelRoom.room.asc()).all()


@router.get("/{id}", response_model=HostelRoomResponse)
def get_hostel_room_by_id(id: str, db: Session = Depends(get_db)):
    room = db.query(HostelRoom).filter(HostelRoom.id == id).first()
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    if not room:
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")
    return room


@router.post("", response_model=HostelRoomResponse, status_code=status.HTTP_201_CREATED)
<<<<<<< HEAD
def create_hostel_room(payload: HostelRoomCreate, db: Session = Depends(get_db)):
    room_id = payload.id or f"RM-{payload.room.replace(' ', '').upper()}"

    existing = db.query(HostelRoom).filter(HostelRoom.id == room_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Room ID '{room_id}' already exists.")

    data = payload.model_dump()
    data["id"] = room_id
    room = HostelRoom(**data)

    db.add(room)
    db.commit()
    db.refresh(room)
    sync_to_mongodb('hostel_rooms', room.__dict__.copy())
    return room


@router.put("/{id}", response_model=HostelRoomResponse)
def update_hostel_room(id: str, payload: HostelRoomUpdate, db: Session = Depends(get_db)):
    room = db.query(HostelRoom).filter(HostelRoom.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return room


@router.delete("/{id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def delete_hostel_room(id: str, db: Session = Depends(get_db)):
    room = db.query(HostelRoom).filter(HostelRoom.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")

    db.delete(room)
    db.commit()
    sync_to_mongodb('hostel_rooms', {"id": id}, delete=True)
=======
def delete_hostel_room(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "hostel_rooms", id):
        raise HTTPException(status_code=404, detail=f"Hostel room '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Hostel room '{id}' deleted successfully."}
