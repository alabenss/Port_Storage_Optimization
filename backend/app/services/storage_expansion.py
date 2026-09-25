from sqlalchemy.orm import Session

from app.models.storage_zone import StorageZone
from app.models.storage_position import StoragePosition



def expand_package_storage(
    db: Session,
    number_of_positions=60
):

    zone = (
        db.query(StorageZone)
        .filter(
            StorageZone.code == "PACK-01"
        )
        .first()
    )


    if not zone:

        return {
            "status": "ERROR",
            "message": "Package storage zone not found"
        }



    existing_positions = (

        db.query(StoragePosition)

        .filter(
            StoragePosition.zone_id == zone.id,
            StoragePosition.position_type == "PACKAGE_STACK"
        )

        .count()

    )



    created = []



    for i in range(
        existing_positions + 1,
        number_of_positions + 1
    ):


        position = StoragePosition(

            zone_id=zone.id,

            position_code=f"PACK-{i:03}",

            position_type="PACKAGE_STACK",

            row_code="P",

            slot_number=i,

            level=1,

            max_stack_level=4,

            max_weight=60000,

            current_weight=0,

            occupied=False,

            active=True,

            accessibility_score=0.75,

            x_coordinate=i * 2,

            y_coordinate=65,

            length=5,

            width=5,

            height=8

        )


        db.add(position)

        created.append(
            position.position_code
        )



    db.commit()



    return {

        "status": "STORAGE_EXPANDED",

        "zone": zone.code,

        "previous_positions": existing_positions,

        "new_total_positions": number_of_positions,

        "created": created,

        "added_capacity_kg":

            len(created) * 60000

    }