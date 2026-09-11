import time
import os
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from app.models import VehicleFilter, SearchResponse, Vehicle
from app.db import get_connection
from app.llm_parser import parse_llm
from app.fallback_parser import parse_fallback
from app.validation import validate_and_clamp
from app.sql_builder import build_sql
from app.relaxation import relax_query, count_results
from app.explain import explain_filter
from app.cache import get_cached, set_cached, reset_cache

load_dotenv()
app = FastAPI(title="AI Vehicle Search Engine")

class SearchRequest(BaseModel):
    query: str

def execute_query(sql: str, params: List[Any]) -> List[Vehicle]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append(Vehicle(**dict(row)))
    return results

@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest, no_llm: bool = Query(False)):
    start_time = time.time()

    cached = get_cached(req.query)
    if cached:
        # Just update latency on cached
        cached['latency_ms'] = round((time.time() - start_time) * 1000, 2)
        return cached

    llm_enabled = bool(os.getenv("GEMINI_API_KEY")) and not no_llm

    parser_used = "fallback"
    filters = None

    if llm_enabled:
        filters = parse_llm(req.query)
        if filters:
            parser_used = "llm"

    if not filters:
        filters = parse_fallback(req.query)

    filters = validate_and_clamp(filters)

    # Check if empty, then relax
    relaxed_msgs = []
    if count_results(filters) == 0:
        filters, relaxed_msgs = relax_query(filters)

    sql, params = build_sql(filters)
    results = execute_query(sql, params)

    explanation = explain_filter(filters)

    latency_ms = round((time.time() - start_time) * 1000, 2)

    resp = {
        "query": req.query,
        "interpreted_filters": filters.model_dump(),
        "explanation": explanation,
        "parser": parser_used,
        "sql": sql,
        "sql_params": params,
        "relaxed": relaxed_msgs,
        "count": len(results),
        "results": [r.model_dump() for r in results],
        "latency_ms": latency_ms
    }

    set_cached(req.query, resp)
    return resp

@app.post("/search/filters", response_model=SearchResponse)
async def search_filters(req: VehicleFilter):
    start_time = time.time()

    filters = validate_and_clamp(req)

    relaxed_msgs = []
    if count_results(filters) == 0:
        filters, relaxed_msgs = relax_query(filters)

    sql, params = build_sql(filters)
    results = execute_query(sql, params)

    explanation = explain_filter(filters)
    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "query": None,
        "interpreted_filters": filters.model_dump(),
        "explanation": explanation,
        "parser": "explicit",
        "sql": sql,
        "sql_params": params,
        "relaxed": relaxed_msgs,
        "count": len(results),
        "results": [r.model_dump() for r in results],
        "latency_ms": latency_ms
    }

@app.get("/vehicles/{id}", response_model=Optional[Vehicle])
async def get_vehicle(id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Vehicle(**dict(row))
    return None

@app.get("/stats")
async def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT make, COUNT(*) FROM vehicles GROUP BY make")
    makes = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return {"total_vehicles": total, "by_make": makes}

@app.get("/health")
async def health():
    llm_enabled = bool(os.getenv("GEMINI_API_KEY"))
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        count = cursor.fetchone()[0]
    except Exception:
        count = 0
    finally:
        conn.close()

    return {
        "status": "ok",
        "llm_enabled": llm_enabled,
        "llm_model": os.getenv("GEMINI_MODEL") if llm_enabled else None,
        "vehicle_count": count
    }

@app.get("/examples")
async def examples():
    return {
        "examples": [
            "Show SUVs under 15L",
            "Family cars with high safety ratings",
            "Diesel automatic below 80k km",
            "Something reliable for city commuting",
            "Electric convertible with 10 seats under 1 lakh"
        ]
    }

@app.post("/cache/reset")
async def clear_cache():
    reset_cache()
    return {"status": "cache cleared"}
