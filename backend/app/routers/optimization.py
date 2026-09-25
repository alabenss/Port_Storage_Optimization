from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.cargo_unit import CargoUnit

from app.services.placement_engine import (
    PlacementEngine
)

from app.services.cargo_service import (
    classify_cargo
)


router = APIRouter()


@router.post("/recommend/{cargo_id}")
def recommend_position(
    cargo_id: int,
    db: Session = Depends(get_db)
):

    # =====================================================
    # FIND CARGO
    # =====================================================

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

    # =====================================================
    # REFRESH INTELLIGENCE FIRST
    # =====================================================

    intelligence = classify_cargo(
        db,
        cargo.id
    )

    if not intelligence:

        raise HTTPException(
            status_code=400,
            detail="Cargo classification failed"
        )

    # Refresh ORM object after intelligence update.
    db.refresh(cargo)

    # =====================================================
    # RUN PLACEMENT ENGINE
    # =====================================================

    engine = PlacementEngine()

    ranking = engine.evaluate_positions(
        db,
        cargo
    )

    if not ranking:

        raise HTTPException(
            status_code=400,
            detail="No storage positions configured"
        )

    cargo_weight = float(
        cargo.weight or 0
    )

    # =====================================================
    # FIND A REAL SINGLE-POSITION CANDIDATE
    # =====================================================

    single_position_candidates = []

    for item in ranking:

        if item["score"] <= -999:
            continue

        position = item["position"]

        available_capacity = (
            engine.get_available_capacity(
                position
            )
        )

        if available_capacity >= cargo_weight:

            single_position_candidates.append(
                item
            )

    # =====================================================
    # SINGLE POSITION
    # =====================================================

    if single_position_candidates:

        best = (
            single_position_candidates[0]
        )

        position = best["position"]

        return {

            "cargo_id":
                cargo.id,

            "cargo_reference":
                cargo.reference,

            "status":
                "POSITION_RECOMMENDED",

            "placement_mode":
                "SINGLE_POSITION",

            "cargo_weight":
                cargo_weight,

            "recommended_position":
            {

                "id":
                    position.id,

                "code":
                    position.position_code,

                "position_type":
                    position.position_type,

                "row":
                    position.row_code,

                "slot":
                    position.slot_number,

                "zone":
                {

                    "code":
                        position.zone.code,

                    "name":
                        position.zone.name,

                    "type":
                        position.zone.zone_type

                },

                "available_capacity":
                    engine.get_available_capacity(
                        position
                    ),

                "accessibility_score":
                    position.accessibility_score,

                "coordinates":
                {

                    "x":
                        position.x_coordinate,

                    "y":
                        position.y_coordinate

                },

                "score":
                    best["score"]

            },

            "ai_decision":
            {

                "classification":
                    intelligence[
                        "classification"
                    ],

                "storage_profile":
                    intelligence[
                        "analysis"
                    ][
                        "storage_profile"
                    ],

                "handling_method":
                    intelligence[
                        "analysis"
                    ][
                        "handling_method"
                    ],

                "risk_level":
                    intelligence[
                        "analysis"
                    ][
                        "risk_level"
                    ],

                "reason":
                    best["reasons"]

            }

        }

    # =====================================================
    # MULTI-POSITION PLAN
    # =====================================================

    plan = (
        engine.calculate_multi_position_plan(
            db,
            cargo
        )
    )

    # =====================================================
    # NOT ENOUGH STORAGE
    # =====================================================

    if not plan["feasible"]:

        return {

            "cargo_id":
                cargo.id,

            "cargo_reference":
                cargo.reference,

            "status":
                "INSUFFICIENT_STORAGE_CAPACITY",

            "placement_mode":
                "UNAVAILABLE",

            "cargo_weight":
                cargo_weight,

            "required_zone_type":
                plan[
                    "required_zone_type"
                ],

            "available_capacity":
                plan[
                    "total_capacity"
                ],

            "remaining_unallocated_weight":
                plan[
                    "remaining_weight"
                ],

            "candidate_positions":
            [

                {

                    "id":
                        detail[
                            "position"
                        ].id,

                    "code":
                        detail[
                            "position"
                        ].position_code,

                    "zone":
                        detail[
                            "position"
                        ].zone.name,

                    "available_capacity":
                        detail[
                            "available_capacity"
                        ]

                }

                for detail
                in plan[
                    "selected_position_details"
                ]

            ],

            "ai_decision":
            {

                "classification":
                    intelligence[
                        "classification"
                    ],

                "storage_profile":
                    intelligence[
                        "analysis"
                    ][
                        "storage_profile"
                    ],

                "reason":
                [
                    "No single compatible position can contain the cargo",
                    "Total compatible free storage capacity is insufficient"
                ]

            }

        }

    # =====================================================
    # VALID MULTI-POSITION RECOMMENDATION
    # =====================================================

    selected_details = (
        plan[
            "selected_position_details"
        ]
    )

    recommended_zone = None

    if selected_details:

        recommended_zone = {
            "code":
                selected_details[0][
                    "position"
                ].zone.code,

            "name":
                selected_details[0][
                    "position"
                ].zone.name,

            "type":
                selected_details[0][
                    "position"
                ].zone.zone_type
        }

    return {

        "cargo_id":
            cargo.id,

        "cargo_reference":
            cargo.reference,

        "status":
            "MULTI_POSITION_RECOMMENDED",

        "placement_mode":
            "MULTI_POSITION",

        "cargo_weight":
            cargo_weight,

        "required_positions":
            plan[
                "required_positions"
            ],

        "required_zone_type":
            plan[
                "required_zone_type"
            ],

        "recommended_zone":
            recommended_zone,

        "total_selected_capacity":
            plan[
                "total_capacity"
            ],

        "remaining_unallocated_weight":
            plan[
                "remaining_weight"
            ],

        "positions":
        [

            {

                "id":
                    detail[
                        "position"
                    ].id,

                "code":
                    detail[
                        "position"
                    ].position_code,

                "position_type":
                    detail[
                        "position"
                    ].position_type,

                "row":
                    detail[
                        "position"
                    ].row_code,

                "slot":
                    detail[
                        "position"
                    ].slot_number,

                "zone":
                {

                    "code":
                        detail[
                            "position"
                        ].zone.code,

                    "name":
                        detail[
                            "position"
                        ].zone.name,

                    "type":
                        detail[
                            "position"
                        ].zone.zone_type

                },

                "allocated_weight":
                    detail[
                        "allocated_weight"
                    ],

                "available_capacity":
                    detail[
                        "available_capacity"
                    ],

                "score":
                    detail[
                        "score"
                    ],

                "coordinates":
                {

                    "x":
                        detail[
                            "position"
                        ].x_coordinate,

                    "y":
                        detail[
                            "position"
                        ].y_coordinate

                }

            }

            for detail
            in selected_details

        ],

        "ai_decision":
        {

            "classification":
                intelligence[
                    "classification"
                ],

            "storage_profile":
                intelligence[
                    "analysis"
                ][
                    "storage_profile"
                ],

            "handling_method":
                intelligence[
                    "analysis"
                ][
                    "handling_method"
                ],

            "risk_level":
                intelligence[
                    "analysis"
                ][
                    "risk_level"
                ],

            "reason":
            [
                "No single compatible position has sufficient capacity",
                "Cargo divided across compatible storage positions",
                "Only the cargo-specific storage zone was considered",
                "Free capacity and accessibility were considered"
            ]

        }

    }