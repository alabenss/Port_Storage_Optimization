from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_database

from app.models.cargo_unit import CargoUnit
from app.models.vehicle import Vehicle
from app.models.allocation import Allocation
from app.models.storage_position import StoragePosition
from app.models.storage_zone import StorageZone
from app.models.movement import Movement


router = APIRouter()


# =====================================================
# COMPLETE DASHBOARD SUMMARY
# =====================================================

@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_database)
):

    # -------------------------
    # CARGO
    # -------------------------

    total_cargo = (
        db.query(CargoUnit)
        .count()
    )


    total_weight = (
        db.query(
            func.sum(CargoUnit.weight)
        )
        .scalar()
        or 0
    )


    cargo_status = {}

    statuses = (
        db.query(
            CargoUnit.status,
            func.count(CargoUnit.id)
        )
        .group_by(
            CargoUnit.status
        )
        .all()
    )


    for status, count in statuses:
        cargo_status[status] = count



    # -------------------------
    # VEHICLES
    # -------------------------

    total_vehicles = (
        db.query(Vehicle)
        .count()
    )



    # -------------------------
    # STORAGE
    # -------------------------

    total_positions = (
        db.query(StoragePosition)
        .count()
    )


    occupied_positions = (
        db.query(StoragePosition)
        .filter(
            StoragePosition.occupied == True
        )
        .count()
    )


    occupancy = 0

    if total_positions:
        occupancy = round(
            occupied_positions /
            total_positions *
            100,
            2
        )



    # -------------------------
    # OPERATIONS
    # -------------------------

    active_allocations = (
        db.query(Allocation)
        .filter(
            Allocation.status == "ACTIVE"
        )
        .count()
    )


    movements_total = (
        db.query(Movement)
        .count()
    )


    allocated = (
        db.query(Movement)
        .filter(
            Movement.action == "ALLOCATED"
        )
        .count()
    )


    released = (
        db.query(Movement)
        .filter(
            Movement.action == "RELEASED"
        )
        .count()
    )


    relocated = (
        db.query(Movement)
        .filter(
            Movement.action == "RELOCATED"
        )
        .count()
    )



    return {


        "cargo": {

            "total_units":
                total_cargo,

            "total_weight":
                total_weight,

            "status":
                cargo_status
        },


        "vehicles":
            total_vehicles,



        "storage": {

            "total_positions":
                total_positions,

            "occupied":
                occupied_positions,

            "available":
                total_positions -
                occupied_positions,

            "occupancy_percent":
                occupancy
        },



        "operations": {

            "active_allocations":
                active_allocations,

            "movements":
                movements_total,

            "allocated":
                allocated,

            "released":
                released,

            "relocated":
                relocated
        }

    }




# =====================================================
# STORAGE ZONE ANALYTICS
# =====================================================

@router.get("/zones")
def dashboard_zones(
    db: Session = Depends(get_database)
):

    zones = (
        db.query(StorageZone)
        .all()
    )


    result = []


    for zone in zones:


        positions = (
            db.query(StoragePosition)
            .filter(
                StoragePosition.zone_id == zone.id
            )
            .all()
        )


        total_positions = len(
            positions
        )


        occupied = len(
            [
                p for p in positions
                if p.occupied
            ]
        )


        current_weight = sum(
            p.current_weight or 0
            for p in positions
        )


        utilization = 0


        if zone.capacity:

            utilization = round(
                current_weight /
                zone.capacity *
                100,
                2
            )



        result.append({

            "zone":
                zone.name,

            "type":
                zone.zone_type,


            "capacity":
                zone.capacity,


            "current_weight":
                current_weight,


            "utilization_percent":
                utilization,


            "total_positions":
                total_positions,


            "occupied":
                occupied,


            "available":
                total_positions -
                occupied
        })



    return result





# =====================================================
# MOVEMENT ANALYTICS
# =====================================================

@router.get("/movements")
def dashboard_movements(
    db: Session = Depends(get_database)
):


    total = (
        db.query(Movement)
        .count()
    )


    allocated = (
        db.query(Movement)
        .filter(
            Movement.action=="ALLOCATED"
        )
        .count()
    )


    released = (
        db.query(Movement)
        .filter(
            Movement.action=="RELEASED"
        )
        .count()
    )


    relocated = (
        db.query(Movement)
        .filter(
            Movement.action=="RELOCATED"
        )
        .count()
    )



    return {

        "total_movements":
            total,

        "allocated":
            allocated,

        "released":
            released,

        "relocated":
            relocated
    }
# =====================================================
# STORAGE MAP VISUALIZATION
# =====================================================

@router.get("/map")
def dashboard_map(
    db: Session = Depends(get_database)
):

    positions = (
        db.query(StoragePosition)
        .all()
    )


    result = []


    for position in positions:


        zone = (
            db.query(StorageZone)
            .filter(
                StorageZone.id == position.zone_id
            )
            .first()
        )


        allocations = (
            db.query(Allocation)
            .filter(
                Allocation.position_id == position.id,
                Allocation.status == "ACTIVE"
            )
            .all()
        )


        cargo_list = []


        current_weight = 0


        for allocation in allocations:

            current_weight += (
                allocation.allocated_weight
                or 0
            )


            cargo_list.append({

                "cargo_id":
                    allocation.cargo_id,

                "weight":
                    allocation.allocated_weight

            })



        utilization = 0


        if position.max_weight:

            utilization = round(
                current_weight /
                position.max_weight *
                100,
                2
            )



        # ----------------------------
        # POSITION STATUS
        # ----------------------------

        status = "EMPTY"


        if position.occupied:


            if utilization >= 100:

                status = "FULL"


            elif utilization >= 50:

                status = "PARTIAL"


            else:

                status = "LOW"



        result.append({

            "id":
                position.id,


            "code":
                position.position_code,


            "zone":
                zone.name
                if zone else None,


            "zone_type":
                zone.zone_type
                if zone else None,



            "coordinates": {

                "x":
                    position.x_coordinate,


                "y":
                    position.y_coordinate

            },


            "capacity":
                position.max_weight,


            "current_weight":
                current_weight,


            "occupied":
                position.occupied,


            "utilization":
                utilization,


            "status":
                status,


            "cargo":
                cargo_list

        })



    return result