from sqlalchemy import Column, Integer, String, DateTime

from datetime import datetime

from app.database.base import Base


class ImportJob(Base):

    __tablename__ = "import_job"


    id = Column(
        Integer,
        primary_key=True
    )


    upload_id = Column(
        String,
        unique=True,
        nullable=False
    )


    original_filename = Column(
        String
    )


    file_path = Column(
        String
    )


    status = Column(
        String,
        default="UPLOADED"
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )