import app.models

from app.database.database import SessionLocal

from app.models.vehicle import Vehicle

from app.models.storage_position import StoragePosition

from app.models.movement import Movement

from app.services.placement_engine import PlacementEngine

from app.services.allocation_service import AllocationService



db = SessionLocal()



vehicle = db.query(Vehicle).first()


print(
    "Vehicle:",
    vehicle.chassis_number,
    vehicle.loaded_weight
)



engine = PlacementEngine()



position = engine.find_best_position(

    db,

    vehicle

)



print(

    "Selected:",

    position.position_code

)



service = AllocationService()



allocation = service.allocate_vehicle(

    db,

    vehicle,

    position

)



print(

    "Allocation:",

    allocation.id

)


print(

    "Position:",

    position.position_code,

    position.current_weight

)


print(

    "Movements:",

    db.query(Movement).count()

)