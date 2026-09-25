from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean
)

from sqlalchemy.orm import relationship

from app.database.base import Base


class StorageZone(Base):

    __tablename__ = "storage_zone"

    id = Column(
        Integer,
        primary_key=True
    )

    code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    zone_type = Column(
        String,
        nullable=False,
        index=True
    )

    description = Column(
        String,
        nullable=True
    )

    capacity = Column(
        Float,
        default=0
    )

    priority_score = Column(
        Float,
        default=0.5
    )

    active = Column(
        Boolean,
        default=True
    )

    # Coordinates on the digital port map.
    # These are NOT GPS yet.
    map_x = Column(
        Float,
        nullable=True
    )

    map_y = Column(
        Float,
        nullable=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    positions = relationship(
        "StoragePosition",
        back_populates="zone",
        cascade="all, delete-orphan"
    )