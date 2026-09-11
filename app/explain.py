from app.models import VehicleFilter

def explain_filter(f: VehicleFilter) -> str:
    parts = []

    if f.make:
        parts.append(f"make in {', '.join(f.make)}")
    if f.model:
        parts.append(f"model in {', '.join(f.model)}")
    if f.body_type:
        vals = [v.value if hasattr(v, 'value') else str(v) for v in f.body_type]
        parts.append(f"body type in {', '.join(vals)}")
    if f.fuel_type:
        vals = [v.value if hasattr(v, 'value') else str(v) for v in f.fuel_type]
        parts.append(f"fuel type in {', '.join(vals)}")
    if f.transmission:
        vals = [v.value if hasattr(v, 'value') else str(v) for v in f.transmission]
        parts.append(f"transmission in {', '.join(vals)}")
    if f.city:
        parts.append(f"city in {', '.join(f.city)}")
    if f.color:
        parts.append(f"color in {', '.join(f.color)}")

    if f.price_max is not None:
        parts.append(f"price at most ₹{f.price_max:,}")
    if f.km_max is not None:
        parts.append(f"driven at most {f.km_max:,} km")
    if f.year_min is not None:
        parts.append(f"year from {f.year_min}")

    if f.seats_min is not None:
        parts.append(f"at least {f.seats_min} seats")
    if f.safety_rating_min is not None:
        parts.append(f"safety rating of at least {f.safety_rating_min}")

    if f.keywords:
        parts.append(f"matching keywords {', '.join(f.keywords)}")

    if not parts:
        return "Looking for any vehicle."

    return "Looking for vehicles with " + "; ".join(parts) + "."
