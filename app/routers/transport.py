from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.mongo import sync_to_mongodb
from app.models.transport import TransportVehicle
from app.schemas.transport import TransportVehicleCreate, TransportVehicleUpdate, TransportVehicleResponse

router = APIRouter(prefix="/transport", tags=["Transport"])


@router.get("", response_model=List[TransportVehicleResponse])
def get_transport_vehicles(
    search: Optional[str] = Query(None, description="Search by vehicle number, route, or driver"),
    route: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
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
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")
    return vehicle


@router.post("", response_model=TransportVehicleResponse, status_code=status.HTTP_201_CREATED)
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
    return vehicle


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_transport_vehicle(id: str, db: Session = Depends(get_db)):
    vehicle = db.query(TransportVehicle).filter(TransportVehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle '{id}' not found.")

    db.delete(vehicle)
    db.commit()
    sync_to_mongodb('transport_vehicles', {"id": id}, delete=True)
    return {"message": f"Vehicle '{id}' deleted successfully."}
