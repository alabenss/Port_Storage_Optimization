from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database.base import Base



class StoragePosition(Base):

    __tablename__ = "storage_position"


    id = Column(
        Integer,
        primary_key=True
    )


    zone_id = Column(
        Integer,
        ForeignKey("storage_zone.id"),
        nullable=False,
        index=True
    )


    position_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )


    position_type = Column(
        String,
        nullable=False,
        index=True
    )


    row_code = Column(
        String,
        nullable=True
    )


    slot_number = Column(
        Integer,
        nullable=True
    )


    level = Column(
        Integer,
        default=1
    )


    max_stack_level = Column(
        Integer,
        default=1
    )


    max_weight = Column(
        Float,
        default=0
    )


    current_weight = Column(
        Float,
        default=0
    )


    occupied = Column(
        Boolean,
        default=False,
        index=True
    )


    active = Column(
        Boolean,
        default=True
    )


    accessibility_score = Column(
        Float,
        default=0.5
    )


    # =====================================
    # DIGITAL MAP COORDINATES
    # =====================================

    x_coordinate = Column(
        Float,
        nullable=True
    )


    y_coordinate = Column(
        Float,
        nullable=True
    )


    # =====================================
    # REAL GPS COORDINATES FOR LEAFLET MAP
    # =====================================

    latitude = Column(
        Float,
        nullable=True
    )


    longitude = Column(
        Float,
        nullable=True
    )


    # =====================================
    # PHYSICAL DIMENSIONS
    # =====================================

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



    zone = relationship(
        "StorageZone",
        back_populates="positions"
    )


    allocations = relationship(
        "Allocation",
        back_populates="position",
        cascade="all, delete-orphan"
    )