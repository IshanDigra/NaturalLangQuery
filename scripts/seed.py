import random
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import create_schema, get_connection
from app.catalog import CATALOG, CITIES, COLORS, FEATURES
from app.enums import FuelType, Transmission

# Use a fixed seed for reproducibility
random.seed(42)

def generate_vehicle():
    template = random.choice(CATALOG)
    make = template["make"]
    model = template["model"]
    body_type = template["body_type"]
    seats = template["seats"]

    # Fuel and transmission
    if body_type == "Electric" or model == "ZS EV":
        fuel_type = FuelType.ELECTRIC
        transmission = Transmission.AUTOMATIC
    else:
        fuel_type = random.choice([FuelType.PETROL, FuelType.DIESEL, FuelType.CNG])
        transmission = random.choice([Transmission.MANUAL, Transmission.AUTOMATIC])

    city = random.choice(CITIES)
    color = random.choice(COLORS)

    year = random.randint(2015, 2024)
    # older car = cheaper & more km
    age = 2024 - year

    base_price = random.randint(300000, 4000000)
    price = int(base_price * (0.9 ** age)) # simple depreciation

    km = random.randint(1000, 150000)

    mileage = round(random.uniform(10.0, 25.0), 1)
    if fuel_type == FuelType.ELECTRIC:
        mileage = round(random.uniform(5.0, 10.0), 1) # interpret as km per kWh for EVs

    safety_rating = random.randint(2, 5)

    num_features = random.randint(2, 6)
    car_features = random.sample(FEATURES, num_features)
    features_str = ", ".join(car_features)

    description = f"A reliable {year} {make} {model} in {color}, driven {km} km. Good condition with {features_str}. Available in {city}."

    return {
        "make": make,
        "model": model,
        "body_type": body_type.value if hasattr(body_type, 'value') else body_type,
        "fuel_type": fuel_type.value if hasattr(fuel_type, 'value') else fuel_type,
        "transmission": transmission.value if hasattr(transmission, 'value') else transmission,
        "city": city,
        "color": color,
        "price": price,
        "km": km,
        "year": year,
        "seats": seats,
        "mileage": mileage,
        "safety_rating": safety_rating,
        "features": features_str,
        "description": description
    }

def main():
    create_schema()
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data just in case
    cursor.execute("DELETE FROM vehicles")

    vehicles_data = [generate_vehicle() for _ in range(453)] # specific number from doc: vehicle_count:453

    for v in vehicles_data:
        cursor.execute("""
            INSERT INTO vehicles (make, model, body_type, fuel_type, transmission, city, color, price, km, year, seats, mileage, safety_rating, features, description)
            VALUES (:make, :model, :body_type, :fuel_type, :transmission, :city, :color, :price, :km, :year, :seats, :mileage, :safety_rating, :features, :description)
        """, v)

    conn.commit()
    conn.close()
    print("Seed complete. Database populated with 453 rows.")

if __name__ == "__main__":
    main()
