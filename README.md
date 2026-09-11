# AI Vehicle Search Engine

A backend service for searching vehicles using natural language. Send a sentence and get back matching vehicles along with an explanation of how the query was interpreted.

**Key Features:**
- **Natural Language Parsing**: Uses LLM (Gemini) or a fallback regex parser.
- **Fuzzy Concept Mapping**: Understands phrases like "family car" or "high safety".
- **Graceful Relaxation**: Automatically widens search criteria if no vehicles match.

For architectural details, please see [design.md](design.md).

## Quickstart

Run the following commands to set up and start the server:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.seed          # Seed the SQLite database
uvicorn app.main:app --reload   # Start the server
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger documentation.

*Note: The service runs perfectly without an API key using the built-in offline parser. To enable the LLM parser, copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.*

## Environment Variables

Copy `.env.example` to `.env` to configure these optional variables:

- `GEMINI_API_KEY`: Enables LLM parsing (get one at [Google AI Studio](https://aistudio.google.com/apikey)).
- `GEMINI_MODEL`: Model to use (default: `gemini-2.0-flash`).
- `GEMINI_TIMEOUT_SECONDS`: Request timeout before fallback (default: `8`).
- `DB_PATH`: SQLite file location (default: `data/vehicles.db`).

## Endpoints

### `POST /search` (Natural Language Search)

Search for vehicles using plain English.

```bash
curl -s -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Show SUVs under 15L"}'
```
*Tip: Append `?no_llm=true` to the URL to force the offline fallback parser.*

### `POST /search/filters` (Structured Search)

Search using exact JSON filters without natural language processing.

```bash
curl -s -X POST http://127.0.0.1:8000/search/filters \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": ["Diesel"], "seats_min": 7, "limit": 5}'
```

### Other Endpoints

- **`GET /vehicles/{id}`**: Fetch details of a single vehicle.
- **`GET /stats`**: View catalog statistics and breakdowns.
- **`GET /health`**: Check system status and LLM availability.
- **`GET /examples`**: Get sample demo queries.
- **`POST /cache/reset`**: Clear the in-memory query cache.

---
*For tests and evaluation harness, run `python -m tests.eval`.*
