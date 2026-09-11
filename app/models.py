from pydantic import BaseModel, Field
from typing import List, Optional, Any
from app.enums import BodyType, FuelType, Transmission

class VehicleFilter(BaseModel):
    make: Optional[List[str]] = None
    model: Optional[List[str]] = None
    body_type: Optional[List[BodyType]] = None
    fuel_type: Optional[List[FuelType]] = None
    transmission: Optional[List[Transmission]] = None
    city: Optional[List[str]] = None
    color: Optional[List[str]] = None

    price_min: Optional[int] = None
    price_max: Optional[int] = None

    km_min: Optional[int] = None
    km_max: Optional[int] = None

    year_min: Optional[int] = None
    year_max: Optional[int] = None

    seats_min: Optional[int] = None
    seats_max: Optional[int] = None

    mileage_min: Optional[float] = None

    safety_rating_min: Optional[int] = None

    features_any: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

    limit: Optional[int] = Field(default=20)
    offset: Optional[int] = Field(default=0)

class Vehicle(BaseModel):
    id: int
    make: str
    model: str
    body_type: str
    fuel_type: str
    transmission: str
    city: str
    color: str
    price: int
    km: int
    year: int
    seats: int
    mileage: float
    safety_rating: int
    features: str
    description: str

class SearchResponse(BaseModel):
    query: Optional[str] = None
    interpreted_filters: VehicleFilter
    explanation: str
    parser: str
    sql: str
    sql_params: List[Any]
    relaxed: List[str]
    count: int
    results: List[Vehicle]
    latency_ms: float
