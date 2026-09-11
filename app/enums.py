from enum import Enum

class BodyType(str, Enum):
    HATCHBACK = "Hatchback"
    SEDAN = "Sedan"
    SUV = "SUV"
    COMPACT_SUV = "Compact SUV"
    MUV = "MUV"
    LUXURY = "Luxury"
    CONVERTIBLE = "Convertible"
    COUPE = "Coupe"
    PICKUP = "Pickup"

class FuelType(str, Enum):
    PETROL = "Petrol"
    DIESEL = "Diesel"
    CNG = "CNG"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"

class Transmission(str, Enum):
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"
