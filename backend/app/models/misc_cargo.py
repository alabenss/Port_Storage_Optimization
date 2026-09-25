from sqlalchemy import (
    Column,
    Integer,
    Float,
    Boolean,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.base import Base



class MiscCargo(Base):

    __tablename__ = "misc_cargo"


    id = Column(
        Integer,
        primary_key=True
    )


    cargo_unit_id = Column(
        Integer,
        ForeignKey(
            "cargo_unit.id"
        ),
        nullable=False
    )


    cargo_category = Column(
        String,
        nullable=False
    )


    weight = Column(
        Float,
        default=0
    )


    quantity = Column(
        Integer,
        default=1
    )


    # packages can stack
    stackable = Column(
        Boolean,
        default=False
    )


    # bulk needs silo
    requires_silo = Column(
        Boolean,
        default=False
    )


    cargo_unit = relationship(
        "CargoUnit",
        back_populates="misc_cargo"
    )