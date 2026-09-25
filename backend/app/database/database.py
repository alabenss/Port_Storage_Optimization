from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///./port_storage.db"


engine = create_engine(

    DATABASE_URL,

    connect_args={

        "check_same_thread": False

    }

)


SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()



# Backward compatibility
# Some routers still use get_database

def get_database():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()