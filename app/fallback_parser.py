import re
from typing import Dict, Any, List
from app.models import VehicleFilter
from app.concepts import CONCEPTS
from app.enums import BodyType, FuelType, Transmission
from app.catalog import CATALOG, CITIES, COLORS

def parse_fallback(query: str) -> VehicleFilter:
    query_lower = query.lower()
    filters: Dict[str, Any] = {}

    # 1. Apply concepts
    for phrase, concept_filters in CONCEPTS.items():
        if phrase in query_lower:
            for k, v in concept_filters.items():
                filters[k] = v

    # 2. Hard filters extraction via Regex and Keywords

    # Price
    # Matches "under 15L", "below 80k", "under 1 lakh"
    price_match = re.search(r'(under|below)\s+(\d+(?:\.\d+)?)\s*(lakh|l|k)', query_lower)
    if price_match:
        val = float(price_match.group(2))
        unit = price_match.group(3)
        if unit in ['lakh', 'l']:
            filters['price_max'] = int(val * 100000)
        elif unit == 'k':
            filters['price_max'] = int(val * 1000)

    # KM
    # Matches "below 80k km", "under 50000 km"
    km_match = re.search(r'(under|below)\s+(\d+(?:\.\d+)?)\s*(k)?\s*km', query_lower)
    if km_match:
        val = float(km_match.group(2))
        unit = km_match.group(3)
        if unit == 'k':
            filters['km_max'] = int(val * 1000)
        else:
            filters['km_max'] = int(val)

    # Seats
    seats_match = re.search(r'(\d+)\s*seats?', query_lower)
    if seats_match:
        filters['seats_min'] = int(seats_match.group(1))

    # Vocabs
    found_body_types = []
    # Hardcode mapping for 'suv' to include 'compact suv' like the README implies
    if 'suv' in query_lower:
        found_body_types.extend([BodyType.SUV, BodyType.COMPACT_SUV])
    else:
        for bt in BodyType:
            if bt.value.lower() in query_lower:
                found_body_types.append(bt)

    if found_body_types:
        existing = filters.get('body_type', [])
        if isinstance(existing, list):
            filters['body_type'] = list(set(existing + found_body_types))

    found_fuel_types = []
    for ft in FuelType:
        if ft.value.lower() in query_lower:
            found_fuel_types.append(ft)
    if found_fuel_types:
        filters['fuel_type'] = found_fuel_types

    found_transmissions = []
    for tr in Transmission:
        if tr.value.lower() in query_lower:
            found_transmissions.append(tr)
    if found_transmissions:
        filters['transmission'] = found_transmissions

    found_cities = []
    for city in CITIES:
        if city.lower() in query_lower:
            found_cities.append(city)
    if found_cities:
        filters['city'] = found_cities

    found_colors = []
    for color in COLORS:
        if color.lower() in query_lower:
            found_colors.append(color)
    if found_colors:
        filters['color'] = found_colors

    # Makes and Models
    ambiguous_models = {"city", "punch", "compass", "endeavour"}

    found_makes = set()
    found_models = set()

    for item in CATALOG:
        make = item['make']
        model = item['model']
        make_l = make.lower()
        model_l = model.lower()

        if make_l in query_lower:
            found_makes.add(make)

        if model_l in query_lower:
            if model_l in ambiguous_models:
                if make_l in query_lower:
                    found_models.add(model)
                    found_makes.add(make)
            else:
                found_models.add(model)

    if found_makes:
        filters['make'] = list(found_makes)
    if found_models:
        filters['model'] = list(found_models)

    # 3. Vague intent -> keywords
    stop_words = {"show", "me", "some", "cars", "vehicles", "looking", "for", "with", "a", "an", "the", "in", "under", "below"}
    words = [w for w in re.findall(r'\b\w+\b', query_lower) if w not in stop_words]

    meaningful_words = []
    for w in words:
        if not any(w in str(v).lower() for v in filters.values()):
            meaningful_words.append(w)

    if meaningful_words and not filters: # Only if really vague
        filters['keywords'] = meaningful_words

    return VehicleFilter(**filters)
