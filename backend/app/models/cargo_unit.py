from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship

from datetime import datetime

from app.database.base import Base



class CargoUnit(Base):

    __tablename__ = "cargo_unit"


    id = Column(
        Integer,
        primary_key=True
    )


    reference = Column(
        String,
        unique=True,
        nullable=False
    )


    cargo_type = Column(
        String,
        default="UNKNOWN"
    )


    cargo_category = Column(
        String,
        default="GENERAL"
    )


    weight = Column(
        Float,
        default=0
    )


    length = Column(
        Float,
        nullable=True
    )


    width = Column(
        Float,
        nullable=True
    )


    height = Column(
        Float,
        nullable=True
    )


    quantity = Column(
        Integer,
        default=1
    )


    stackable = Column(
        Boolean,
        default=False
    )


    handling_method = Column(
        String,
        default="STANDARD"
    )


    storage_profile = Column(
        String,
        default="GENERAL_STORAGE"
    )


    status = Column(
        String,
        default="IMPORTED"
    )


    arrival_date = Column(
        DateTime,
        default=datetime.utcnow
    )


    bl_id = Column(
        Integer,
        ForeignKey(
            "bill_of_lading.id"
        )
    )



    # -------------------------
    # Relationships
    # -------------------------


    bill = relationship(
        "BillOfLading",
        back_populates="cargo_units"
    )


    vehicles = relationship(
        "Vehicle",
        back_populates="cargo_unit"
    )


    containers = relationship(
        "Container",
        back_populates="cargo_unit"
    )


    trailers = relationship(
        "Trailer",
        back_populates="cargo_unit"
    )


    # FIX:
    # Required by MiscCargo model
    misc_cargo = relationship(
        "MiscCargo",
        back_populates="cargo_unit",
        cascade="all, delete-orphan"
    )


    allocations = relationship(
        "Allocation",
        back_populates="cargo",
        cascade="all, delete-orphan"
    )


    movements = relationship(
        "Movement",
        back_populates="cargo",
        cascade="all, delete-orphan",
        lazy="selectin"
    )