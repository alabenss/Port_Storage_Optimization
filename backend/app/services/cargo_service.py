from sqlalchemy.orm import Session

from app.models.cargo_unit import CargoUnit
from app.models.vehicle import Vehicle
from app.models.container import Container
from app.models.trailer import Trailer


class CargoIntelligenceService:

    # ============================================================
    # TEXT HELPERS
    # ============================================================

    @staticmethod
    def _build_search_text(cargo: CargoUnit) -> str:

        parts = [
            cargo.reference or "",
            cargo.cargo_type or "",
            cargo.cargo_category or "",
        ]

        if cargo.bill:

            parts.extend([
                cargo.bill.bl_number or "",
                cargo.bill.cargo_nature or "",
                cargo.bill.description or "",
            ])

        return " ".join(
            str(value)
            for value in parts
            if value is not None
        ).upper()


    @staticmethod
    def _contains_any(text: str, words: list[str]) -> bool:

        return any(
            word in text
            for word in words
        )


    # ============================================================
    # MAIN CLASSIFICATION ENGINE
    # ============================================================

    def classify_cargo(
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
            return None


        # --------------------------------------------------------
        # Detect linked operational records
        # --------------------------------------------------------

        vehicles = (
            db.query(Vehicle)
            .filter(
                Vehicle.cargo_unit_id == cargo.id
            )
            .count()
        )

        containers = (
            db.query(Container)
            .filter(
                Container.cargo_unit_id == cargo.id
            )
            .count()
        )

        trailers = (
            db.query(Trailer)
            .filter(
                Trailer.cargo_unit_id == cargo.id
            )
            .count()
        )


        weight = float(
            cargo.weight or 0
        )

        quantity = int(
            cargo.quantity or 1
        )

        text = self._build_search_text(
            cargo
        )


        # ========================================================
        # CLASSIFICATION
        #
        # Storage families:
        #
        # VEHICLE
        # CONTAINER
        # BULK
        # COIL
        # PACKAGE
        #
        # These correspond directly to the digital yard.
        # ========================================================


        # --------------------------------------------------------
        # VEHICLE
        # --------------------------------------------------------

        if vehicles > 0:

            classification = "VEHICLE"

            handling = "VEHICLE_HANDLING"

            storage_profile = "VEHICLE"

            position_type = "VEHICLE_SLOT"

            stackable = False

            requires_scanner = True

            classification_reason = (
                "Vehicle record linked to cargo unit"
            )


        # --------------------------------------------------------
        # CONTAINER
        # --------------------------------------------------------

        elif containers > 0:

            classification = "CONTAINER"

            handling = "CONTAINER_CRANE"

            storage_profile = "CONTAINER"

            position_type = "CONTAINER_SLOT"

            stackable = True

            requires_scanner = True

            classification_reason = (
                "Container record linked to cargo unit"
            )


        # --------------------------------------------------------
        # BULK
        # --------------------------------------------------------

        elif self._contains_any(
            text,
            [
                "BULK",
                "VRAC",
                "GRAIN",
                "GRAINS",
                "CEREAL",
                "CEREALE",
                "CEREALES",
                "CEMENT",
                "CIMENT",
                "POWDER",
                "POUDRE",
                "FLOUR",
                "FARINE"
            ]
        ):

            classification = "BULK"

            handling = "BULK_HANDLING"

            storage_profile = "BULK"

            position_type = "SILO"

            stackable = False

            requires_scanner = False

            classification_reason = (
                "Bulk cargo terminology detected "
                "in cargo/BL description"
            )


        # --------------------------------------------------------
        # COIL
        # --------------------------------------------------------

        elif self._contains_any(
            text,
            [
                "COIL",
                "COILS",
                "BOBINE",
                "BOBINES",
                "STEEL COIL",
                "STEEL COILS",
                "ROULEAU",
                "ROULEAUX"
            ]
        ):

            classification = "COIL"

            handling = "CRANE_REQUIRED"

            storage_profile = "COIL"

            position_type = "COIL_SLOT"

            stackable = False

            requires_scanner = False

            classification_reason = (
                "Coil terminology detected "
                "in cargo/BL description"
            )


        # --------------------------------------------------------
        # PACKAGE
        #
        # All remaining miscellaneous goods are treated as
        # packaged/general miscellaneous cargo for this project.
        # --------------------------------------------------------

        else:

            classification = "PACKAGE"

            storage_profile = "PACKAGE"

            position_type = "PACKAGE_STACK"

            requires_scanner = False


            # Heavy package / project cargo
            if weight > 30000:

                handling = "CRANE_REQUIRED"

                stackable = False

                classification_reason = (
                    "Miscellaneous cargo classified as PACKAGE; "
                    "weight requires heavy handling"
                )

            else:

                handling = "FORKLIFT_OR_STANDARD"

                stackable = True

                classification_reason = (
                    "Miscellaneous cargo classified as PACKAGE"
                )


        # ========================================================
        # RISK LEVEL
        # ========================================================

        if weight > 200000:

            risk = "VERY_HIGH"

        elif weight > 100000:

            risk = "HIGH"

        elif weight > 30000:

            risk = "MEDIUM"

        else:

            risk = "LOW"


        # ========================================================
        # PHYSICAL SIZE
        # ========================================================

        length = cargo.length
        width = cargo.width
        height = cargo.height

        volume = None

        if (
            length is not None
            and width is not None
            and height is not None
        ):

            try:

                volume = round(
                    float(length)
                    * float(width)
                    * float(height),
                    3
                )

            except (TypeError, ValueError):

                volume = None


        # ========================================================
        # SAVE CLASSIFICATION
        # ========================================================

        if not cargo.cargo_category:
            cargo.cargo_category = classification

        cargo.handling_method = handling

        cargo.storage_profile = storage_profile

        cargo.stackable = stackable


        # Keep cargo_type as the origin/type entered by the system.
        # Example:
        # MANIFEST
        # MANUAL
        #
        # cargo_category contains the physical classification.


        db.commit()

        db.refresh(cargo)


        # ========================================================
        # RESPONSE
        # ========================================================

        return {

            "cargo_id":
                cargo.id,

            "reference":
                cargo.reference,

            "classification":
                classification,

            "cargo_type":
                cargo.cargo_type,

            "weight":
                weight,

            "quantity":
                quantity,

            "status":
                cargo.status,

            "analysis":
            {

                "vehicles_detected":
                    vehicles,

                "containers_detected":
                    containers,

                "trailers_detected":
                    trailers,

                "risk_level":
                    risk,

                "handling_method":
                    handling,

                "storage_profile":
                    storage_profile,

                "required_zone_type":
                    storage_profile,

                "required_position_type":
                    position_type,

                "stackable":
                    stackable,

                "requires_scanner":
                    requires_scanner,

                "classification_reason":
                    classification_reason,

                "dimensions":
                {
                    "length":
                        length,

                    "width":
                        width,

                    "height":
                        height,

                    "volume":
                        volume
                }

            }

        }


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def classify_cargo(
    db: Session,
    cargo_id: int
):

    service = CargoIntelligenceService()

    return service.classify_cargo(
        db,
        cargo_id
    )