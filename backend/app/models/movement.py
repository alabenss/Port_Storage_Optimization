from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from datetime import datetime

from app.database.base import Base


class Movement(Base):

    __tablename__ = "movement"

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

    from_position = Column(
        String,
        nullable=True
    )

    to_position = Column(
        String,
        nullable=True
    )

    action = Column(
        String,
        nullable=False,
        index=True
    )

    reason = Column(
        String,
        nullable=True
    )

    performed_by = Column(
        String,
        default="SYSTEM"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    cargo = relationship(
        "CargoUnit",
        back_populates="movements"
    )