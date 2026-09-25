import pandas as pd
import unicodedata

from app.models.bill_of_lading import BillOfLading
from app.models.cargo_unit import CargoUnit
from app.models.vehicle import Vehicle
from app.models.container import Container
from app.models.trailer import Trailer
from app.models.misc_cargo import MiscCargo

from app.services.cargo_service import classify_cargo


INVALID_VALUES = {
    "",
    "NAN",
    "NONE",
    "NULL",
    "EOF",
    "CODE"
}


def clean(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    value = str(value).strip()

    if value.upper() in INVALID_VALUES:
        return None

    return value


def normalize(value):

    if value is None:
        return ""

    return (
        unicodedata.normalize(
            "NFD",
            str(value)
        )
        .encode(
            "ascii",
            "ignore"
        )
        .decode()
        .lower()
        .replace(" ", "")
        .replace("\t", "")
        .replace("°", "")
        .replace("/", "")
        .replace("-", "")
        .replace("_", "")
        .replace("'", "")
    )


def number(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if isinstance(value, str):
        value = (
            value
            .replace(" ", "")
            .replace(",", ".")
        )

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def integer(value):

    value = number(value)

    if value is None:
        return None

    try:
        return int(value)

    except (TypeError, ValueError):
        return None


def read_sheet(file_path, sheet):

    selected = None

    for header in range(5):

        try:

            df = pd.read_excel(
                file_path,
                sheet_name=sheet,
                header=header
            )

            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            if selected is None:
                selected = df

            combined = "".join(
                normalize(column)
                for column in df.columns
            )

            if (
                "nbl" in combined
                or "nchassis" in combined
                or "ntc" in combined
            ):
                return df

        except Exception:
            continue

    return selected


def find_column(columns, keys):

    for column in columns:

        normalized_column = normalize(column)

        for key in keys:

            if normalize(key) in normalized_column:
                return column

    return None


def detect_misc_category(description):

    text = str(
        description or ""
    ).upper()

    if any(
        word in text
        for word in [
            "BULK",
            "VRAC",
            "CIMENT",
            "CEMENT",
            "GRAIN"
        ]
    ):
        return {
            "category": "BULK",
            "stackable": False,
            "requires_silo": True
        }

    if any(
        word in text
        for word in [
            "COIL",
            "BOBINE",
            "ROULEAU"
        ]
    ):
        return {
            "category": "COIL",
            "stackable": False,
            "requires_silo": False
        }

    return {
        "category": "PACKAGE",
        "stackable": True,
        "requires_silo": False
    }


def import_manifest_to_database(
    db,
    file_path
):

    excel = pd.ExcelFile(file_path)

    result = {

        "created": {
            "bill_of_lading": 0,
            "cargo": 0,
            "vehicles": 0,
            "containers": 0,
            "trailers": 0,
            "misc_cargo": 0
        },

        "updated": {
            "bill_of_lading": 0,
            "cargo": 0
        },

        "skipped": {
            "bill_of_lading": 0,
            "vehicles": 0,
            "containers": 0,
            "trailers": 0
        },

        "errors": [],

        "cargo_ids": []
    }

    cargo_map = {}

    # =====================================================
    # 1. BILL OF LADING + CARGO UNIT
    # =====================================================

    if "BL" in excel.sheet_names:

        df = read_sheet(
            file_path,
            "BL"
        )

        if df is not None:

            bl_col = find_column(
                df.columns,
                [
                    "N° B/L",
                    "BL"
                ]
            )

            nature_col = find_column(
                df.columns,
                [
                    "Nature De Marchandise",
                    "Nature de cargaison",
                    "Nature"
                ]
            )

            description_col = find_column(
                df.columns,
                [
                    "Description commerciale",
                    "Description"
                ]
            )

            weight_col = find_column(
                df.columns,
                [
                    "Poids Brut",
                    "Poids"
                ]
            )

            package_col = find_column(
                df.columns,
                [
                    "Nombre colis",
                    "Nbr colis",
                    "Package"
                ]
            )

            if not bl_col:

                result["errors"].append({
                    "section": "BL",
                    "message": "Bill of Lading column not detected"
                })

            else:

                for row_index, row in df.iterrows():

                    reference = clean(
                        row.get(bl_col)
                    )

                    if not reference:
                        continue

                    try:

                        gross_weight = number(
                            row.get(weight_col)
                        ) or 0

                        package_number = integer(
                            row.get(package_col)
                        )

                        nature = clean(
                            row.get(nature_col)
                        )

                        description = clean(
                            row.get(description_col)
                        )

                        bill = (
                            db.query(BillOfLading)
                            .filter(
                                BillOfLading.bl_number == reference
                            )
                            .first()
                        )

                        if bill:

                            changed = False

                            if (
                                nature
                                and bill.cargo_nature != nature
                            ):
                                bill.cargo_nature = nature
                                changed = True

                            if (
                                description
                                and bill.description != description
                            ):
                                bill.description = description
                                changed = True

                            if (
                                gross_weight
                                and bill.gross_weight != gross_weight
                            ):
                                bill.gross_weight = gross_weight
                                changed = True

                            if (
                                package_number is not None
                                and bill.package_number != package_number
                            ):
                                bill.package_number = package_number
                                changed = True

                            if changed:
                                result["updated"]["bill_of_lading"] += 1
                            else:
                                result["skipped"]["bill_of_lading"] += 1

                        else:

                            bill = BillOfLading(
                                bl_number=reference,
                                cargo_nature=nature,
                                description=description,
                                gross_weight=gross_weight,
                                package_number=package_number
                            )

                            db.add(bill)
                            db.flush()

                            result["created"]["bill_of_lading"] += 1

                        cargo = (
                            db.query(CargoUnit)
                            .filter(
                                CargoUnit.reference == reference
                            )
                            .first()
                        )

                        if cargo:

                            cargo_changed = False

                            if cargo.bl_id != bill.id:
                                cargo.bl_id = bill.id
                                cargo_changed = True

                            if (
                                gross_weight
                                and cargo.weight != gross_weight
                            ):
                                cargo.weight = gross_weight
                                cargo_changed = True

                            if (
                                package_number is not None
                                and package_number > 0
                                and cargo.quantity != package_number
                            ):
                                cargo.quantity = package_number
                                cargo_changed = True

                            if cargo_changed:
                                result["updated"]["cargo"] += 1

                        else:

                            cargo = CargoUnit(
                                reference=reference,
                                cargo_type="MANIFEST",
                                weight=gross_weight,
                                quantity=(
                                    package_number
                                    if package_number
                                    and package_number > 0
                                    else 1
                                ),
                                status="IMPORTED",
                                bl_id=bill.id
                            )

                            db.add(cargo)
                            db.flush()

                            result["created"]["cargo"] += 1

                        cargo_map[reference] = cargo

                        if cargo.id not in result["cargo_ids"]:
                            result["cargo_ids"].append(
                                cargo.id
                            )

                    except Exception as exc:

                        result["errors"].append({
                            "section": "BL",
                            "row": int(row_index) + 1,
                            "reference": reference,
                            "message": str(exc)
                        })

    db.flush()

    # =====================================================
    # 2. VEHICLES
    # =====================================================

    if "Véhicule" in excel.sheet_names:

        df = read_sheet(
            file_path,
            "Véhicule"
        )

        if df is not None:

            bl_col = find_column(
                df.columns,
                ["N° B/L"]
            )

            chassis_col = find_column(
                df.columns,
                [
                    "N° châssis du véhicule",
                    "chassis"
                ]
            )

            registration_col = find_column(
                df.columns,
                ["immatriculation"]
            )

            manufacturer_col = find_column(
                df.columns,
                [
                    "fabricant",
                    "Code du fabricant"
                ]
            )

            model_col = find_column(
                df.columns,
                [
                    "modèle",
                    "modele",
                    "Code du modèle"
                ]
            )

            type_col = find_column(
                df.columns,
                ["Type de véhicule"]
            )

            year_col = find_column(
                df.columns,
                ["Année de fabrication"]
            )

            cylinder_col = find_column(
                df.columns,
                ["Nbr de cylindres"]
            )

            weight_col = find_column(
                df.columns,
                ["Poids total en charge"]
            )

            if not chassis_col:

                result["errors"].append({
                    "section": "VEHICLE",
                    "message": "Vehicle chassis column not detected"
                })

            else:

                for row_index, row in df.iterrows():

                    chassis = clean(
                        row.get(chassis_col)
                    )

                    if not chassis:
                        continue

                    try:

                        duplicate = (
                            db.query(Vehicle)
                            .filter(
                                Vehicle.chassis_number == chassis
                            )
                            .first()
                        )

                        if duplicate:

                            result["skipped"]["vehicles"] += 1
                            continue

                        bl_number = clean(
                            row.get(bl_col)
                        )

                        cargo = cargo_map.get(
                            bl_number
                        )

                        if cargo is None and bl_number:

                            cargo = (
                                db.query(CargoUnit)
                                .filter(
                                    CargoUnit.reference == bl_number
                                )
                                .first()
                            )

                        vehicle = Vehicle(
                            cargo_unit_id=(
                                cargo.id
                                if cargo
                                else None
                            ),
                            chassis_number=chassis,
                            registration_number=clean(
                                row.get(registration_col)
                            ),
                            manufacturer=clean(
                                row.get(manufacturer_col)
                            ),
                            model=clean(
                                row.get(model_col)
                            ),
                            vehicle_type=clean(
                                row.get(type_col)
                            ),
                            year=integer(
                                row.get(year_col)
                            ),
                            engine_cylinders=integer(
                                row.get(cylinder_col)
                            ),
                            loaded_weight=number(
                                row.get(weight_col)
                            )
                        )

                        db.add(vehicle)

                        result["created"]["vehicles"] += 1

                    except Exception as exc:

                        result["errors"].append({
                            "section": "VEHICLE",
                            "row": int(row_index) + 1,
                            "chassis": chassis,
                            "message": str(exc)
                        })

    db.flush()

    # =====================================================
    # 3. CONTAINERS
    # =====================================================

    if "Conteneur" in excel.sheet_names:

        df = read_sheet(
            file_path,
            "Conteneur"
        )

        if df is not None:

            bl_col = find_column(
                df.columns,
                ["N° B/L"]
            )

            container_col = find_column(
                df.columns,
                [
                    "N° TC",
                    "Container"
                ]
            )

            category_col = find_column(
                df.columns,
                [
                    "Catégorie",
                    "Categorie",
                    "Type"
                ]
            )

            package_col = find_column(
                df.columns,
                [
                    "Nombre colis",
                    "Package"
                ]
            )

            weight_col = find_column(
                df.columns,
                [
                    "Poids Brut",
                    "Poids"
                ]
            )

            if not container_col:

                result["errors"].append({
                    "section": "CONTAINER",
                    "message": "Container number column not detected"
                })

            else:

                for row_index, row in df.iterrows():

                    container_number = clean(
                        row.get(container_col)
                    )

                    if not container_number:
                        continue

                    try:

                        duplicate = (
                            db.query(Container)
                            .filter(
                                Container.container_number
                                == container_number
                            )
                            .first()
                        )

                        if duplicate:

                            result["skipped"]["containers"] += 1
                            continue

                        bl_number = clean(
                            row.get(bl_col)
                        )

                        cargo = cargo_map.get(
                            bl_number
                        )

                        if cargo is None and bl_number:

                            cargo = (
                                db.query(CargoUnit)
                                .filter(
                                    CargoUnit.reference == bl_number
                                )
                                .first()
                            )

                        container = Container(
                            cargo_unit_id=(
                                cargo.id
                                if cargo
                                else None
                            ),
                            container_number=container_number,
                            category=clean(
                                row.get(category_col)
                            ),
                            package_number=integer(
                                row.get(package_col)
                            ),
                            gross_weight=number(
                                row.get(weight_col)
                            )
                        )

                        db.add(container)

                        result["created"]["containers"] += 1

                    except Exception as exc:

                        result["errors"].append({
                            "section": "CONTAINER",
                            "row": int(row_index) + 1,
                            "container_number": container_number,
                            "message": str(exc)
                        })

    db.flush()

    # =====================================================
    # 4. TRAILERS
    # =====================================================

    if "Remorque" in excel.sheet_names:

        df = read_sheet(
            file_path,
            "Remorque"
        )

        if df is not None:

            bl_col = find_column(
                df.columns,
                ["N° B/L"]
            )

            reference_col = find_column(
                df.columns,
                [
                    "N° châssis",
                    "Référence",
                    "Reference"
                ]
            )

            type_col = find_column(
                df.columns,
                ["Type"]
            )

            weight_col = find_column(
                df.columns,
                ["Poids"]
            )

            if not reference_col:

                result["errors"].append({
                    "section": "TRAILER",
                    "message": "Trailer reference column not detected"
                })

            else:

                for row_index, row in df.iterrows():

                    reference = clean(
                        row.get(reference_col)
                    )

                    if not reference:
                        continue

                    try:

                        duplicate = (
                            db.query(Trailer)
                            .filter(
                                Trailer.reference == reference
                            )
                            .first()
                        )

                        if duplicate:

                            result["skipped"]["trailers"] += 1
                            continue

                        bl_number = clean(
                            row.get(bl_col)
                        )

                        cargo = cargo_map.get(
                            bl_number
                        )

                        if cargo is None and bl_number:

                            cargo = (
                                db.query(CargoUnit)
                                .filter(
                                    CargoUnit.reference == bl_number
                                )
                                .first()
                            )

                        trailer = Trailer(
                            cargo_unit_id=(
                                cargo.id
                                if cargo
                                else None
                            ),
                            reference=reference,
                            trailer_type=clean(
                                row.get(type_col)
                            ),
                            weight=number(
                                row.get(weight_col)
                            )
                        )

                        db.add(trailer)

                        result["created"]["trailers"] += 1

                    except Exception as exc:

                        result["errors"].append({
                            "section": "TRAILER",
                            "row": int(row_index) + 1,
                            "reference": reference,
                            "message": str(exc)
                        })

    db.flush()

    # =====================================================
    # 5. CREATE MISC CARGO ONLY WHEN APPROPRIATE
    # =====================================================

    for cargo in cargo_map.values():

        try:

            has_vehicle = (
                db.query(Vehicle)
                .filter(
                    Vehicle.cargo_unit_id == cargo.id
                )
                .first()
                is not None
            )

            has_container = (
                db.query(Container)
                .filter(
                    Container.cargo_unit_id == cargo.id
                )
                .first()
                is not None
            )

            existing_misc = (
                db.query(MiscCargo)
                .filter(
                    MiscCargo.cargo_unit_id == cargo.id
                )
                .first()
            )

            # Vehicle/container cargo must not also be
            # represented as miscellaneous cargo.
            if has_vehicle or has_container:

                if existing_misc:
                    db.delete(existing_misc)

                continue

            if existing_misc:
                continue

            description = None

            if cargo.bill:

                description = (
                    cargo.bill.description
                    or cargo.bill.cargo_nature
                )

            misc_info = detect_misc_category(
                description
            )

            misc = MiscCargo(
                cargo_unit_id=cargo.id,
                cargo_category=misc_info["category"],
                weight=cargo.weight or 0,
                quantity=cargo.quantity or 1,
                stackable=misc_info["stackable"],
                requires_silo=misc_info["requires_silo"]
            )

            db.add(misc)

            result["created"]["misc_cargo"] += 1

        except Exception as exc:

            result["errors"].append({
                "section": "MISC_CARGO",
                "cargo_id": cargo.id,
                "reference": cargo.reference,
                "message": str(exc)
            })

    db.flush()

    # =====================================================
    # COMMIT PHYSICAL IMPORT
    # =====================================================

    try:

        db.commit()

    except Exception:

        db.rollback()
        raise

    # =====================================================
    # 6. RUN INTELLIGENCE AFTER RELATIONSHIPS EXIST
    # =====================================================

    intelligence_results = []

    for cargo_id in result["cargo_ids"]:

        try:

            intelligence = classify_cargo(
                db,
                cargo_id
            )

            if intelligence:
                intelligence_results.append(
                    intelligence
                )

        except Exception as exc:

            result["errors"].append({
                "section": "INTELLIGENCE",
                "cargo_id": cargo_id,
                "message": str(exc)
            })

    result["intelligence"] = intelligence_results

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    result["summary"] = {

        "created_total":
            sum(result["created"].values()),

        "updated_total":
            sum(result["updated"].values()),

        "skipped_total":
            sum(result["skipped"].values()),

        "error_total":
            len(result["errors"]),

        "cargo_processed":
            len(result["cargo_ids"])
    }

    return result