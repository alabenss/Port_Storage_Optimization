from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_database
from app.services.cargo_service import classify_cargo



router = APIRouter()



@router.get("/cargo/{cargo_id}/classify")
def classify(

    cargo_id:int,

    db:Session = Depends(get_database)

):

    return classify_cargo(
        db,
        cargo_id
    )