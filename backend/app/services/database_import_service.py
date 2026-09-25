from sqlalchemy.orm import Session

from app.models.bill_of_lading import BillOfLading
from app.models.cargo_unit import CargoUnit
from app.models.vehicle import Vehicle
from app.models.container import Container



def clean(value):

    if value is None:
        return None

    return str(value).strip()



def import_bill_of_lading(
    db: Session,
    row
):

    bl_number = clean(
        row.get("N° B/L  ")
    )


    if not bl_number:
        return None


    existing = db.query(
        BillOfLading
    ).filter(
        BillOfLading.bl_number == bl_number
    ).first()


    if existing:
        return existing


    bl = BillOfLading(

        bl_number=bl_number,

        cargo_nature=clean(
            row.get("Nature De Cargaison")
        ),

        description=clean(
            row.get("Description commerciale")
        ),

        gross_weight=row.get(
            "Poids Brut"
        ),

        package_number=row.get(
            "Nombre de colis"
        )

    )


    db.add(bl)

    db.flush()


    return bl



def import_vehicle(
    db: Session,
    row,
    bl
):

    chassis = clean(
        row.get(
            "N° châssis du véhicule"
        )
    )


    if not chassis:
        return None



    cargo = CargoUnit(

        reference=chassis,

        external_id=chassis,

        source_sheet="Véhicule",

        cargo_type="VEHICLE",

        weight=row.get(
            "Poids total en charge"
        ),

        bl_id=bl.id

    )


    db.add(cargo)

    db.flush()



    vehicle = Vehicle(

        cargo_unit_id=cargo.id,

        chassis_number=chassis,

        manufacturer=clean(
            row.get(
                "Code du fabricant de véhicule"
            )
        ),

        model=clean(
            row.get(
                "Code du modèle de véhicule"
            )
        ),

        year=row.get(
            "Année de fabrication"
        ),

        loaded_weight=row.get(
            "Poids total en charge"
        )

    )


    db.add(vehicle)



def import_container(
    db: Session,
    row,
    bl
):

    container_number = clean(
        row.get("N° TC")
    )


    if not container_number:
        return None



    cargo = CargoUnit(

        reference=container_number,

        external_id=container_number,

        source_sheet="Conteneur",

        cargo_type="CONTAINER",

        weight=row.get(
            "Poids Brut(Kg)"
        ),

        bl_id=bl.id

    )


    db.add(cargo)

    db.flush()



    container = Container(

        cargo_unit_id=cargo.id,

        container_number=container_number,

        size=clean(
            row.get(
                "Catégorie de TC"
            )
        ),

        gross_weight=row.get(
            "Poids Brut(Kg)"
        )

    )


    db.add(container)



def import_manifest(
    db: Session,
    sheets
):


    # Import BL first

    bl_map = {}


    if "BL" in sheets:

        for _,row in sheets["BL"]["data"].iterrows():

            bl = import_bill_of_lading(
                db,
                row
            )

            if bl:
                bl_map[
                    bl.bl_number
                ] = bl



    # Import vehicles

    if "Véhicule" in sheets:

        for _,row in sheets["Véhicule"]["data"].iterrows():

            bl_number = clean(
                row.get("N° B/L")
            )


            bl = bl_map.get(
                bl_number
            )


            if bl:

                import_vehicle(
                    db,
                    row,
                    bl
                )



    # Import containers

    if "Conteneur" in sheets:

        for _,row in sheets["Conteneur"]["data"].iterrows():

            bl_number = clean(
                row.get("N° B/L")
            )


            bl = bl_map.get(
                bl_number
            )


            if bl:

                import_container(
                    db,
                    row,
                    bl
                )



    db.commit()


    return {

        "status":"SUCCESS",

        "bills_of_lading":
        len(bl_map)

    }