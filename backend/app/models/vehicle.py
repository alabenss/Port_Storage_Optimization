from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.base import Base


class Vehicle(Base):

    __tablename__ = "vehicle"


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


    chassis_number = Column(
        String,
        unique=True,
        nullable=False
    )


    registration_number = Column(
        String,
        nullable=True
    )


    manufacturer = Column(
        String,
        nullable=True
    )


    model = Column(
        String,
        nullable=True
    )


    vehicle_type = Column(
        String,
        nullable=True
    )


    year = Column(
        Integer,
        nullable=True
    )


    engine_cylinders = Column(
        Integer,
        nullable=True
    )


    loaded_weight = Column(
        Float,
        nullable=True
    )


    cargo_unit = relationship(
        "CargoUnit",
        back_populates="vehicles"
    )