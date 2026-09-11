import copy
from typing import Tuple, List
from app.models import VehicleFilter
from app.db import get_connection
from app.sql_builder import build_sql

def count_results(f: VehicleFilter) -> int:
    query, params = build_sql(f)
    # Convert SELECT * to SELECT count(*) to test
    count_query = query.replace("SELECT *", "SELECT COUNT(*)", 1)

    # Remove LIMIT and OFFSET for counting
    count_query = count_query.rsplit(" LIMIT", 1)[0]
    count_params = params[:-2]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(count_query, count_params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def relax_query(f: VehicleFilter) -> Tuple[VehicleFilter, List[str]]:
    """
    1. widen price_max by 25% -- a stated budget is usually a soft ceiling
    2. drop km_max -- "low km" is a preference, not a hard requirement
    3. drop safety_rating_min -- typically derived from a fuzzy concept, not stated directly
    4. drop seats_min -- same, from "family car"
    5. drop transmission -- plenty of cross-transmission equivalents exist
    6. drop fuel_type
    7. drop body_type
    8. drop keywords -- the loosest signal (free text) gives way before named entities
    9. drop features_any
    10. drop make / model / city / color -- these name a specific real thing; identity is the last thing given up
    """

    relaxed = []
    curr_f = copy.deepcopy(f)

    if count_results(curr_f) > 0:
        return curr_f, relaxed

    # 1. widen price_max by 25%
    if curr_f.price_max is not None:
        old_price = curr_f.price_max
        curr_f.price_max = int(curr_f.price_max * 1.25)
        if count_results(curr_f) > 0:
            relaxed.append(f"Widened maximum price from {old_price} to {curr_f.price_max}")
            return curr_f, relaxed

    # 2. drop km_max
    if curr_f.km_max is not None:
        curr_f.km_max = None
        relaxed.append("Dropped maximum kilometer limit")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 3. drop safety_rating_min
    if curr_f.safety_rating_min is not None:
        curr_f.safety_rating_min = None
        relaxed.append("Dropped minimum safety rating requirement")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 4. drop seats_min
    if curr_f.seats_min is not None:
        curr_f.seats_min = None
        relaxed.append("Dropped minimum seats requirement")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 5. drop transmission
    if curr_f.transmission:
        curr_f.transmission = None
        relaxed.append("Dropped transmission preference")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 6. drop fuel_type
    if curr_f.fuel_type:
        curr_f.fuel_type = None
        relaxed.append("Dropped fuel type preference")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 7. drop body_type
    if curr_f.body_type:
        curr_f.body_type = None
        relaxed.append("Dropped body type preference")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 8. drop keywords
    if curr_f.keywords:
        curr_f.keywords = None
        relaxed.append("Dropped vague keywords")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 9. drop features_any
    if curr_f.features_any:
        curr_f.features_any = None
        relaxed.append("Dropped required features")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    # 10. drop make / model / city / color (drop them one by one if present)
    if curr_f.color:
        curr_f.color = None
        relaxed.append("Dropped color preference")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    if curr_f.city:
        curr_f.city = None
        relaxed.append("Dropped city constraint")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    if curr_f.model:
        curr_f.model = None
        relaxed.append("Dropped model constraint")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    if curr_f.make:
        curr_f.make = None
        relaxed.append("Dropped make constraint")
        if count_results(curr_f) > 0:
            return curr_f, relaxed

    return curr_f, relaxed
