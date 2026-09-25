from pydantic import BaseModel
from typing import Optional


# =========================================================
# POSITION RESPONSE
# =========================================================

class PositionResponse(BaseModel):

    id: int

    zone_id: int

    position_code: str

    position_type: str


    row_code: Optional[str] = None

    slot_number: Optional[int] = None


    level: Optional[int] = None

    max_stack_level: Optional[int] = None


    max_weight: Optional[float] = None

    current_weight: Optional[float] = None


    occupied: Optional[bool] = None

    active: Optional[bool] = None


    accessibility_score: Optional[float] = None



    # ==========================
    # DIGITAL MAP COORDINATES
    # ==========================

    x_coordinate: Optional[float] = None

    y_coordinate: Optional[float] = None



    # ==========================
    # REAL GPS COORDINATES
    # ==========================

    latitude: Optional[float] = None

    longitude: Optional[float] = None



    length: Optional[float] = None

    width: Optional[float] = None

    height: Optional[float] = None



    class Config:

        from_attributes = True


# =========================================================
# ZONE RESPONSE
# =========================================================

class ZoneResponse(BaseModel):

    id: int

    code: str

    name: str

    zone_type: Optional[str] = None

    capacity: float


    class Config:
        from_attributes = True



# =========================================================
# ALLOCATION RESPONSE
# =========================================================

class AllocationResponse(BaseModel):

    id: int

    cargo_id: int

    position_id: int

    status: str


    class Config:
        from_attributes = True



# =========================================================
# CREATE ZONE
# =========================================================

class ZoneCreate(BaseModel):

    code: str

    name: str

    zone_type: str

    capacity: float

    latitude: float | None = None

    longitude: float | None = None



# =========================================================
# UPDATE ZONE
# =========================================================

class ZoneUpdate(BaseModel):

    code: Optional[str] = None

    name: Optional[str] = None

    zone_type: Optional[str] = None

    capacity: Optional[float] = None



# =========================================================
# CREATE POSITION
# =========================================================

class PositionCreate(BaseModel):

    zone_id: int

    position_code: str

    position_type: str

    max_weight: float

    latitude: float | None = None

    longitude: float | None = None



# =========================================================
# UPDATE POSITION
# =========================================================

class PositionUpdate(BaseModel):

    zone_id: Optional[int] = None

    position_code: Optional[str] = None

    position_type: Optional[str] = None

    max_weight: Optional[float] = None
