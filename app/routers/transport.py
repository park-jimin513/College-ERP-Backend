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
from app.schemas.transport import (
    TransportVehicleCreate,
    TransportVehicleResponse,
    TransportVehicleUpdate,
)

router = APIRouter(prefix="/transport", tags=["Transport"])


@router.get("", response_model=List[TransportVehicleResponse])
def get_transport_vehicles(
    search: Optional[str] = Query(None, description="Search by vehicle number, route, or driver"),
    route: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Database = Depends(get_db),
):
    return list_documents(
        db,
        "transport_vehicles",
        filters={"route": route, "status": status},
        search=search,
        search_fields=("vehicle", "route", "driver", "id"),
    )


@router.get("/{id}", response_model=TransportVehicleResponse)
def get_transport_vehicle_by_id(id: str, db: Database = Depends(get_db)):
    vehicle = get_document(db, "transport_vehicles", id)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")
    return vehicle


@router.post("", response_model=TransportVehicleResponse, status_code=status.HTTP_201_CREATED)
def create_transport_vehicle(payload: TransportVehicleCreate, db: Database = Depends(get_db)):
    count = mongo_collection("transport_vehicles", db).count_documents({})
    vehicle_id = payload.id or f"VEH-{count + 1:02d}"
    if get_document(db, "transport_vehicles", vehicle_id):
        raise HTTPException(status_code=400, detail=f"Vehicle ID '{vehicle_id}' already exists.")
    data = payload.model_dump()
    data["id"] = vehicle_id
    return insert_document(db, "transport_vehicles", data)


@router.put("/{id}", response_model=TransportVehicleResponse)
def update_transport_vehicle(id: str, payload: TransportVehicleUpdate, db: Database = Depends(get_db)):
    vehicle = update_document(db, "transport_vehicles", id, payload.model_dump(exclude_unset=True))
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")
    return vehicle


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_transport_vehicle(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "transport_vehicles", id):
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")
    return {"message": f"Vehicle '{id}' deleted successfully."}
