from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.base import Base



class Trailer(Base):

    __tablename__ = "trailer"


    id = Column(
        Integer,
        primary_key=True
    )


    cargo_unit_id = Column(
        Integer,
        ForeignKey(
            "cargo_unit.id"
        ),
        nullable=True
    )


    reference = Column(
        String
    )


    trailer_type = Column(
        String
    )


    weight = Column(
        Float
    )


    cargo_unit = relationship(
        "CargoUnit",
        back_populates="trailers"
    )