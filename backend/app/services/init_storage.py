from sqlalchemy.orm import Session

from app.models.storage_zone import StorageZone
from app.models.storage_position import StoragePosition


# =========================================================
# Djen Djen Port GPS BASE
# =========================================================

BASE_LAT = 36.8200
BASE_LON = 5.8870


def initialize_storage(db: Session):

    existing_positions = db.query(StoragePosition).count()
    existing_zones = db.query(StorageZone).count()

    if existing_positions > 0 and existing_zones > 0:
        return {
            "status": "STORAGE_ALREADY_INITIALIZED",
            "zones": existing_zones,
            "positions": existing_positions
        }


    # =====================================================
    # ZONES
    # =====================================================

    zone_definitions = [

        {
            "code": "VEH-01",
            "name": "Vehicle Yard",
            "zone_type": "VEHICLE_YARD",
            "capacity": 40
        },

        {
            "code": "CONT-01",
            "name": "Container Yard",
            "zone_type": "CONTAINER_YARD",
            "capacity": 24
        },

        {
            "code": "PACK-01",
            "name": "Package Storage",
            "zone_type": "PACKAGE_AREA",
            "capacity": 120
        },

        {
            "code": "COIL-01",
            "name": "Coil Storage",
            "zone_type": "COIL_AREA",
            "capacity": 16
        },

        {
            "code": "BULK-01",
            "name": "Bulk Area",
            "zone_type": "BULK_AREA",
            "capacity": 4
        }
    ]


    zones = {}


    for z in zone_definitions:

        zone = StorageZone(
            code=z["code"],
            name=z["name"],
            zone_type=z["zone_type"],
            capacity=z["capacity"],
            active=True
        )

        db.add(zone)
        db.flush()

        zones[z["code"]] = zone



    # =====================================================
    # VEHICLE SLOTS
    # =====================================================

    vehicle_zone = zones["VEH-01"]


    for i in range(1,41):

        row = (i-1)//5
        col = (i-1)%5

        db.add(
            StoragePosition(

                zone_id=vehicle_zone.id,

                position_code=f"VEH-{i:03}",

                position_type="VEHICLE_SLOT",

                row_code="V",

                slot_number=i,

                latitude=36.8185 + row*0.00015,

                longitude=5.8890 + col*0.00020,

                max_weight=80000,

                occupied=False,

                active=True,

                accessibility_score=0.9
            )
        )



    # =====================================================
    # CONTAINER SLOTS
    # =====================================================

    container_zone = zones["CONT-01"]


    for i in range(1,25):

        row=(i-1)//6
        col=(i-1)%6


        db.add(
            StoragePosition(

                zone_id=container_zone.id,

                position_code=f"CONT-{i:03}",

                position_type="CONTAINER_SLOT",

                row_code="C",

                slot_number=i,

                level=1,

                max_stack_level=5,

                latitude=36.8212 + row*0.00018,

                longitude=5.8868 + col*0.00022,

                max_weight=30000,

                occupied=False,

                active=True,

                accessibility_score=0.85

            )
        )



    # =====================================================
    # PACKAGE POSITIONS
    # =====================================================

    package_zone = zones["PACK-01"]


    for i in range(1,121):

        row=(i-1)//10
        col=(i-1)%10


        db.add(

            StoragePosition(

                zone_id=package_zone.id,

                position_code=f"PACK-{i:03}",

                position_type="PACKAGE_STACK",

                row_code="P",

                slot_number=i,

                level=1,

                max_stack_level=6,


                latitude=36.8190 + row*0.00012,

                longitude=5.8878 + col*0.00012,


                max_weight=100000,

                occupied=False,

                active=True,

                accessibility_score=0.75,

                length=5,

                width=5,

                height=12
            )

        )



    # =====================================================
    # COILS
    # =====================================================

    coil_zone = zones["COIL-01"]


    for i in range(1,17):

        db.add(

            StoragePosition(

                zone_id=coil_zone.id,

                position_code=f"COIL-{i:03}",

                position_type="COIL_SLOT",

                row_code="CO",

                slot_number=i,

                latitude=36.8220 + ((i-1)//4)*0.0002,

                longitude=5.8900 + ((i-1)%4)*0.00025,

                max_weight=150000,

                occupied=False,

                active=True,

                accessibility_score=0.8

            )

        )



    # =====================================================
    # SILOS
    # =====================================================

    bulk_zone = zones["BULK-01"]


    for i in range(1,5):

        db.add(

            StoragePosition(

                zone_id=bulk_zone.id,

                position_code=f"SILO-{i:03}",

                position_type="SILO",

                row_code="S",

                slot_number=i,

                latitude=36.8240,

                longitude=5.8910+i*0.0002,

                max_weight=500000,

                occupied=False,

                active=True,

                accessibility_score=0.7

            )

        )


    db.commit()


    return {

        "status":"STORAGE_READY",

        "zones":db.query(StorageZone).count(),

        "positions":db.query(StoragePosition).count()

    }