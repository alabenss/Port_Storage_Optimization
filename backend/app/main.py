from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine
from app.database.database import SessionLocal
from app.database.base import Base

import app.models

from app.models import (
    import_job,
    cargo_unit,
    vehicle,
    container,
    trailer,
    bill_of_lading,
    allocation,
    movement,
    storage_position,
    storage_zone
)

from app.routers import importer
from app.routers import storage
from app.routers import cargo
from app.routers import dashboard
from app.routers import optimization
from app.routers import intelligence
from app.routers import ai_dashboard
from app.routers import reports
from app.routers import auth
from app.services.init_storage import initialize_storage


# Keep this import because your Operations endpoints
# are already working in Swagger.
try:
    from app.routers import operations
except ImportError:
    operations = None


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Port Storage Optimization Platform",
    description=(
        "Intelligent cargo storage management, "
        "automatic allocation and optimization system."
    ),
    version="1.0.0"
)

# =========================================================
# INITIALIZE STORAGE SYSTEM
# =========================================================

@app.on_event("startup")
def startup():

    db = SessionLocal()

    try:

        result = initialize_storage(db)

        print(
            "STORAGE INITIALIZATION:",
            result
        )

    finally:

        db.close()


# =========================================================
# CORS
# Allows React/Vite frontend to communicate with FastAPI
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    importer.router,
    prefix="/import",
    tags=["Import"]
)

app.include_router(
    storage.router,
    prefix="/storage",
    tags=["Storage"]
)

app.include_router(
    cargo.router,
    prefix="/cargo",
    tags=["Cargo"]
)

app.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    optimization.router,
    prefix="/optimization",
    tags=["Optimization"]
)

app.include_router(
    intelligence.router,
    prefix="/intelligence",
    tags=["Intelligence"]
)

if operations is not None:
    app.include_router(
        operations.router,
        prefix="/operations",
        tags=["Operations"]
    )
app.include_router(
    ai_dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def home():

    return {
        "message":
            "AI Port Storage Optimization Platform running",

        "frontend":
            "http://localhost:5173",

        "api_docs":
            "/docs",

        "status":
            "ONLINE"
    }
