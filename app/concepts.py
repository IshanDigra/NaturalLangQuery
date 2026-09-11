# Fuzzy-phrase -> filter mapping
CONCEPTS = {
    "family car": {"seats_min": 6},
    "family cars": {"seats_min": 6},
    "high safety": {"safety_rating_min": 4},
    "safe": {"safety_rating_min": 4},
    "safest": {"safety_rating_min": 5},
    "fuel efficient": {"mileage_min": 18.0},
    "good mileage": {"mileage_min": 18.0},
    "low mileage": {"km_max": 30000},
    "less driven": {"km_max": 30000},
    "almost new": {"km_max": 10000, "year_min": 2023},
    "cheap": {"price_max": 500000},
    "affordable": {"price_max": 800000},
    "budget": {"price_max": 800000},
    "premium": {"price_min": 2000000},
    "luxury": {"price_min": 2500000},
    "spacious": {"seats_min": 5, "body_type": ["SUV", "MUV"]},
}
