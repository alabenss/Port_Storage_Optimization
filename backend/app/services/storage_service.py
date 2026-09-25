from sqlalchemy.orm import Session

from app.models.storage_zone import StorageZone
from app.models.storage_position import StoragePosition



class StorageService:


    def create_zone(
        self,
        db: Session,
        name,
        zone_type,
        capacity,
        priority_score=0.5
    ):


        existing = (
            db.query(StorageZone)
            .filter(
                StorageZone.name == name
            )
            .first()
        )


        if existing:

            return existing



        zone = StorageZone(

            name=name,

            zone_type=zone_type,

            capacity=capacity,

            priority_score=priority_score

        )


        db.add(zone)

        db.commit()

        db.refresh(zone)


        return zone




    def create_positions(
        self,
        db: Session,
        zone,
        prefix,
        number,
        max_weight
    ):


        created=[]


        for i in range(
            1,
            number + 1
        ):


            code = f"{prefix}{i:03}"


            existing = (

                db.query(StoragePosition)

                .filter(
                    StoragePosition.position_code == code
                )

                .first()

            )


            if existing:
                continue



            position = StoragePosition(


                zone_id=zone.id,


                position_code=code,


                max_weight=max_weight,


                current_weight=0,


                occupied=False,


                accessibility_score=0.5

            )


            db.add(position)

            created.append(position)



        db.commit()



        return created