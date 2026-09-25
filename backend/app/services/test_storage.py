from app.database.database import SessionLocal
from app.database.base import Base
from app.database.database import engine

# Import models so SQLAlchemy knows all tables
import app.models

from app.models.storage_zone import StorageZone
from app.models.storage_position import StoragePosition


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# HELPERS
# ============================================================

def create_zone(
    db,
    code,
    name,
    zone_type,
    description,
    capacity,
    priority_score,
    map_x,
    map_y
):
    """
    Create a storage zone if it does not already exist.
    """

    existing_zone = (
        db.query(StorageZone)
        .filter(StorageZone.code == code)
        .first()
    )

    if existing_zone:
        return existing_zone

    zone = StorageZone(
        code=code,
        name=name,
        zone_type=zone_type,
        description=description,
        capacity=capacity,
        priority_score=priority_score,
        active=True,
        map_x=map_x,
        map_y=map_y
    )

    db.add(zone)
    db.flush()

    return zone


def create_position(
    db,
    zone,
    position_code,
    position_type,
    row_code,
    slot_number,
    level,
    max_stack_level,
    max_weight,
    accessibility_score,
    x_coordinate,
    y_coordinate,
    length=None,
    width=None,
    height=None
):
    """
    Create one physical storage position if it does not already exist.
    """

    existing_position = (
        db.query(StoragePosition)
        .filter(
            StoragePosition.position_code == position_code
        )
        .first()
    )

    if existing_position:
        return existing_position

    position = StoragePosition(
        zone_id=zone.id,
        position_code=position_code,
        position_type=position_type,
        row_code=row_code,
        slot_number=slot_number,
        level=level,
        max_stack_level=max_stack_level,
        max_weight=max_weight,
        current_weight=0,
        occupied=False,
        active=True,
        accessibility_score=accessibility_score,
        x_coordinate=x_coordinate,
        y_coordinate=y_coordinate,
        length=length,
        width=width,
        height=height
    )

    db.add(position)

    return position


# ============================================================
# VEHICLE YARD
# ============================================================

def create_vehicle_yard(db):

    zone = create_zone(
        db=db,
        code="VEH",
        name="Vehicle Yard",
        zone_type="VEHICLE",
        description=(
            "Dedicated outdoor storage area for imported vehicles "
            "before scanner clearance and owner retrieval."
        ),
        capacity=120000.0,
        priority_score=0.90,
        map_x=20.0,
        map_y=25.0
    )

    position_number = 1

    # 4 rows x 10 spaces = 40 vehicle positions
    for row_index, row in enumerate(["A", "B", "C", "D"]):

        for slot in range(1, 11):

            create_position(
                db=db,
                zone=zone,
                position_code=f"VEH-{row}{slot:02d}",
                position_type="VEHICLE_SLOT",
                row_code=row,
                slot_number=slot,
                level=1,
                max_stack_level=1,
                max_weight=3000.0,
                accessibility_score=0.90,
                x_coordinate=20.0 + (slot * 2.5),
                y_coordinate=25.0 + (row_index * 4.0),
                length=5.5,
                width=2.5,
                height=None
            )

            position_number += 1

    return zone


# ============================================================
# CONTAINER YARD
# ============================================================

def create_container_yard(db):

    zone = create_zone(
        db=db,
        code="CTR",
        name="Container Yard",
        zone_type="CONTAINER",
        description=(
            "Dedicated container storage area. Containers remain "
            "separated from vehicles and miscellaneous cargo."
        ),
        capacity=720000.0,
        priority_score=0.95,
        map_x=55.0,
        map_y=20.0
    )

    # 4 rows x 6 ground positions = 24 positions
    for row_index, row in enumerate(["A", "B", "C", "D"]):

        for slot in range(1, 7):

            create_position(
                db=db,
                zone=zone,
                position_code=f"CTR-{row}{slot:02d}",
                position_type="CONTAINER_SLOT",
                row_code=row,
                slot_number=slot,
                level=1,
                max_stack_level=4,
                max_weight=30000.0,
                accessibility_score=0.85,
                x_coordinate=55.0 + (slot * 4.0),
                y_coordinate=20.0 + (row_index * 5.0),
                length=12.2,
                width=2.5,
                height=2.9
            )

    return zone


# ============================================================
# PACKAGE STORAGE AREA
# ============================================================

def create_package_area(db):

    zone = create_zone(
        db=db,
        code="PKG",
        name="Package Storage Area",
        zone_type="PACKAGE",
        description=(
            "Storage area for miscellaneous packaged goods. "
            "Packages may be stacked when their storage rules permit it."
        ),
        capacity=240000.0,
        priority_score=0.80,
        map_x=45.0,
        map_y=55.0
    )

    # 3 rows x 4 storage bases = 12 positions
    for row_index, row in enumerate(["A", "B", "C"]):

        for slot in range(1, 5):

            create_position(
                db=db,
                zone=zone,
                position_code=f"PKG-{row}{slot:02d}",
                position_type="PACKAGE_STACK",
                row_code=row,
                slot_number=slot,
                level=1,
                max_stack_level=4,
                max_weight=20000.0,
                accessibility_score=0.75,
                x_coordinate=45.0 + (slot * 3.0),
                y_coordinate=55.0 + (row_index * 4.0),
                length=4.0,
                width=4.0,
                height=8.0
            )

    return zone


# ============================================================
# COIL STORAGE AREA
# ============================================================

def create_coil_area(db):

    zone = create_zone(
        db=db,
        code="COIL",
        name="Coil Storage Area",
        zone_type="COIL",
        description=(
            "Dedicated miscellaneous-goods area for coils. "
            "Coils cannot be stacked."
        ),
        capacity=480000.0,
        priority_score=0.85,
        map_x=70.0,
        map_y=55.0
    )

    # 4 rows x 4 positions = 16 coil positions
    for row_index, row in enumerate(["A", "B", "C", "D"]):

        for slot in range(1, 5):

            create_position(
                db=db,
                zone=zone,
                position_code=f"COIL-{row}{slot:02d}",
                position_type="COIL_SLOT",
                row_code=row,
                slot_number=slot,
                level=1,
                max_stack_level=1,
                max_weight=30000.0,
                accessibility_score=0.80,
                x_coordinate=70.0 + (slot * 3.0),
                y_coordinate=55.0 + (row_index * 4.0),
                length=3.0,
                width=3.0,
                height=None
            )

    return zone


# ============================================================
# BULK SILO AREA
# ============================================================

def create_bulk_silo_area(db):

    zone = create_zone(
        db=db,
        code="BULK",
        name="Bulk Silo Area",
        zone_type="BULK",
        description=(
            "Dedicated silo storage area for miscellaneous bulk goods."
        ),
        capacity=800000.0,
        priority_score=0.95,
        map_x=15.0,
        map_y=65.0
    )

    # 4 individual silos
    for silo_number in range(1, 5):

        create_position(
            db=db,
            zone=zone,
            position_code=f"SILO-{silo_number:02d}",
            position_type="SILO",
            row_code="SILO",
            slot_number=silo_number,
            level=1,
            max_stack_level=1,
            max_weight=200000.0,
            accessibility_score=0.70,
            x_coordinate=15.0 + (silo_number * 5.0),
            y_coordinate=65.0,
            length=8.0,
            width=8.0,
            height=20.0
        )

    return zone


# ============================================================
# MAIN INITIALIZER
# ============================================================

def main():

    db = SessionLocal()

    try:

        print()
        print("=" * 65)
        print("PORT STORAGE INITIALIZATION")
        print("=" * 65)

        create_vehicle_yard(db)
        print("[OK] Vehicle Yard created")

        create_container_yard(db)
        print("[OK] Container Yard created")

        create_package_area(db)
        print("[OK] Package Storage Area created")

        create_coil_area(db)
        print("[OK] Coil Storage Area created")

        create_bulk_silo_area(db)
        print("[OK] Bulk Silo Area created")

        db.commit()

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        zones = (
            db.query(StorageZone)
            .order_by(StorageZone.id)
            .all()
        )

        positions = (
            db.query(StoragePosition)
            .order_by(StoragePosition.id)
            .all()
        )

        print()
        print("=" * 65)
        print("INITIALIZATION COMPLETE")
        print("=" * 65)

        print(f"Storage zones     : {len(zones)}")
        print(f"Storage positions : {len(positions)}")

        print()
        print("ZONE SUMMARY")
        print("-" * 65)

        total_declared_capacity = 0

        for zone in zones:

            zone_positions = (
                db.query(StoragePosition)
                .filter(
                    StoragePosition.zone_id == zone.id
                )
                .count()
            )

            total_declared_capacity += zone.capacity or 0

            print(
                f"{zone.code:<6} | "
                f"{zone.name:<24} | "
                f"{zone.zone_type:<10} | "
                f"{zone_positions:>3} positions | "
                f"{zone.capacity:>10,.0f} kg"
            )

        print("-" * 65)

        print(
            f"Total declared capacity: "
            f"{total_declared_capacity:,.0f} kg"
        )

        print()

        if len(zones) == 5 and len(positions) == 96:

            print(
                "[SUCCESS] Digital port storage layout is ready."
            )

        else:

            print(
                "[WARNING] Expected 5 zones and 96 positions."
            )

        print("=" * 65)
        print()

    except Exception as exc:

        db.rollback()

        print()
        print("=" * 65)
        print("INITIALIZATION FAILED")
        print("=" * 65)
        print(str(exc))
        print("=" * 65)
        print()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()