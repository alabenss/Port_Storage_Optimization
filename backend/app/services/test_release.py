import app.models


from app.database.database import SessionLocal

from app.models.allocation import Allocation

from app.models.storage_position import StoragePosition

from app.services.allocation_service import AllocationService



db = SessionLocal()



allocation = (
    db.query(Allocation)
    .filter(
        Allocation.status=="ACTIVE"
    )
    .first()
)



print(
    "Before:",
    allocation.status,
    allocation.position.position_code,
    allocation.position.occupied
)



service = AllocationService()



service.release_allocation(

    db,

    allocation

)



print(

    "After:",
    allocation.status,
    allocation.position.position_code,
    allocation.position.occupied

)