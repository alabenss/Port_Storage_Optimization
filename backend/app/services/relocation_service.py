from datetime import datetime

from sqlalchemy.orm import Session

from app.models.allocation import Allocation
from app.models.cargo_unit import CargoUnit
from app.models.movement import Movement

from app.services.placement_engine import PlacementEngine
from app.services.cargo_service import classify_cargo


class RelocationService:

    def relocate_cargo(
        self,
        db: Session,
        cargo: CargoUnit
    ):

        # -------------------------------------------------
        # 1. FIND CURRENT ACTIVE ALLOCATIONS
        # -------------------------------------------------

        current_allocations = (
            db.query(Allocation)
            .filter(
                Allocation.cargo_id == cargo.id,
                Allocation.status == "ACTIVE"
            )
            .all()
        )

        if not current_allocations:

            return {
                "status": "NOT_ALLOCATED",
                "cargo_id": cargo.id,
                "reference": cargo.reference,
                "message": "Cargo has no active storage allocation"
            }

        cargo_weight = float(cargo.weight or 0)

        if cargo_weight <= 0:

            return {
                "status": "INVALID_CARGO_WEIGHT",
                "cargo_id": cargo.id,
                "reference": cargo.reference,
                "cargo_weight": cargo_weight
            }

        # -------------------------------------------------
        # 2. GET CARGO INTELLIGENCE
        # -------------------------------------------------

        intelligence = classify_cargo(
            db,
            cargo.id
        )

        required_zone_type = (
            intelligence
            .get("analysis", {})
            .get("storage_profile")
        )

        # -------------------------------------------------
        # 3. ASK PLACEMENT ENGINE FOR RANKING
        # -------------------------------------------------

        engine = PlacementEngine()

        ranking = engine.evaluate_positions(
            db,
            cargo
        )

        if not ranking:

            return {
                "status": "NO_RELOCATION_AVAILABLE",
                "cargo_id": cargo.id,
                "reference": cargo.reference,
                "message": "No compatible storage positions found"
            }

        # -------------------------------------------------
        # 4. IDENTIFY CURRENT POSITIONS
        # -------------------------------------------------

        current_position_ids = {
            allocation.position_id
            for allocation in current_allocations
        }

        current_positions = [
            allocation.position.position_code
            for allocation in current_allocations
            if allocation.position
        ]

        # -------------------------------------------------
        # 5. BUILD CANDIDATE LIST
        #
        # Important:
        # Current positions are excluded.
        # We only relocate if OTHER free positions can
        # completely contain the cargo.
        # -------------------------------------------------

        candidates = []

        for item in ranking:

            position = item.get("position")

            if not position:
                continue

            if position.id in current_position_ids:
                continue

            if position.occupied:
                continue

            zone = position.zone

            if not zone:
                continue

            if (
                required_zone_type
                and zone.zone_type != required_zone_type
            ):
                continue

            available_capacity = max(
                float(position.max_weight or 0)
                - float(position.current_weight or 0),
                0
            )

            if available_capacity <= 0:
                continue

            score = float(
                item.get("score", 0)
            )

            if score <= -999:
                continue

            candidates.append({
                "position": position,
                "available_capacity": available_capacity,
                "score": score,
                "reasons": item.get("reasons", [])
            })

        # -------------------------------------------------
        # 6. SELECT ENOUGH NEW POSITIONS
        # -------------------------------------------------

        selected = []

        remaining_weight = cargo_weight

        for candidate in candidates:

            if remaining_weight <= 0:
                break

            position = candidate["position"]

            available_capacity = (
                candidate["available_capacity"]
            )

            allocated_weight = min(
                remaining_weight,
                available_capacity
            )

            selected.append({
                "position": position,
                "allocated_weight": allocated_weight,
                "score": candidate["score"],
                "reasons": candidate["reasons"]
            })

            remaining_weight -= allocated_weight

        # -------------------------------------------------
        # 7. SAFETY CHECK
        #
        # DO NOT release current positions if new storage
        # cannot contain the entire cargo.
        # -------------------------------------------------

        if remaining_weight > 0:

            return {
                "status": "RELOCATION_NOT_POSSIBLE",
                "cargo_id": cargo.id,
                "reference": cargo.reference,
                "cargo_weight": cargo_weight,
                "current_positions": current_positions,
                "available_new_capacity": (
                    cargo_weight - remaining_weight
                ),
                "remaining_unallocated_weight": (
                    remaining_weight
                ),
                "message": (
                    "Cargo remains in its current storage "
                    "because alternative capacity is insufficient"
                )
            }

        # -------------------------------------------------
        # 8. SAVE OLD ALLOCATION INFORMATION
        # -------------------------------------------------

        old_allocations_data = []

        for allocation in current_allocations:

            if not allocation.position:
                continue

            old_allocations_data.append({
                "allocation": allocation,
                "position": allocation.position,
                "position_code":
                    allocation.position.position_code,
                "allocated_weight":
                    float(allocation.allocated_weight or 0)
            })

        # -------------------------------------------------
        # 9. PERFORM RELOCATION IN ONE TRANSACTION
        # -------------------------------------------------

        new_allocations = []
        relocation_movements = []

        try:

            # ---------------------------------------------
            # RELEASE OLD ALLOCATIONS
            # ---------------------------------------------

            for old in old_allocations_data:

                allocation = old["allocation"]
                position = old["position"]

                allocation.status = "RELEASED"
                allocation.released_at = datetime.utcnow()

                position.occupied = False
                position.current_weight = 0

            # ---------------------------------------------
            # CREATE NEW ALLOCATIONS
            # ---------------------------------------------

            for index, item in enumerate(selected):

                position = item["position"]
                allocated_weight = item["allocated_weight"]

                reason_text = (
                    "AI relocation recommendation to "
                    f"{position.position_code}"
                )

                new_allocation = Allocation(
                    cargo_id=cargo.id,
                    position_id=position.id,
                    allocated_weight=allocated_weight,
                    status="ACTIVE",
                    allocation_method="AI_RELOCATION",
                    score=item["score"],
                    reason=reason_text
                )

                db.add(new_allocation)

                position.current_weight = (
                    allocated_weight
                )

                position.occupied = True

                # -----------------------------------------
                # CREATE RELOCATION MOVEMENT
                #
                # We map old -> new where possible.
                # If the number of positions differs,
                # from_position can be None.
                # -----------------------------------------

                old_position_code = None

                if index < len(old_allocations_data):

                    old_position_code = (
                        old_allocations_data[index]
                        ["position_code"]
                    )

                movement = Movement(
                    cargo_id=cargo.id,
                    from_position=old_position_code,
                    to_position=position.position_code,
                    action="RELOCATED",
                    reason=(
                        f"AI storage relocation from "
                        f"{old_position_code or 'MULTI_POSITION'} "
                        f"to {position.position_code} "
                        f"({allocated_weight} kg)"
                    ),
                    performed_by="SYSTEM"
                )

                db.add(movement)

                new_allocations.append({
                    "position_id": position.id,
                    "position_code":
                        position.position_code,
                    "zone":
                        position.zone.name,
                    "zone_type":
                        position.zone.zone_type,
                    "allocated_weight":
                        allocated_weight,
                    "position_capacity":
                        float(position.max_weight or 0),
                    "ai_score":
                        item["score"]
                })

                relocation_movements.append({
                    "action": "RELOCATED",
                    "from_position":
                        old_position_code,
                    "to_position":
                        position.position_code,
                    "allocated_weight":
                        allocated_weight
                })

            # ---------------------------------------------
            # HANDLE OLD POSITIONS THAT HAVE NO DIRECT
            # NEW POSITION PAIR
            # ---------------------------------------------

            if len(old_allocations_data) > len(selected):

                for old in old_allocations_data[
                    len(selected):
                ]:

                    movement = Movement(
                        cargo_id=cargo.id,
                        from_position=old[
                            "position_code"
                        ],
                        to_position=None,
                        action="RELOCATED",
                        reason=(
                            "Position released during AI "
                            "storage consolidation"
                        ),
                        performed_by="SYSTEM"
                    )

                    db.add(movement)

                    relocation_movements.append({
                        "action": "RELOCATED",
                        "from_position":
                            old["position_code"],
                        "to_position": None,
                        "allocated_weight": 0
                    })

            # ---------------------------------------------
            # UPDATE CARGO STATUS
            # ---------------------------------------------

            cargo.status = "STORED"

            db.commit()

        except Exception:

            db.rollback()
            raise

        # -------------------------------------------------
        # 10. RESPONSE
        # -------------------------------------------------

        return {
            "status": "RELOCATED",
            "relocation_method": "AI_RELOCATION",
            "cargo_id": cargo.id,
            "reference": cargo.reference,
            "cargo_weight": cargo_weight,
            "required_zone_type": required_zone_type,
            "old_positions": current_positions,
            "new_positions": [
                item["position_code"]
                for item in new_allocations
            ],
            "old_allocations_released":
                len(old_allocations_data),
            "new_allocations_created":
                len(new_allocations),
            "allocated_weight": sum(
                item["allocated_weight"]
                for item in new_allocations
            ),
            "allocations": new_allocations,
            "movements_created":
                len(relocation_movements),
            "movements":
                relocation_movements
        }