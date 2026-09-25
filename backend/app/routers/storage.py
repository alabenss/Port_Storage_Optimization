from datetime import datetime
import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_database

from app.models.storage_zone import StorageZone
from app.models.storage_position import StoragePosition
from app.models.vehicle import Vehicle
from app.models.allocation import Allocation
from app.models.movement import Movement
from app.models.cargo_unit import CargoUnit

from app.schemas.storage import (
    ZoneResponse,
    PositionResponse,
    AllocationResponse,
    ZoneCreate,
    PositionCreate,
    ZoneUpdate,
    PositionUpdate
)

from app.services.placement_engine import PlacementEngine
from app.services.allocation_service import AllocationService
from app.services.multi_allocation_service import MultiAllocationService
from app.services.relocation_service import RelocationService
from app.services.storage_expansion import expand_package_storage


router = APIRouter()


# =========================================================
# GET ZONES
# =========================================================

@router.get(
    "/zones",
    response_model=list[ZoneResponse]
)
def get_zones(
    db: Session = Depends(get_database)
):

    return (
        db.query(StorageZone)
        .all()
    )


# =========================================================
# GET POSITIONS
# =========================================================

@router.get(
    "/positions",
    response_model=list[PositionResponse]
)
def get_positions(
    db: Session = Depends(get_database)
):

    return (
        db.query(StoragePosition)
        .all()
    )


# =========================================================
# OCCUPANCY
# =========================================================

@router.get("/occupancy")
def occupancy(
    db: Session = Depends(get_database)
):

    total = (
        db.query(StoragePosition)
        .count()
    )

    occupied = (
        db.query(StoragePosition)
        .filter(
            StoragePosition.occupied == True
        )
        .count()
    )

    return {
        "total_positions": total,
        "occupied": occupied,
        "available": total - occupied,
        "occupancy_percent": round(
            (occupied / total * 100)
            if total
            else 0,
            2
        )
    }


# =========================================================
# VEHICLE ALLOCATION
# =========================================================

@router.post(
    "/allocate/vehicle/{vehicle_id}",
    response_model=AllocationResponse
)
def allocate_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_database)
):

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    engine = PlacementEngine()

    position = engine.find_best_position(
        db,
        vehicle
    )

    if not position:

        raise HTTPException(
            status_code=400,
            detail="No available storage position"
        )

    service = AllocationService()

    return service.allocate_vehicle(
        db,
        vehicle,
        position
    )


# =========================================================
# CARGO ALLOCATION
# =========================================================

@router.post(
    "/allocate/cargo/{cargo_id}"
)
def allocate_cargo(
    cargo_id: int,
    db: Session = Depends(get_database)
):

    cargo = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.id == cargo_id
        )
        .first()
    )

    if not cargo:

        raise HTTPException(
            status_code=404,
            detail="Cargo not found"
        )

    service = MultiAllocationService()

    return service.allocate_large_cargo(
        db,
        cargo
    )


# =========================================================
# AI RECOMMENDATION PREVIEW ONLY
# =========================================================

@router.post(
    "/recommend/{cargo_id}"
)
def recommend_cargo(
    cargo_id: int,
    db: Session = Depends(get_database)
):

    cargo = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.id == cargo_id
        )
        .first()
    )


    if not cargo:

        raise HTTPException(
            status_code=404,
            detail="Cargo not found"
        )


    engine = PlacementEngine()


    plan = engine.calculate_multi_position_plan(
        db,
        cargo
    )


    return plan


# =========================================================
# ALLOCATE USING AI RECOMMENDATION
# =========================================================

@router.post(
    "/allocate/recommended/{cargo_id}"
)
def allocate_recommended_cargo(
    cargo_id: int,
    db: Session = Depends(get_database)
):

    cargo = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.id == cargo_id
        )
        .first()
    )

    if not cargo:

        raise HTTPException(
            status_code=404,
            detail="Cargo not found"
        )

    service = MultiAllocationService()

    # Use the already generated AI recommendation.
    # Do not recalculate a new placement during confirmation.
    ai_plan = PlacementEngine().calculate_multi_position_plan(
        db,
        cargo
    )

    return service.allocate_large_cargo(
        db,
        cargo,
        recommended_plan=ai_plan
    )


# =========================================================
# AI CARGO RELOCATION / RE-OPTIMIZATION
# =========================================================

@router.post(
    "/relocate/cargo/{cargo_id}"
)
def relocate_cargo(
    cargo_id: int,
    db: Session = Depends(get_database)
):

    cargo = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.id == cargo_id
        )
        .first()
    )

    if not cargo:

        raise HTTPException(
            status_code=404,
            detail="Cargo not found"
        )

    service = RelocationService()

    return service.relocate_cargo(
        db,
        cargo
    )


# =========================================================
# RELEASE ONE ALLOCATION
# =========================================================

@router.post(
    "/release/allocation/{allocation_id}"
)
def release_allocation(
    allocation_id: int,
    db: Session = Depends(get_database)
):

    allocation = (
        db.query(Allocation)
        .filter(
            Allocation.id == allocation_id
        )
        .first()
    )

    if not allocation:

        raise HTTPException(
            status_code=404,
            detail="Allocation not found"
        )

    service = AllocationService()

    return service.release_allocation(
        db,
        allocation
    )


# =========================================================
# RELEASE ALL STORAGE USED BY ONE CARGO
# =========================================================

@router.post(
    "/release/cargo/{cargo_id}"
)
def release_cargo(
    cargo_id: int,
    db: Session = Depends(get_database)
):

    cargo = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.id == cargo_id
        )
        .first()
    )

    if not cargo:

        raise HTTPException(
            status_code=404,
            detail="Cargo not found"
        )

    allocations = (
        db.query(Allocation)
        .filter(
            Allocation.cargo_id == cargo_id,
            Allocation.status == "ACTIVE"
        )
        .all()
    )

    if not allocations:

        return {
            "status": "NOT_ALLOCATED",
            "cargo_id": cargo.id,
            "reference": cargo.reference,
            "released_positions": []
        }

    released_positions = []

    try:

        for allocation in allocations:

            position = allocation.position

            if position:

                released_positions.append(
                    position.position_code
                )

                movement = Movement(
                    cargo_id=cargo.id,
                    from_position=position.position_code,
                    to_position=None,
                    action="RELEASED",
                    reason=(
                        f"Cargo {cargo.reference} released "
                        f"from {position.position_code}"
                    ),
                    performed_by="SYSTEM"
                )

                db.add(movement)

                position.occupied = False
                position.current_weight = 0

            allocation.status = "RELEASED"
            allocation.released_at = datetime.utcnow()

        cargo.status = "IMPORTED"

        db.commit()

    except Exception:

        db.rollback()
        raise

    return {
        "status": "CARGO_RELEASED",
        "cargo_id": cargo.id,
        "reference": cargo.reference,
        "released_allocations": len(allocations),
        "released_positions": released_positions,
        "cargo_status": cargo.status
    }


# =========================================================
# MOVEMENTS
# =========================================================

@router.get(
    "/movements"
)
def movements(
    db: Session = Depends(get_database)
):

    return (
        db.query(Movement)
        .order_by(
            Movement.created_at.desc()
        )
        .all()
    )




# =========================================================
# MANUAL CARGO ALLOCATION
# =========================================================

from pydantic import BaseModel


class ManualAllocationRequest(BaseModel):
    cargo_id: int
    position_id: int



@router.post("/allocate/manual")
def allocate_manual(
    data: ManualAllocationRequest,
    db: Session = Depends(get_database)
):

    cargo = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.id == data.cargo_id
        )
        .first()
    )

    if not cargo:
        raise HTTPException(
            status_code=404,
            detail="Cargo not found"
        )


    position = (
        db.query(StoragePosition)
        .filter(
            StoragePosition.id == data.position_id
        )
        .first()
    )

    if not position:
        raise HTTPException(
            status_code=404,
            detail="Position not found"
        )


    if position.occupied:
        raise HTTPException(
            status_code=400,
            detail="Position already occupied"
        )


    cargo_weight = cargo.weight or 0


    if (
        position.max_weight
        and cargo_weight > position.max_weight
    ):
        raise HTTPException(
            status_code=400,
            detail="Cargo weight exceeds position capacity"
        )


    allocation = Allocation(
        cargo_id=cargo.id,
        position_id=position.id,
        allocated_weight=cargo_weight,
        status="ACTIVE",
        allocation_method="MANUAL",
        reason="Manual operator allocation"
    )


    position.occupied = True
    position.current_weight = cargo_weight


    movement = Movement(
        cargo_id=cargo.id,
        from_position=None,
        to_position=position.position_code,
        action="ALLOCATED",
        reason=(
            f"Cargo {cargo.reference} manually "
            f"allocated to {position.position_code}"
        ),
        performed_by="OPERATOR"
    )


    db.add(allocation)
    db.add(movement)


    cargo.status = "STORED"


    try:

        db.commit()
        db.refresh(allocation)

    except Exception:

        db.rollback()
        raise


    return {

        "status": "MANUAL_ALLOCATION_COMPLETED",

        "allocation_id": allocation.id,

        "cargo": {
            "id": cargo.id,
            "reference": cargo.reference
        },

        "position": {
            "id": position.id,
            "code": position.position_code
        }

    }


# =========================================================
# RESET TEST STORAGE
# =========================================================

@router.delete(
    "/reset-test-storage"
)
def reset_test_storage(
    db: Session = Depends(get_database)
):

    db.query(Allocation).delete()

    positions = (
        db.query(StoragePosition)
        .all()
    )

    for position in positions:

        position.occupied = False
        position.current_weight = 0

    db.commit()

    return {
        "status": "STORAGE_RESET"
    }

@router.delete("/reset-full-storage")
def reset_full_storage(
    db: Session = Depends(get_database)
):

    db.query(StoragePosition).delete()
    db.query(StorageZone).delete()

    db.commit()

    return {
        "status": "FULL_STORAGE_RESET"
    }

@router.post("/expand-package-storage")
def expand_package(
    db: Session = Depends(get_database)
):

    return expand_package_storage(
        db,
        60
    )

@router.get("/debug/zones")
def debug_zones(
    db: Session = Depends(get_database)
):

    zones = db.query(StorageZone).all()

    return [
        {
            "id": z.id,
            "code": z.code,
            "name": z.name,
            "type": z.zone_type
        }
        for z in zones
    ]



# ADD THESE IMPORTS IN storage router




# =========================================================
# CREATE ZONE
# =========================================================

# =========================================================
# CREATE ZONE + AUTO GENERATE POSITIONS
# =========================================================

@router.post("/zones/create", response_model=ZoneResponse)
def create_zone(
    data: ZoneCreate,
    db: Session = Depends(get_database)
):


    # Coordinates are mandatory
    if data.latitude is None or data.longitude is None:

        raise HTTPException(
            status_code=400,
            detail="Latitude and longitude are required for zone creation"
        )



    zone = StorageZone(

        code=data.code,

        name=data.name,

        zone_type=data.zone_type,

        capacity=data.capacity,

        latitude=data.latitude,

        longitude=data.longitude

    )


    db.add(zone)

    db.commit()

    db.refresh(zone)



    # ===============================
    # AUTO GENERATE POSITIONS
    # ===============================


    capacity = int(data.capacity)



    if data.zone_type == "VEHICLE_YARD":

        prefix = "VEH"

        position_type = "VEHICLE_SLOT"



    elif data.zone_type == "CONTAINER_YARD":

        prefix = "CONT"

        position_type = "CONTAINER"



    elif data.zone_type == "PACKAGE_AREA":

        prefix = "PACK"

        position_type = "STORAGE_SLOT"



    else:

        prefix = "POS"

        position_type = "STORAGE_SLOT"




    columns = 10



    for i in range(capacity):


        row = i // columns

        col = i % columns



        position = StoragePosition(

            zone_id=zone.id,


            position_code=f"{prefix}-{i+1:03}",


            position_type=position_type,


            max_weight=10000,


            latitude=data.latitude + (row * 0.00005),


            longitude=data.longitude + (col * 0.00005),


            occupied=False

        )


        db.add(position)




    db.commit()

    db.refresh(zone)


    return zone

# =========================================================
# CREATE POSITION
# =========================================================

@router.post("/positions/create", response_model=PositionResponse)
def create_position(
    data: PositionCreate,
    db: Session = Depends(get_database)
):

    position = StoragePosition(
        zone_id=data.zone_id,
        position_code=data.position_code,
        position_type=data.position_type,
        max_weight=data.max_weight
    )

    db.add(position)
    db.commit()
    db.refresh(position)

    return position



# =========================================================
# DELETE ZONE
# =========================================================

@router.delete("/zones/{zone_id}")
def delete_zone(
    zone_id:int,
    db:Session=Depends(get_database)
):

    zone = db.query(StorageZone).filter(
        StorageZone.id==zone_id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    db.delete(zone)
    db.commit()

    return {"status":"ZONE_DELETED"}



# =========================================================
# DELETE POSITION
# =========================================================

@router.delete("/positions/{position_id}")
def delete_position(
    position_id:int,
    db:Session=Depends(get_database)
):

    position = db.query(StoragePosition).filter(
        StoragePosition.id==position_id
    ).first()

    if not position:
        raise HTTPException(
            status_code=404,
            detail="Position not found"
        )

    db.delete(position)
    db.commit()

    return {"status":"POSITION_DELETED"}





# =========================================================
# STORAGE ROUTER UPDATE PATCH
# Add this at the END of your existing storage.py router
# DO NOT replace your router file
# =========================================================


# =========================================================
# UPDATE ZONE
# =========================================================
# =========================================================
# UPDATE ZONE
# =========================================================

@router.put(
    "/zones/{zone_id}",
    response_model=ZoneResponse
)
def update_zone(
    zone_id: int,
    data: ZoneUpdate,
    db: Session = Depends(get_database)
):

    zone = (
        db.query(StorageZone)
        .filter(
            StorageZone.id == zone_id
        )
        .first()
    )


    if not zone:

        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )


    old_capacity = int(zone.capacity)


    values = data.dict(
        exclude_unset=True
    )


    new_capacity = int(
    values.get(
        "capacity",
        old_capacity
    )
    )


    # ============================================
    # IF CAPACITY DECREASES
    # REMOVE EXTRA EMPTY POSITIONS
    # ============================================

    if new_capacity < old_capacity:

        positions = (
            db.query(StoragePosition)
            .filter(
                StoragePosition.zone_id == zone_id
            )
            .order_by(
                StoragePosition.id.desc()
            )
            .all()
        )


        remove_count = int(old_capacity - new_capacity)


        removable = [
            p for p in positions
            if not p.occupied
        ]


        if len(removable) < remove_count:

            raise HTTPException(
                status_code=400,
                detail="Cannot reduce capacity: some positions are occupied"
            )


        for position in removable[:remove_count]:

            db.delete(position)



        # ============================================
    # IF CAPACITY INCREASES
    # CREATE NEW POSITIONS
    # ============================================

    if new_capacity > old_capacity:

        prefix = "POS"
        position_type = "STORAGE_SLOT"

        if zone.zone_type == "VEHICLE_YARD":
            prefix = "VEH"
            position_type = "VEHICLE_SLOT"

        elif zone.zone_type == "CONTAINER_YARD":
            prefix = "CONT"
            position_type = "CONTAINER"

        elif zone.zone_type == "PACKAGE_AREA":
            prefix = "PACK"
            position_type = "STORAGE_SLOT"


        for i in range(int(old_capacity), int(new_capacity)):

            position = StoragePosition(
                zone_id=zone.id,
                position_code=f"{prefix}-{i+1:03}",
                position_type=position_type,
                max_weight=10000,
                latitude=zone.latitude,
                longitude=zone.longitude,
                occupied=False
            )

            db.add(position)




    # update zone fields

    for key,value in values.items():

        setattr(
            zone,
            key,
            value
        )


    db.commit()

    db.refresh(zone)


    return zone