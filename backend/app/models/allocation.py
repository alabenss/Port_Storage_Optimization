from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    String
)

from sqlalchemy.orm import relationship

from datetime import datetime

from app.database.base import Base


class Allocation(Base):

    __tablename__ = "allocation"

    id = Column(
        Integer,
        primary_key=True
    )

    cargo_id = Column(
        Integer,
        ForeignKey("cargo_unit.id"),
        nullable=False,
        index=True
    )

    position_id = Column(
        Integer,
        ForeignKey("storage_position.id"),
        nullable=False,
        index=True
    )

    # Actual amount of cargo assigned to THIS position.
    allocated_weight = Column(
        Float,
        default=0
    )

    status = Column(
        String,
        default="ACTIVE",
        index=True
    )

    allocation_method = Column(
        String,
        default="AUTOMATIC"
    )

    score = Column(
        Float,
        nullable=True
    )

    reason = Column(
        String,
        nullable=True
    )

    allocated_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    released_at = Column(
        DateTime,
        nullable=True
    )

    cargo = relationship(
        "CargoUnit",
        back_populates="allocations"
    )

    position = relationship(
        "StoragePosition",
        back_populates="allocations"
    )