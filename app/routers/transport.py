from typing import List, Optional
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.transport import TransportVehicle
from app.schemas.transport import TransportVehicleCreate, TransportVehicleUpdate, TransportVehicleResponse
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
from app.schemas.transport import (
    TransportVehicleCreate,
    TransportVehicleResponse,
    TransportVehicleUpdate,
)
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

router = APIRouter(prefix="/transport", tags=["Transport"])


@router.get("", response_model=List[TransportVehicleResponse])
def get_transport_vehicles(
    search: Optional[str] = Query(None, description="Search by vehicle number, route, or driver"),
    route: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
<<<<<<< HEAD
    db: Session = Depends(get_db)
):
    query = db.query(TransportVehicle)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                TransportVehicle.vehicle.ilike(s),
                TransportVehicle.route.ilike(s),
                TransportVehicle.driver.ilike(s),
                TransportVehicle.id.ilike(s)
            )
        )
    if route:
        query = query.filter(TransportVehicle.route == route)
    if status:
        query = query.filter(TransportVehicle.status == status)

    return query.order_by(TransportVehicle.id.asc()).all()


@router.get("/{id}", response_model=TransportVehicleResponse)
def get_transport_vehicle_by_id(id: str, db: Session = Depends(get_db)):
    vehicle = db.query(TransportVehicle).filter(TransportVehicle.id == id).first()
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")
    return vehicle


@router.post("", response_model=TransportVehicleResponse, status_code=status.HTTP_201_CREATED)
<<<<<<< HEAD
def create_transport_vehicle(payload: TransportVehicleCreate, db: Session = Depends(get_db)):
    count = db.query(TransportVehicle).count()
    vehicle_id = payload.id or f"VEH-{count + 1:02d}"

    existing = db.query(TransportVehicle).filter(TransportVehicle.id == vehicle_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Vehicle ID '{vehicle_id}' already exists.")

    data = payload.model_dump()
    data["id"] = vehicle_id
    vehicle = TransportVehicle(**data)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    sync_to_mongodb('transport_vehicles', vehicle.__dict__.copy())
    return vehicle


@router.put("/{id}", response_model=TransportVehicleResponse)
def update_transport_vehicle(id: str, payload: TransportVehicleUpdate, db: Session = Depends(get_db)):
    vehicle = db.query(TransportVehicle).filter(TransportVehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
=======
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
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return vehicle


@router.delete("/{id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def delete_transport_vehicle(id: str, db: Session = Depends(get_db)):
    vehicle = db.query(TransportVehicle).filter(TransportVehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")

    db.delete(vehicle)
    db.commit()
    sync_to_mongodb('transport_vehicles', {"id": id}, delete=True)
=======
def delete_transport_vehicle(id: str, db: Database = Depends(get_db)):
    if not delete_document(db, "transport_vehicles", id):
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return {"message": f"Vehicle '{id}' deleted successfully."}
