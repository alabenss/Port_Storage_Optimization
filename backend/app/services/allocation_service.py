from sqlalchemy.orm import Session

from app.models.allocation import Allocation
from app.models.storage_position import StoragePosition
from app.models.cargo_unit import CargoUnit
from app.models.movement import Movement


class AllocationService:

    # ---------------------------------
    # VEHICLE ALLOCATION
    # ---------------------------------

    def allocate_vehicle(
        self,
        db: Session,
        vehicle,
        position: StoragePosition
    ):

        allocation = Allocation(
            vehicle_id=vehicle.id,
            position_id=position.id
        )

        position.occupied = True

        if vehicle.weight:
            position.current_weight = vehicle.weight
        else:
            position.current_weight = 0

        db.add(allocation)

        try:

            db.commit()
            db.refresh(allocation)

        except Exception:

            db.rollback()
            raise

        return allocation


    # ---------------------------------
    # SIMPLE CARGO ALLOCATION
    # ---------------------------------

    def allocate_cargo(
        self,
        db: Session,
        cargo_id: int
    ):

        cargo = (
            db.query(CargoUnit)
            .filter(
                CargoUnit.id == cargo_id
            )
            .first()
        )

        if not cargo:

            return {
                "error": "Cargo not found"
            }

        return {
            "status": "ALLOCATED",
            "cargo_id": cargo.id
        }


    # ---------------------------------
    # RELEASE ONE ALLOCATION
    # ---------------------------------

    def release_allocation(
        self,
        db: Session,
        allocation: Allocation
    ):

        position = (
            db.query(StoragePosition)
            .filter(
                StoragePosition.id ==
                allocation.position_id
            )
            .first()
        )

        old_position = None

        if position:

            old_position = (
                position.position_code
            )

            position.occupied = False
            position.current_weight = 0


        # ---------------------------------
        # Movement history
        # Only cargo movements are supported
        # by the current Movement model
        # ---------------------------------

        if (
            allocation.cargo_id is not None
            and old_position is not None
        ):

            movement = Movement(

                cargo_id=allocation.cargo_id,

                from_position=old_position,

                to_position=None,

                action="RELEASED",

                reason=(
                    f"Cargo released from "
                    f"{old_position}"
                ),

                performed_by="SYSTEM"
            )

            db.add(movement)


        # ---------------------------------
        # Update allocation
        # ---------------------------------

        allocation.status = "RELEASED"


        try:

            db.commit()
            db.refresh(allocation)

        except Exception:

            db.rollback()
            raise


        return {

            "status": "RELEASED",

            "allocation_id":
                allocation.id,

            "cargo_id":
                allocation.cargo_id,

            "vehicle_id":
                allocation.vehicle_id,

            "released_position":
                old_position

        }