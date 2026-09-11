from app.models import VehicleFilter

def validate_and_clamp(f: VehicleFilter) -> VehicleFilter:
    """Clamps/drops anything unsafe before it reaches SQL."""

    if f.limit is None or f.limit > 100:
        f.limit = 20
    elif f.limit <= 0:
        f.limit = 1

    if f.offset is None or f.offset < 0:
        f.offset = 0

    if f.price_min is not None and f.price_min < 0:
        f.price_min = 0
    if f.price_max is not None and f.price_max < 0:
        f.price_max = 0

    if f.price_min and f.price_max and f.price_min > f.price_max:
        f.price_min, f.price_max = f.price_max, f.price_min

    if f.km_min is not None and f.km_min < 0:
        f.km_min = 0
    if f.km_max is not None and f.km_max < 0:
        f.km_max = 0

    if f.km_min and f.km_max and f.km_min > f.km_max:
        f.km_min, f.km_max = f.km_max, f.km_min

    if f.year_min is not None and f.year_min < 1900:
        f.year_min = 1900
    if f.year_max is not None and f.year_max > 2100:
        f.year_max = 2100

    if f.seats_min is not None and f.seats_min < 1:
        f.seats_min = 1
    if f.seats_max is not None and f.seats_max > 20:
        f.seats_max = 20

    if f.safety_rating_min is not None:
        if f.safety_rating_min < 0:
            f.safety_rating_min = 0
        elif f.safety_rating_min > 5:
            f.safety_rating_min = 5

    if f.mileage_min is not None and f.mileage_min < 0:
        f.mileage_min = 0

    return f
