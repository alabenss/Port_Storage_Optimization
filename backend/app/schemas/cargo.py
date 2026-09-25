from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# =========================================================
# CARGO
# =========================================================

class CargoResponse(BaseModel):

    id: int
    reference: str

    cargo_type: Optional[str] = None
    cargo_category: Optional[str] = None

    weight: Optional[float] = None

    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

    quantity: Optional[int] = None

    stackable: Optional[bool] = None

    handling_method: Optional[str] = None
    storage_profile: Optional[str] = None

    status: Optional[str] = None

    arrival_date: Optional[datetime] = None

    bl_id: Optional[int] = None

    class Config:
        from_attributes = True


# =========================================================
# MANUAL CARGO CREATE
# =========================================================

class ManualCargoCreate(BaseModel):

    reference: str = Field(
        ...,
        min_length=1
    )

    bl_number: Optional[str] = None

    cargo_nature: Optional[str] = None

    description: Optional[str] = None


    cargo_category: Optional[str] = None


    weight: float = Field(
        default=0,
        ge=0
    )

    quantity: int = Field(
        default=1,
        ge=1
    )

    length: Optional[float] = Field(
        default=None,
        ge=0
    )

    width: Optional[float] = Field(
        default=None,
        ge=0
    )

    height: Optional[float] = Field(
        default=None,
        ge=0
    )

    cargo_type: str = "MANUAL"


# =========================================================
# CARGO UPDATE
# =========================================================

class CargoUpdate(BaseModel):

    reference: Optional[str] = None

    cargo_type: Optional[str] = None

    cargo_category: Optional[str] = None

    weight: Optional[float] = Field(
        default=None,
        ge=0
    )

    quantity: Optional[int] = Field(
        default=None,
        ge=1
    )

    length: Optional[float] = Field(
        default=None,
        ge=0
    )

    width: Optional[float] = Field(
        default=None,
        ge=0
    )

    height: Optional[float] = Field(
        default=None,
        ge=0
    )

    stackable: Optional[bool] = None

    handling_method: Optional[str] = None

    storage_profile: Optional[str] = None

    status: Optional[str] = None


    # Bill of Lading fields

    bl_number: Optional[str] = None

    cargo_nature: Optional[str] = None

    description: Optional[str] = None


# =========================================================
# VEHICLE
# =========================================================

class VehicleResponse(BaseModel):

    id: int

    cargo_unit_id: Optional[int] = None

    chassis_number: str

    registration_number: Optional[str] = None

    manufacturer: Optional[str] = None

    model: Optional[str] = None

    vehicle_type: Optional[str] = None

    year: Optional[int] = None

    engine_cylinders: Optional[int] = None

    loaded_weight: Optional[float] = None

    class Config:
        from_attributes = True


# =========================================================
# CONTAINER
# =========================================================

class ContainerResponse(BaseModel):

    id: int

    cargo_unit_id: Optional[int] = None

    container_number: Optional[str] = None

    category: Optional[str] = None

    package_number: Optional[int] = None

    gross_weight: Optional[float] = None

    seal_1: Optional[str] = None
    seal_2: Optional[str] = None
    seal_3: Optional[str] = None

    class Config:
        from_attributes = True


# =========================================================
# TRAILER
# =========================================================

class TrailerResponse(BaseModel):

    id: int

    cargo_unit_id: Optional[int] = None

    reference: Optional[str] = None

    trailer_type: Optional[str] = None

    weight: Optional[float] = None

    class Config:
        from_attributes = True