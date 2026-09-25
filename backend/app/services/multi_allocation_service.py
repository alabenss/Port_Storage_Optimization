from sqlalchemy.orm import Session

from app.models.allocation import Allocation
from app.models.movement import Movement

from app.services.placement_engine import PlacementEngine


class MultiAllocationService:

    # =====================================================
    # ALLOCATE CARGO USING PLACEMENT ENGINE PLAN
    # =====================================================

    def allocate_large_cargo(
        self,
        db: Session,
        cargo,
        recommended_plan=None
    ):

        # -------------------------------------------------
        # PREVENT DUPLICATE ACTIVE ALLOCATION
        # -------------------------------------------------

        existing_allocations = (

            db.query(Allocation)

            .filter(

                Allocation.cargo_id
                == cargo.id,

                Allocation.status
                == "ACTIVE"

            )

            .all()

        )


        if existing_allocations:

            return {

                "status":
                    "ALREADY_ALLOCATED",

                "cargo_id":
                    cargo.id,

                "reference":
                    cargo.reference,

                "positions":
                [

                    allocation
                    .position
                    .position_code

                    for allocation
                    in existing_allocations

                    if (
                        allocation.position
                        is not None
                    )

                ]

            }


        # -------------------------------------------------
        # GET THE EXACT AI PLACEMENT PLAN
        # -------------------------------------------------

        engine = PlacementEngine()


        if recommended_plan is not None:
            plan = recommended_plan
        else:
            plan = (
                engine.calculate_multi_position_plan(
                    db,
                    cargo
                )
            )


        plan_status = (
            plan.get(
                "status"
            )
        )


        # -------------------------------------------------
        # CLASSIFICATION FAILURE
        # -------------------------------------------------

        if (
            plan_status
            == "CLASSIFICATION_FAILED"
        ):

            return {

                "status":
                    "CLASSIFICATION_FAILED",

                "cargo_id":
                    cargo.id,

                "reference":
                    cargo.reference

            }


        # -------------------------------------------------
        # OPTIONAL SCANNER INFORMATION
        # -------------------------------------------------

        if (
            plan_status
            == "SCANNER_REQUIRED"
        ):

            # Scanner workflow is optional.
            # Continue with allocation when the
            # PlacementEngine has enough cargo data.

            plan_status = "READY"


        # -------------------------------------------------
        # INVALID WEIGHT
        # -------------------------------------------------

        if (
            plan_status
            == "INVALID_CARGO_WEIGHT"
        ):

            return {

                "status":
                    "INVALID_CARGO_WEIGHT",

                "cargo_id":
                    cargo.id,

                "reference":
                    cargo.reference,

                "required_weight":
                    plan.get(
                        "cargo_weight",
                        0
                    )

            }


        # -------------------------------------------------
        # INSUFFICIENT CAPACITY
        # -------------------------------------------------

        if not plan.get(
            "feasible",
            False
        ):

            return {

                "status":
                    "INSUFFICIENT_STORAGE_CAPACITY",

                "cargo_id":
                    cargo.id,

                "reference":
                    cargo.reference,

                "classification":
                    plan.get(
                        "classification"
                    ),

                "required_zone_type":
                    plan.get(
                        "required_zone_type"
                    ),

                "required_position_type":
                    plan.get(
                        "required_position_type"
                    ),

                "required_weight":
                    plan.get(
                        "cargo_weight",
                        0
                    ),

                "available_capacity":
                    plan.get(
                        "available_capacity",
                        plan.get(
                            "total_capacity",
                            0
                        )
                    ),

                "remaining_unallocated_weight":
                    plan.get(
                        "remaining_weight",
                        0
                    ),

                "candidate_positions":
                    plan.get(
                        "candidate_positions",
                        []
                    )

            }


        # -------------------------------------------------
        # EXACT POSITIONS SELECTED BY PLACEMENT ENGINE
        # -------------------------------------------------

        selected_details = (
            plan.get(
                "selected_position_details",
                []
            )
        )


        if not selected_details:

            return {

                "status":
                    "NO_STORAGE_PLAN",

                "cargo_id":
                    cargo.id,

                "reference":
                    cargo.reference

            }


        # -------------------------------------------------
        # FINAL SAFETY CHECK BEFORE DATABASE WRITE
        # -------------------------------------------------

        required_weight = float(
            cargo.weight or 0
        )


        planned_weight = sum(

            float(
                item.get(
                    "allocated_weight",
                    0
                )
            )

            for item
            in selected_details

        )


        if (
            round(
                planned_weight,
                3
            )
            <
            round(
                required_weight,
                3
            )
        ):

            return {

                "status":
                    "INVALID_STORAGE_PLAN",

                "cargo_id":
                    cargo.id,

                "required_weight":
                    required_weight,

                "planned_weight":
                    round(
                        planned_weight,
                        3
                    )

            }


        # -------------------------------------------------
        # PERSIST EXACT RECOMMENDATION
        # -------------------------------------------------

        created_allocations = []

        created_movements = []


        try:

            for item in selected_details:

                position = (
                    item["position"]
                )


                allocated_weight = float(
                    item[
                        "allocated_weight"
                    ]
                )


                # -----------------------------------------
                # Re-check state in transaction
                # -----------------------------------------

                if not position.active:

                    raise ValueError(
                        (
                            "Recommended position "
                            f"{position.position_code} "
                            "is inactive"
                        )
                    )


                if position.occupied:

                    raise ValueError(
                        (
                            "Recommended position "
                            f"{position.position_code} "
                            "is no longer available"
                        )
                    )


                available_capacity = (
                    engine.get_available_capacity(
                        position
                    )
                )


                if (
                    available_capacity
                    < allocated_weight
                ):

                    raise ValueError(
                        (
                            "Recommended position "
                            f"{position.position_code} "
                            "no longer has enough capacity"
                        )
                    )


                # -----------------------------------------
                # ALLOCATION
                # -----------------------------------------

                allocation = Allocation(

                cargo_id=
                    cargo.id,

                position_id=
                    position.id,

                allocated_weight=
                    allocated_weight,

                status=
                    "ACTIVE",

                allocation_method=
                    "AI_RECOMMENDED",

                score=item.get("score"),

                reason="; ".join(
                    item.get("reasons", [])
                )

                )


                db.add(
                    allocation
                )


                # -----------------------------------------
                # UPDATE POSITION
                # -----------------------------------------

                position.current_weight = (

                    float(
                        position.current_weight
                        or 0
                    )

                    +

                    allocated_weight

                )


                position.occupied = True


                # -----------------------------------------
                # MOVEMENT
                # -----------------------------------------

                movement = Movement(

                    cargo_id=
                        cargo.id,

                    from_position=
                        None,

                    to_position=
                        position.position_code,

                    action=
                        "ALLOCATED",

                    reason=
                        (
                            "AI recommended storage "
                            f"allocation "
                            f"({allocated_weight} kg) "
                            f"to "
                            f"{position.position_code}"
                        ),

                    performed_by=
                        "SYSTEM"

                )


                db.add(
                    movement
                )


                # -----------------------------------------
                # RESPONSE DATA
                # -----------------------------------------

                created_allocations.append({

                    "position_id":
                        position.id,

                    "position_code":
                        position.position_code,

                    "zone":
                        position.zone.name,

                    "zone_type":
                        position.zone.zone_type,

                    "position_type":
                        position.position_type,

                    "allocated_weight":
                        round(
                            allocated_weight,
                            3
                        ),

                    "position_capacity":
                        float(
                            position.max_weight
                            or 0
                        ),

                    "ai_score":
                        item.get(
                            "score"
                        )

                })


                created_movements.append({

                    "action":
                        "ALLOCATED",

                    "from_position":
                        None,

                    "to_position":
                        position.position_code,

                    "allocated_weight":
                        round(
                            allocated_weight,
                            3
                        )

                })


            # ---------------------------------------------
            # UPDATE CARGO
            # ---------------------------------------------

            cargo.status = "STORED"


            # ---------------------------------------------
            # ATOMIC COMMIT
            # ---------------------------------------------

            db.commit()


        except Exception as exc:

            db.rollback()


            return {

                "status":
                    "ALLOCATION_FAILED",

                "cargo_id":
                    cargo.id,

                "error":
                    str(exc)

            }


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        return {

            "status":
                "ALLOCATED",

            "allocation_method":
                "AI_RECOMMENDED",

            "cargo_id":
                cargo.id,

            "reference":
                cargo.reference,

            "classification":
                plan.get(
                    "classification"
                ),

            "required_zone_type":
                plan.get(
                    "required_zone_type"
                ),

            "required_position_type":
                plan.get(
                    "required_position_type"
                ),

            "stackable":
                plan.get(
                    "stackable",
                    False
                ),

            "required_weight":
                required_weight,

            "allocated_weight":
                round(
                    sum(
                        item[
                            "allocated_weight"
                        ]

                        for item
                        in created_allocations
                    ),
                    3
                ),

            "positions_used":
                len(
                    created_allocations
                ),

            "allocations":
                created_allocations,

            "movements_created":
                len(
                    created_movements
                ),

            "movements":
                created_movements

        }