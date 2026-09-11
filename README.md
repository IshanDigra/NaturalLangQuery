```markdown
# AI Vehicle Search Engine

A backend service where you send a sentence and get back matching vehicles
**plus the interpretation** of what was asked. See `requirement.md` for the
original brief and `DESIGN.md` for the reasoning behind the choices below.

Three query types work out of the box:

| Type | Example | How it's handled |
|---|---|---|
| Hard filters | "Diesel automatic below 80k km" | LLM (or regex fallback) -> filter object -> SQL |
| Fuzzy concepts | "Family cars with high safety ratings" | Concept table maps the phrase to concrete filter fields |
| Vague intent | "Something reliable for city commuting" | Keyword match against the description text |

## Quickstart (5 commands)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional -- add a Gemini key here for LLM parsing
python -m scripts.seed          # generates data/vehicles.db (~450 rows, fixed seed)
uvicorn app.main:app --reload

```

Open http://127.0.0.1:8000/docs for interactive Swagger docs.

**Runs with zero setup and no API key.** Without `GEMINI_API_KEY` set, every
`/search` call automatically uses the offline regex/keyword fallback parser
instead of erroring out (`parser: "fallback"` in the response). Get a free
key at https://aistudio.google.com/apikey if you want the LLM path too.

## Environment variables

All optional -- copy `.env.example` to `.env` and edit as needed.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | *(empty)* | If unset, the service always uses the offline fallback parser |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Any Gemini model that supports `generateContent` + `response_schema` |
| `GEMINI_TIMEOUT_SECONDS` | `8` | Request timeout before falling back to the offline parser |
| `DB_PATH` | `data/vehicles.db` | SQLite file location |

## Endpoints

### `POST /search` -- natural-language search

```bash
curl -s -X POST "[http://127.0.0.1:8000/search](http://127.0.0.1:8000/search)" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show SUVs under 15L"}'

```

Add `?no_llm=true` to force the offline parser even when a key is configured:

```bash
curl -s -X POST "[http://127.0.0.1:8000/search?no_llm=true](http://127.0.0.1:8000/search?no_llm=true)" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show SUVs under 15L"}'

```

Response shape:

```json
{
  "query": "Show SUVs under 15L",
  "interpreted_filters": {"body_type": ["SUV", "Compact SUV"], "price_max": 1500000, "limit": 20, "...": null},
  "explanation": "Looking for vehicles with body type in SUV, Compact SUV; price at most ₹1,500,000.",
  "parser": "fallback",
  "sql": "SELECT * FROM vehicles WHERE body_type IN (?, ?) AND price <= ? LIMIT ?",
  "sql_params": ["SUV", "Compact SUV", 1500000, 20],
  "relaxed": [],
  "count": 20,
  "results": ["... vehicle rows ..."],
  "latency_ms": 3.42
}

```

| Field | Why it matters |
| --- | --- |
| `interpreted_filters` | Exactly what the query was understood to mean |
| `explanation` | One sentence in plain English |
| `parser` | `"llm"` or `"fallback"` -- proves the degradation path works |
| `sql` | The parameterized statement actually executed |
| `relaxed` | Set when a constraint was widened/dropped to avoid an empty result |

### `POST /search/filters` -- structured search, no LLM involved

```bash
curl -s -X POST "[http://127.0.0.1:8000/search/filters](http://127.0.0.1:8000/search/filters)" \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": ["Diesel"], "seats_min": 7, "limit": 5}'

```

Body is a `VehicleFilter` (same shape as `interpreted_filters` above). Same
response envelope as `/search`, with `"parser": "explicit"`.

### `GET /vehicles/{id}` -- single vehicle detail

```bash
curl -s [http://127.0.0.1:8000/vehicles/1](http://127.0.0.1:8000/vehicles/1)

```

### `GET /stats` -- catalogue totals and breakdowns

```bash
curl -s [http://127.0.0.1:8000/stats](http://127.0.0.1:8000/stats)

```

### `GET /health` -- status, whether the LLM path is enabled, which model

```bash
curl -s [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
# {"status":"ok","llm_enabled":false,"llm_model":null,"vehicle_count":453}

```

### `GET /examples` -- sample demo queries

```bash
curl -s [http://127.0.0.1:8000/examples](http://127.0.0.1:8000/examples)

```

### `POST /cache/reset` -- clear the in-memory query cache

```

```