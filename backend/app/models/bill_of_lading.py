from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.database.base import Base


class BillOfLading(Base):

    __tablename__ = "bill_of_lading"


    id = Column(
        Integer,
        primary_key=True
    )


    bl_number = Column(
        String,
        unique=True,
        nullable=False
    )


    cargo_nature = Column(
        String
    )


    description = Column(
        String
    )


    gross_weight = Column(
        Float
    )


    package_number = Column(
        Integer
    )


    cargo_units = relationship(
        "CargoUnit",
        back_populates="bill"
    )