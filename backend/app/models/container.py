from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.base import Base



class Container(Base):

    __tablename__ = "container"


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


    container_number = Column(
        String,
        unique=True
    )


    category = Column(
        String
    )


    package_number = Column(
        Integer
    )


    gross_weight = Column(
        Float
    )


    seal_1 = Column(
        String
    )


    seal_2 = Column(
        String
    )


    seal_3 = Column(
        String
    )


    cargo_unit = relationship(
        "CargoUnit",
        back_populates="containers"
    )