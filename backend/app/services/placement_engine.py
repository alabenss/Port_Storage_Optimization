from sqlalchemy.orm import Session

from app.models.storage_position import StoragePosition
from app.models.storage_zone import StorageZone

from app.services.cargo_service import classify_cargo


class PlacementEngine:

    # =====================================================
    # AVAILABLE CAPACITY
    # =====================================================

    def get_available_capacity(
        self,
        position: StoragePosition
    ):

        max_weight = float(
            position.max_weight or 0
        )

        current_weight = float(
            position.current_weight or 0
        )

        return max(
            0.0,
            max_weight - current_weight
        )


    # =====================================================
    # GET STORAGE REQUIREMENTS
    # SINGLE SOURCE = CARGO INTELLIGENCE
    # =====================================================

    def get_storage_requirements(
        self,
        db: Session,
        cargo
    ):

        intelligence = classify_cargo(
            db,
            cargo.id
        )

        if not intelligence:

            return None

        analysis = intelligence.get(
            "analysis",
            {}
        )

        return {

            "intelligence":
                intelligence,

            "classification":
                intelligence.get(
                    "classification"
                ),

            "required_zone_type":
                analysis.get(
                    "required_zone_type"
                ),

            "required_position_type":
                analysis.get(
                    "required_position_type"
                ),

            "stackable":
                analysis.get(
                    "stackable",
                    False
                ),

            "requires_scanner":
                analysis.get(
                    "requires_scanner",
                    False
                )

        }


    # =====================================================
    # SCORE ONE POSITION
    # =====================================================

    def calculate_single_score(
        self,
        cargo,
        position,
        required_zone_type=None,
        required_position_type=None
    ):

        reasons = []

        # -------------------------------------------------
        # HARD CONSTRAINTS
        # -------------------------------------------------

        if not position.active:

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        "Position inactive"
                    ]

            }


        if not position.zone:

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        "Position has no storage zone"
                    ]

            }


        if not position.zone.active:

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        "Storage zone inactive"
                    ]

            }


        if position.occupied:

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        "Position occupied"
                    ]

            }


        actual_zone_type = (
            position.zone.zone_type
            or ""
        ).upper()


        expected_zone_type = (
            required_zone_type
            or ""
        ).upper()


        zone_type_aliases = {
            "PACKAGE": {
                "PACKAGE",
                "PACKAGE_AREA",
                "PACKAGE_YARD",
            },
            "PACKAGE_AREA": {
                "PACKAGE",
                "PACKAGE_AREA",
                "PACKAGE_YARD",
            },
            "BULK": {
                "BULK",
                "BULK_SILO_AREA",
            },
            "BULK_SILO_AREA": {
                "BULK",
                "BULK_SILO_AREA",
            },
            "COIL": {
                "COIL",
                "COIL_AREA",
            },
            "COIL_AREA": {
                "COIL",
                "COIL_AREA",
            },
            "VEHICLE": {
                "VEHICLE",
                "VEHICLE_YARD",
            },
            "VEHICLE_YARD": {
                "VEHICLE",
                "VEHICLE_YARD",
            },
            "CONTAINER": {
                "CONTAINER",
                "CONTAINER_YARD",
            },
            "CONTAINER_YARD": {
                "CONTAINER",
                "CONTAINER_YARD",
            },
        }

        accepted_zone_types = zone_type_aliases.get(
            expected_zone_type,
            {expected_zone_type}
        )

        if (
            expected_zone_type
            and
            actual_zone_type
            not in accepted_zone_types
        ):

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        (
                            "Wrong zone: cargo requires "
                            f"{expected_zone_type}"
                        )
                    ]

            }


        actual_position_type = (
            position.position_type
            or ""
        ).upper()


        expected_position_type = (
            required_position_type
            or ""
        ).upper()


        position_type_aliases = {
            "PACKAGE_STACK": {
                "PACKAGE_STACK",
                "PACKAGE",
                "STACK",
            },
            "CONTAINER_SLOT": {
                "CONTAINER_SLOT",
                "CONTAINER",
            },
            "VEHICLE_SLOT": {
                "VEHICLE_SLOT",
                "VEHICLE",
            },
            "COIL_SLOT": {
                "COIL_SLOT",
                "COIL",
            },
            "SILO": {
                "SILO",
                "BULK",
            },
        }

        accepted_position_types = position_type_aliases.get(
            expected_position_type,
            {expected_position_type}
        )

        if (
            expected_position_type
            and
            actual_position_type
            not in accepted_position_types
        ):

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        (
                            "Wrong position type: cargo requires "
                            f"{expected_position_type}"
                        )
                    ]

            }


        available_capacity = (
            self.get_available_capacity(
                position
            )
        )


        if available_capacity <= 0:

            return {

                "position":
                    position,

                "score":
                    -999,

                "reasons":
                    [
                        "No remaining weight capacity"
                    ]

            }


        # -------------------------------------------------
        # SOFT SCORING
        # -------------------------------------------------

        score = 100.0


        if expected_zone_type:

            reasons.append(
                (
                    f"Correct {expected_zone_type} "
                    "storage zone"
                )
            )


        if expected_position_type:

            reasons.append(
                (
                    f"Correct {expected_position_type} "
                    "position type"
                )
            )


        reasons.append(
            "Position is free"
        )


        # Accessibility

        accessibility = float(
            position.accessibility_score or 0
        )

        score += (
            accessibility * 20
        )

        reasons.append(
            "Accessibility considered"
        )


        # Zone priority

        priority = float(
            position.zone.priority_score or 0
        )

        score += (
            priority * 20
        )

        reasons.append(
            "Zone priority considered"
        )


        # Capacity contribution

        cargo_weight = float(
            cargo.weight or 0
        )


        if (
            cargo_weight > 0
            and
            available_capacity >= cargo_weight
        ):

            score += 40

            reasons.append(
                "Single position has enough capacity"
            )

        elif cargo_weight > 0:

            capacity_ratio = min(
                available_capacity
                / cargo_weight,
                1.0
            )

            score += (
                capacity_ratio * 20
            )

            reasons.append(
                (
                    "Position can participate in "
                    "multi-position allocation"
                )
            )


        return {

            "position":
                position,

            "score":
                round(
                    score,
                    2
                ),

            "reasons":
                reasons,

            "available_capacity":
                round(
                    available_capacity,
                    3
                )

        }


    # =====================================================
    # RANK POSITIONS
    # =====================================================

    def evaluate_positions(
        self,
        db: Session,
        cargo
    ):

        requirements = (
            self.get_storage_requirements(
                db,
                cargo
            )
        )


        if not requirements:

            return []


        required_zone_type = (
            requirements[
                "required_zone_type"
            ]
        )


        required_position_type = (
            requirements[
                "required_position_type"
            ]
        )


        positions = (
            db.query(StoragePosition)
            .join(
                StorageZone,
                StoragePosition.zone_id
                == StorageZone.id
            )
            .all()
        )


        results = []


        for position in positions:

            result = (
                self.calculate_single_score(
                    cargo,
                    position,
                    required_zone_type,
                    required_position_type
                )
            )

            results.append(
                result
            )


        results.sort(

            key=lambda item: (
                item["score"],
                float(
                    item["position"]
                    .accessibility_score
                    or 0
                ),
                float(
                    item["position"]
                    .zone
                    .priority_score
                    or 0
                )
            ),

            reverse=True

        )


        return results


    # =====================================================
    # SINGLE POSITION
    # =====================================================

    def find_best_position(
        self,
        db: Session,
        cargo
    ):

        ranking = (
            self.evaluate_positions(
                db,
                cargo
            )
        )


        cargo_weight = float(
            cargo.weight or 0
        )


        for item in ranking:

            if item["score"] <= -999:

                continue


            position = (
                item["position"]
            )


            available_capacity = (
                self.get_available_capacity(
                    position
                )
            )


            if (
                available_capacity
                >= cargo_weight
            ):

                return position


        return None


    # =====================================================
    # MULTI-POSITION PLAN
    # =====================================================

    def calculate_multi_position_plan(
        self,
        db: Session,
        cargo
    ):

        requirements = (
            self.get_storage_requirements(
                db,
                cargo
            )
        )


        cargo_weight = float(
            cargo.weight or 0
        )


        if not requirements:

            return {

                "status":
                    "CLASSIFICATION_FAILED",

                "feasible":
                    False,

                "required_positions":
                    0,

                "positions_required":
                    0,

                "selected_positions":
                    [],

                "selected_position_details":
                    [],

                "total_capacity":
                    0,

                "available_capacity":
                    0,

                "cargo_weight":
                    cargo_weight,

                "remaining_weight":
                    cargo_weight

            }


        classification = (
            requirements[
                "classification"
            ]
        )


        required_zone_type = (
            requirements[
                "required_zone_type"
            ]
        )


        required_position_type = (
            requirements[
                "required_position_type"
            ]
        )


        # -------------------------------------------------
        # SCANNER IS OPTIONAL
        # Scanner information can enrich cargo data later,
        # but it must not block storage allocation.
        # -------------------------------------------------

        requires_scanner = requirements.get(
        "requires_scanner",
        False
        )


        if cargo_weight <= 0:

            return {

                "status":
                    "INVALID_CARGO_WEIGHT",

                "classification":
                    classification,

                "required_zone_type":
                    required_zone_type,

                "required_position_type":
                    required_position_type,

                "feasible":
                    False,

                "required_positions":
                    0,

                "positions_required":
                    0,

                "selected_positions":
                    [],

                "selected_position_details":
                    [],

                "total_capacity":
                    0,

                "available_capacity":
                    0,

                "cargo_weight":
                    cargo_weight,

                "remaining_weight":
                    cargo_weight

            }


        ranking = (
            self.evaluate_positions(
                db,
                cargo
            )
        )


        compatible = [

            item

            for item in ranking

            if item["score"] > -999

        ]


        # -------------------------------------------------
        # Keep physically close positions together.
        # First zone, then row, then slot.
        # -------------------------------------------------

        compatible.sort(

    key=lambda item: (

        -item["score"],

        item["position"].zone_id,

        (
            item["position"].row_code
            or ""
        ),

        (
            item["position"].slot_number
            if item["position"].slot_number is not None
            else 999999
        )

    )

)


        total_available_capacity = sum(

            self.get_available_capacity(
                item["position"]
            )

            for item in compatible

        )


        # -------------------------------------------------
        # Not enough compatible capacity
        # -------------------------------------------------

        if (
            total_available_capacity
            < cargo_weight
        ):

            return {

                "status":
                    "INSUFFICIENT_STORAGE_CAPACITY",

                "classification":
                    classification,

                "required_zone_type":
                    required_zone_type,

                "required_position_type":
                    required_position_type,

                "stackable":
                    requirements[
                        "stackable"
                    ],

                "feasible":
                    False,

                "required_positions":
                    0,

                "positions_required":
                    0,

                "selected_positions":
                    [],

                "selected_position_details":
                    [],

                "total_capacity":
                    round(
                        total_available_capacity,
                        3
                    ),

                "available_capacity":
                    round(
                        total_available_capacity,
                        3
                    ),

                "cargo_weight":
                    cargo_weight,

                "remaining_weight":
                    round(
                        cargo_weight
                        -
                        total_available_capacity,
                        3
                    ),

                "candidate_positions":
                [

                    {

                        "id":
                            item[
                                "position"
                            ].id,

                        "code":
                            item[
                                "position"
                            ].position_code,

                        "zone":
                            item[
                                "position"
                            ].zone.name,

                        "zone_type":
                            item[
                                "position"
                            ].zone.zone_type,

                        "position_type":
                            item[
                                "position"
                            ].position_type,

                        "available_capacity":
                            round(
                                self.get_available_capacity(
                                    item[
                                        "position"
                                    ]
                                ),
                                3
                            ),

                        "score":
                            item["score"]

                    }

                    for item in compatible

                ]

            }


        # -------------------------------------------------
        # BUILD EXACT PLAN
        # -------------------------------------------------

        selected_positions = []

        selected_position_details = []

        remaining_weight = (
            cargo_weight
        )

        selected_capacity = 0.0


        for item in compatible:

            if remaining_weight <= 0:

                break


            position = (
                item["position"]
            )


            available_capacity = (
                self.get_available_capacity(
                    position
                )
            )


            if available_capacity <= 0:

                continue


            allocated_weight = min(
                available_capacity,
                remaining_weight
            )


            selected_positions.append(
                position
            )


            selected_position_details.append({

                "position":
                    position,

                "allocated_weight":
                    round(
                        allocated_weight,
                        3
                    ),

                "available_capacity":
                    round(
                        available_capacity,
                        3
                    ),

                "score":
                    item["score"],

                "reasons":
                    item["reasons"]

            })


            selected_capacity += (
                available_capacity
            )


            remaining_weight -= (
                allocated_weight
            )


        feasible = (
            remaining_weight <= 0
        )


        required_positions = len(
            selected_positions
        )


        return {

            "status":
                (
                    "PLAN_READY"
                    if feasible
                    else
                    "INSUFFICIENT_STORAGE_CAPACITY"
                ),

            "classification":
                classification,

            "required_zone_type":
                required_zone_type,

            "required_position_type":
                required_position_type,

            "stackable":
                requirements[
                    "stackable"
                ],

            "requires_scanner":
                False,

            "feasible":
                feasible,

            "required_positions":
                required_positions,

            "positions_required":
                required_positions,

            "selected_positions":
                selected_positions,

            "selected_position_details":
                selected_position_details,

            "total_capacity":
                round(
                    selected_capacity,
                    3
                ),

            "available_capacity":
                round(
                    total_available_capacity,
                    3
                ),

            "cargo_weight":
                cargo_weight,

            "remaining_weight":
                round(
                    max(
                        remaining_weight,
                        0
                    ),
                    3
                )

        }