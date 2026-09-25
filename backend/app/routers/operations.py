from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session, joinedload

from app.database.database import get_database

from app.models.storage_zone import StorageZone
from app.models.storage_position import StoragePosition
from app.models.allocation import Allocation


router = APIRouter()


# =========================================================
# REAL-TIME STORAGE MAP
# =========================================================

@router.get("/storage-map")
def storage_map(
    db: Session = Depends(get_database)
):

    zones = (
        db.query(StorageZone)
        .options(
            joinedload(StorageZone.positions)
            .joinedload(StoragePosition.allocations)
            .joinedload(Allocation.cargo)
        )
        .order_by(StorageZone.id)
        .all()
    )

    result = []

    total_positions = 0
    total_occupied = 0
    total_capacity = 0
    total_used_capacity = 0


    for zone in zones:

        zone_positions = []

        zone_total = len(zone.positions)

        zone_occupied = 0

        zone_capacity = 0

        zone_used_capacity = 0


        positions = sorted(
            zone.positions,
            key=lambda p: p.position_code
        )


        for position in positions:

            active_allocation = None


            for allocation in position.allocations:

                if allocation.status == "ACTIVE":

                    active_allocation = allocation

                    break


            occupied = (
                position.occupied
                or active_allocation is not None
            )


            if occupied:

                zone_occupied += 1


            max_weight = (
                position.max_weight or 0
            )

            current_weight = (
                position.current_weight or 0
            )


            zone_capacity += max_weight

            zone_used_capacity += current_weight


            cargo_data = None


            if (
                active_allocation
                and active_allocation.cargo
            ):

                cargo = active_allocation.cargo

                cargo_data = {

                    "id":
                        cargo.id,

                    "reference":
                        cargo.reference,

                    "classification":
                        cargo.cargo_category,

                    "weight":
                        cargo.weight,

                    "status":
                        cargo.status,

                    "handling_method":
                        cargo.handling_method,

                    "storage_profile":
                        cargo.storage_profile,

                    "allocation_id":
                        active_allocation.id,

                    "allocated_at":
                        active_allocation.allocated_at

                }


            utilization = (

                round(
                    (
                        current_weight
                        / max_weight
                    ) * 100,
                    2
                )

                if max_weight > 0

                else 0

            )


            zone_positions.append({

                "id":
                    position.id,

                "position_code":
                    position.position_code,

                "occupied":
                    occupied,

                "max_weight":
                    max_weight,

                "current_weight":
                    current_weight,

                "utilization_percent":
                    utilization,

                "accessibility_score":
                    position.accessibility_score,

                "cargo":
                    cargo_data

            })


        zone_available = (
            zone_total
            - zone_occupied
        )


        occupancy_percent = (

            round(
                (
                    zone_occupied
                    / zone_total
                ) * 100,
                2
            )

            if zone_total > 0

            else 0

        )


        capacity_utilization = (

            round(
                (
                    zone_used_capacity
                    / zone_capacity
                ) * 100,
                2
            )

            if zone_capacity > 0

            else 0

        )


        result.append({

            "zone":
            {

                "id":
                    zone.id,

                "name":
                    zone.name,

                "zone_type":
                    zone.zone_type,

                "declared_capacity":
                    zone.capacity,

                "priority_score":
                    zone.priority_score

            },

            "statistics":
            {

                "total_positions":
                    zone_total,

                "occupied_positions":
                    zone_occupied,

                "available_positions":
                    zone_available,

                "occupancy_percent":
                    occupancy_percent,

                "position_capacity":
                    zone_capacity,

                "used_capacity":
                    zone_used_capacity,

                "capacity_utilization_percent":
                    capacity_utilization

            },

            "positions":
                zone_positions

        })


        total_positions += zone_total

        total_occupied += zone_occupied

        total_capacity += zone_capacity

        total_used_capacity += zone_used_capacity


    total_available = (
        total_positions
        - total_occupied
    )


    global_occupancy = (

        round(
            (
                total_occupied
                / total_positions
            ) * 100,
            2
        )

        if total_positions > 0

        else 0

    )


    global_capacity_utilization = (

        round(
            (
                total_used_capacity
                / total_capacity
            ) * 100,
            2
        )

        if total_capacity > 0

        else 0

    )


    return {

        "summary":
        {

            "zones":
                len(zones),

            "total_positions":
                total_positions,

            "occupied_positions":
                total_occupied,

            "available_positions":
                total_available,

            "occupancy_percent":
                global_occupancy,

            "total_capacity":
                total_capacity,

            "used_capacity":
                total_used_capacity,

            "capacity_utilization_percent":
                global_capacity_utilization

        },

        "zones":
            result

    }


# =========================================================
# ACTIVE ALLOCATIONS
# =========================================================

@router.get("/active-allocations")
def active_allocations(
    db: Session = Depends(get_database)
):

    allocations = (

        db.query(Allocation)

        .options(
            joinedload(Allocation.cargo),
            joinedload(Allocation.position)
            .joinedload(StoragePosition.zone)
        )

        .filter(
            Allocation.status == "ACTIVE"
        )

        .order_by(
            Allocation.allocated_at.desc()
        )

        .all()

    )


    result = []


    for allocation in allocations:

        cargo = allocation.cargo

        position = allocation.position


        result.append({

            "allocation_id":
                allocation.id,

            "allocated_at":
                allocation.allocated_at,

            "cargo":
            {

                "id":
                    cargo.id,

                "reference":
                    cargo.reference,

                "classification":
                    cargo.cargo_category,

                "weight":
                    cargo.weight,

                "handling_method":
                    cargo.handling_method

            },

            "storage":
            {

                "position_id":
                    position.id,

                "position_code":
                    position.position_code,

                "zone":
                    position.zone.name
                    if position.zone
                    else None,

                "zone_type":
                    position.zone.zone_type
                    if position.zone
                    else None

            }

        })


    return {

        "count":
            len(result),

        "allocations":
            result

    }