from typing import Tuple, List, Any
from app.models import VehicleFilter
from app.enums import BodyType, FuelType, Transmission

def build_sql(filter_obj: VehicleFilter) -> Tuple[str, List[Any]]:
    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []

    if filter_obj.make:
        placeholders = ", ".join(["?"] * len(filter_obj.make))
        query += f" AND make IN ({placeholders})"
        params.extend(filter_obj.make)

    if filter_obj.model:
        placeholders = ", ".join(["?"] * len(filter_obj.model))
        query += f" AND model IN ({placeholders})"
        params.extend(filter_obj.model)

    if filter_obj.body_type:
        values = [v.value if hasattr(v, 'value') else str(v) for v in filter_obj.body_type]
        placeholders = ", ".join(["?"] * len(values))
        query += f" AND body_type IN ({placeholders})"
        params.extend(values)

    if filter_obj.fuel_type:
        values = [v.value if hasattr(v, 'value') else str(v) for v in filter_obj.fuel_type]
        placeholders = ", ".join(["?"] * len(values))
        query += f" AND fuel_type IN ({placeholders})"
        params.extend(values)

    if filter_obj.transmission:
        values = [v.value if hasattr(v, 'value') else str(v) for v in filter_obj.transmission]
        placeholders = ", ".join(["?"] * len(values))
        query += f" AND transmission IN ({placeholders})"
        params.extend(values)

    if filter_obj.city:
        placeholders = ", ".join(["?"] * len(filter_obj.city))
        query += f" AND city IN ({placeholders})"
        params.extend(filter_obj.city)

    if filter_obj.color:
        placeholders = ", ".join(["?"] * len(filter_obj.color))
        query += f" AND color IN ({placeholders})"
        params.extend(filter_obj.color)

    if filter_obj.price_min is not None:
        query += " AND price >= ?"
        params.append(filter_obj.price_min)

    if filter_obj.price_max is not None:
        query += " AND price <= ?"
        params.append(filter_obj.price_max)

    if filter_obj.km_min is not None:
        query += " AND km >= ?"
        params.append(filter_obj.km_min)

    if filter_obj.km_max is not None:
        query += " AND km <= ?"
        params.append(filter_obj.km_max)

    if filter_obj.year_min is not None:
        query += " AND year >= ?"
        params.append(filter_obj.year_min)

    if filter_obj.year_max is not None:
        query += " AND year <= ?"
        params.append(filter_obj.year_max)

    if filter_obj.seats_min is not None:
        query += " AND seats >= ?"
        params.append(filter_obj.seats_min)

    if filter_obj.seats_max is not None:
        query += " AND seats <= ?"
        params.append(filter_obj.seats_max)

    if filter_obj.mileage_min is not None:
        query += " AND mileage >= ?"
        params.append(filter_obj.mileage_min)

    if filter_obj.safety_rating_min is not None:
        query += " AND safety_rating >= ?"
        params.append(filter_obj.safety_rating_min)

    if filter_obj.features_any:
        # Use OR for ANY features matching in the features text
        feature_clauses = []
        for feat in filter_obj.features_any:
            feature_clauses.append("features LIKE ?")
            params.append(f"%{feat}%")
        if feature_clauses:
            query += " AND (" + " OR ".join(feature_clauses) + ")"

    if filter_obj.keywords:
        # Search description with LIKE for vaguely matched intent words
        kw_clauses = []
        for kw in filter_obj.keywords:
            kw_clauses.append("description LIKE ?")
            params.append(f"%{kw}%")
        if kw_clauses:
            query += " AND (" + " OR ".join(kw_clauses) + ")"

    # Note: SQLite LIMIT ? OFFSET ?
    limit = filter_obj.limit if filter_obj.limit is not None else 20
    offset = filter_obj.offset if filter_obj.offset is not None else 0

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    return query, params
