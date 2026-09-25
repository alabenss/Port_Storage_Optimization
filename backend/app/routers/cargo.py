from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_database

from app.models.cargo_unit import CargoUnit
from app.models.bill_of_lading import BillOfLading
from app.models.vehicle import Vehicle
from app.models.container import Container
from app.models.trailer import Trailer
from app.models.allocation import Allocation
from app.models.movement import Movement
from app.models.storage_position import StoragePosition

from app.schemas.cargo import (
    CargoResponse,
    VehicleResponse,
    ContainerResponse,
    TrailerResponse,
    ManualCargoCreate,
    CargoUpdate
)

from app.services.cargo_service import classify_cargo


router = APIRouter()


# =========================================================
# HELPER
# =========================================================

def cargo_details(cargo: CargoUnit):

    bill = cargo.bill

    return {

        "id": cargo.id,

        "reference": cargo.reference,

        "cargo_type": cargo.cargo_type,

        "cargo_category": cargo.cargo_category,

        "weight": cargo.weight,

        "dimensions": {
            "length": cargo.length,
            "width": cargo.width,
            "height": cargo.height
        },

        "quantity": cargo.quantity,

        "stackable": cargo.stackable,

        "handling_method": cargo.handling_method,

        "storage_profile": cargo.storage_profile,

        "status": cargo.status,

        "arrival_date": cargo.arrival_date,

        "bill_of_lading": (
            {
                "id": bill.id,
                "bl_number": bill.bl_number,
                "cargo_nature": bill.cargo_nature,
                "description": bill.description,
                "gross_weight": bill.gross_weight,
                "package_number": bill.package_number
            }
            if bill
            else None
        ),

        "vehicles": [
            {
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "registration_number": vehicle.registration_number,
                "manufacturer": vehicle.manufacturer,
                "model": vehicle.model,
                "vehicle_type": vehicle.vehicle_type,
                "year": vehicle.year,
                "engine_cylinders": vehicle.engine_cylinders,
                "loaded_weight": vehicle.loaded_weight
            }
            for vehicle in cargo.vehicles
        ],

        "containers": [
            {
                "id": container.id,
                "container_number": container.container_number,
                "category": container.category,
                "package_number": container.package_number,
                "gross_weight": container.gross_weight,
                "seal_1": container.seal_1,
                "seal_2": container.seal_2,
                "seal_3": container.seal_3
            }
            for container in cargo.containers
        ],

        "trailers": [
            {
                "id": trailer.id,
                "reference": trailer.reference,
                "trailer_type": trailer.trailer_type,
                "weight": trailer.weight
            }
            for trailer in cargo.trailers
        ],

        "allocations": [
            {
                "allocation_id": allocation.id,
                "position_id": allocation.position_id,
                "position_code": (
                    allocation.position.position_code
                    if allocation.position
                    else None
                ),
                "zone": (
                    allocation.position.zone.name
                    if (
                        allocation.position
                        and allocation.position.zone
                    )
                    else None
                ),
                "allocated_weight": allocation.allocated_weight,
                "status": allocation.status,
                "allocation_method": allocation.allocation_method,
                "score": allocation.score,
                "reason": allocation.reason,
                "allocated_at": allocation.allocated_at,
                "released_at": allocation.released_at
            }
            for allocation in cargo.allocations
        ],

        "movements": [
            {
                "id": movement.id,
                "action": movement.action,
                "from_position": movement.from_position,
                "to_position": movement.to_position,
                "reason": movement.reason,
                "performed_by": movement.performed_by,
                "created_at": movement.created_at
            }
            for movement in cargo.movements
        ]

    }


# =========================================================
# MANUAL CARGO CREATION
# =========================================================

@router.post("/manual")
def create_manual_cargo(

    data: ManualCargoCreate,

    db: Session = Depends(get_database)

):

    reference = data.reference.strip()

    bl_number = (
        data.bl_number.strip()
        if data.bl_number
        else None
    )

    if not reference:

        raise HTTPException(
            status_code=400,
            detail="Cargo reference is required"
        )


    existing_cargo = (

        db.query(CargoUnit)

        .filter(
            CargoUnit.reference == reference
        )

        .first()

    )

    if existing_cargo:

        raise HTTPException(
            status_code=409,
            detail="Cargo reference already exists"
        )

    try:

        bill = None

        if bl_number:

            bill = (

                db.query(BillOfLading)

                .filter(
                    BillOfLading.bl_number == bl_number
                )

                .first()

            )


        if not bill:

            bill = BillOfLading(

                bl_number=bl_number or f"MANUAL-{reference}",

                cargo_nature=data.cargo_nature,

                description=data.description,

                gross_weight=data.weight,

                package_number=data.quantity

            )

            db.add(bill)

            db.flush()

        else:

            if (
                not bill.cargo_nature
                and data.cargo_nature
            ):
                bill.cargo_nature = data.cargo_nature

            if (
                not bill.description
                and data.description
            ):
                bill.description = data.description

        cargo = CargoUnit(

            reference=reference,

            cargo_type=(
                data.cargo_type.strip().upper()
                if data.cargo_type
                else "MANUAL"
            ),

            cargo_category=(
                data.cargo_category.strip().upper()
                if data.cargo_category
                else None
            ),

            weight=data.weight,

            length=data.length,

            width=data.width,

            height=data.height,

            quantity=data.quantity,

            status="IMPORTED",

            bl_id=bill.id

        )

        db.add(cargo)

        db.flush()

        cargo_id = cargo.id

        db.commit()

    except Exception:

        db.rollback()

        raise

    intelligence = classify_cargo(
        db,
        cargo_id
    )

    cargo = (

        db.query(CargoUnit)

        .filter(
            CargoUnit.id == cargo_id
        )

        .first()

    )

    return {

        "status": "MANUAL_CARGO_CREATED",

        "cargo": cargo_details(cargo),

        "intelligence": intelligence

    }


# =========================================================
# GET ALL CARGO
# =========================================================

@router.get(
    "/",
    response_model=list[CargoResponse]
)
def get_cargo(

    db: Session = Depends(get_database)

):

    return (

        db.query(CargoUnit)

        .order_by(
            CargoUnit.id.desc()
        )

        .all()

    )


# =========================================================
# SEARCH
# =========================================================

@router.get("/search/{query}")
def search_cargo(

    query: str,

    db: Session = Depends(get_database)

):

    query = query.strip()

    if not query:

        return []

    cargos = (

        db.query(CargoUnit)

        .filter(
            CargoUnit.reference.contains(query)
        )

        .order_by(
            CargoUnit.id.desc()
        )

        .all()

    )

    return [
        cargo_details(cargo)
        for cargo in cargos
    ]


# =========================================================
# VEHICLES
# =========================================================

@router.get(
    "/vehicles/all",
    response_model=list[VehicleResponse]
)
def get_vehicles(

    db: Session = Depends(get_database)

):

    return (

        db.query(Vehicle)

        .order_by(
            Vehicle.id.desc()
        )

        .all()

    )


@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleResponse
)
def get_vehicle(

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

    return vehicle


# =========================================================
# CONTAINERS
# =========================================================

@router.get(
    "/containers/all",
    response_model=list[ContainerResponse]
)
def get_containers(

    db: Session = Depends(get_database)

):

    return (

        db.query(Container)

        .order_by(
            Container.id.desc()
        )

        .all()

    )


# =========================================================
# TRAILERS
# =========================================================

@router.get(
    "/trailers/all",
    response_model=list[TrailerResponse]
)
def get_trailers(

    db: Session = Depends(get_database)

):

    return (

        db.query(Trailer)

        .order_by(
            Trailer.id.desc()
        )

        .all()

    )


# =========================================================
# GET COMPLETE CARGO DETAILS
# =========================================================

@router.get("/{cargo_id}/details")
def get_cargo_details(

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

    return cargo_details(cargo)


# =========================================================
# UPDATE CARGO
# =========================================================

@router.put("/{cargo_id}")
def update_cargo(

    cargo_id: int,

    data: CargoUpdate,

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

    update_data = data.model_dump(
        exclude_unset=True
    )

    # -----------------------------------------------------
    # Cargo reference
    # -----------------------------------------------------

    if "reference" in update_data:

        reference = (
            update_data["reference"] or ""
        ).strip()

        if not reference:

            raise HTTPException(
                status_code=400,
                detail="Cargo reference cannot be empty"
            )

        duplicate = (

            db.query(CargoUnit)

            .filter(
                CargoUnit.reference == reference,
                CargoUnit.id != cargo.id
            )

            .first()

        )

        if duplicate:

            raise HTTPException(
                status_code=409,
                detail="Cargo reference already exists"
            )

        cargo.reference = reference

    # -----------------------------------------------------
    # Standard cargo fields
    # -----------------------------------------------------

    cargo_fields = [

        "cargo_type",
        "cargo_category",
        "weight",
        "quantity",
        "length",
        "width",
        "height",
        "stackable",
        "handling_method",
        "storage_profile",
        "status"

    ]

    for field in cargo_fields:

        if field in update_data:

            value = update_data[field]

            if (
                field in [
                    "cargo_type",
                    "cargo_category",
                    "handling_method",
                    "storage_profile",
                    "status"
                ]
                and isinstance(value, str)
            ):

                value = value.strip().upper()

            setattr(
                cargo,
                field,
                value
            )

    # -----------------------------------------------------
    # Bill of Lading
    # -----------------------------------------------------

    bill = cargo.bill

    bill_fields_present = any(

        field in update_data

        for field in [

            "bl_number",
            "cargo_nature",
            "description"

        ]

    )

    if bill_fields_present:

        if not bill:

            new_bl_number = (
                update_data.get("bl_number")
                or f"MANUAL-{cargo.reference}"
            )

            bill = BillOfLading(

                bl_number=new_bl_number,

                cargo_nature=update_data.get(
                    "cargo_nature"
                ),

                description=update_data.get(
                    "description"
                ),

                gross_weight=cargo.weight,

                package_number=cargo.quantity

            )

            db.add(bill)

            db.flush()

            cargo.bl_id = bill.id

        else:

            if "bl_number" in update_data:

                new_bl_number = (
                    update_data["bl_number"] or ""
                ).strip()

                if not new_bl_number:

                    raise HTTPException(
                        status_code=400,
                        detail="BL number cannot be empty"
                    )

                duplicate_bl = (

                    db.query(BillOfLading)

                    .filter(
                        BillOfLading.bl_number == new_bl_number,
                        BillOfLading.id != bill.id
                    )

                    .first()

                )

                if duplicate_bl:

                    raise HTTPException(
                        status_code=409,
                        detail="Bill of Lading number already exists"
                    )

                bill.bl_number = new_bl_number

            if "cargo_nature" in update_data:

                bill.cargo_nature = (
                    update_data["cargo_nature"]
                )

            if "description" in update_data:

                bill.description = (
                    update_data["description"]
                )

    # Keep BL totals synchronized
    if bill:

        bill.gross_weight = cargo.weight
        bill.package_number = cargo.quantity

    try:

        db.commit()

        db.refresh(cargo)

    except Exception:

        db.rollback()

        raise

    # Re-run classification after edits
    intelligence = classify_cargo(
        db,
        cargo.id
    )

    cargo = (

        db.query(CargoUnit)

        .filter(
            CargoUnit.id == cargo_id
        )

        .first()

    )

    return {

        "status": "CARGO_UPDATED",

        "cargo": cargo_details(cargo),

        "intelligence": intelligence

    }


# =========================================================
# DELETE CARGO
# =========================================================

@router.delete("/{cargo_id}")
def delete_cargo(

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

    reference = cargo.reference

    bill = cargo.bill

    try:

        # -------------------------------------------------
        # Release occupied storage positions
        # -------------------------------------------------

        active_allocations = (

            db.query(Allocation)

            .filter(
                Allocation.cargo_id == cargo.id,
                Allocation.status == "ACTIVE"
            )

            .all()

        )

        for allocation in active_allocations:

            position = (

                db.query(StoragePosition)

                .filter(
                    StoragePosition.id
                    == allocation.position_id
                )

                .first()

            )

            if position:

                position.current_weight = max(
                    0,
                    (
                        position.current_weight
                        or 0
                    )
                    - (
                        allocation.allocated_weight
                        or 0
                    )
                )

                if position.current_weight <= 0:

                    position.current_weight = 0

                    position.occupied = False

        # -------------------------------------------------
        # Delete child records
        # -------------------------------------------------

        db.query(Movement).filter(
            Movement.cargo_id == cargo.id
        ).delete(
            synchronize_session=False
        )

        db.query(Allocation).filter(
            Allocation.cargo_id == cargo.id
        ).delete(
            synchronize_session=False
        )

        db.query(Vehicle).filter(
            Vehicle.cargo_unit_id == cargo.id
        ).delete(
            synchronize_session=False
        )

        db.query(Container).filter(
            Container.cargo_unit_id == cargo.id
        ).delete(
            synchronize_session=False
        )

        db.query(Trailer).filter(
            Trailer.cargo_unit_id == cargo.id
        ).delete(
            synchronize_session=False
        )

        # -------------------------------------------------
        # Delete cargo
        # -------------------------------------------------

        db.delete(cargo)

        db.flush()

        # -------------------------------------------------
        # Delete BL only if nothing else uses it
        # -------------------------------------------------

        if bill:

            remaining_cargo = (

                db.query(CargoUnit)

                .filter(
                    CargoUnit.bl_id == bill.id
                )

                .count()

            )

            if remaining_cargo == 0:

                db.delete(bill)

        db.commit()

    except Exception:

        db.rollback()

        raise

    return {

        "status": "CARGO_DELETED",

        "cargo_id": cargo_id,

        "reference": reference,

        "storage_released": True

    }


# =========================================================
# GET CARGO BY ID
#
# KEEP LAST because /{cargo_id} is dynamic.
# =========================================================

@router.get(
    "/{cargo_id}",
    response_model=CargoResponse
)
def get_cargo_by_id(

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

    return cargo