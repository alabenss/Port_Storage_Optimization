from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_database

from app.models.user import User


router = APIRouter()



@router.post("/login")
def login(

    username:str,

    password:str,

    db:Session=Depends(get_database)

):


    user = (

        db.query(User)

        .filter(
            User.username==username
        )

        .first()

    )


    if not user:

        raise HTTPException(
            404,
            "User not found"
        )


    if user.password != password:

        raise HTTPException(
            401,
            "Invalid password"
        )


    return {


        "status":
        "SUCCESS",


        "user":{

            "id":user.id,

            "username":
            user.username,


            "role":
            user.role

        }

    }