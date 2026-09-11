# AI Vehicle Search Engine

A production-grade backend service that transforms natural language queries into SQL database searches. Users can send free-form sentences and receive matching vehicles, along with a clear explanation of how the query was interpreted.

See `design.md` for a comprehensive overview of the system architecture and design principles.

## Features

Three query types work out of the box, seamlessly resolving varying levels of intent:

| Type | Example | Handling Mechanism |
|---|---|---|
| **Hard filters** | "Diesel automatic below 80k km" | Extracted via LLM (or regex fallback) into a structured filter object, then converted to parameterized SQL. |
| **Fuzzy concepts** | "Family cars with high safety ratings" | Mapped via a concept table directly to concrete database fields (e.g., `seats >= 6`, `safety_rating >= 4`). |
| **Vague intent** | "Something reliable for city commuting" | Executes a keyword match against the vehicle description text for best-effort semantic search. |

## Quickstart & Setup

Follow these step-by-step instructions to get the service running locally.

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your machine.

### 2. Virtual Environment
It's recommended to run the service within an isolated virtual environment.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Copy the example environment file to create your local `.env`.
```bash
cp .env.example .env
```
*(Optional)* Add a Gemini API key to `.env` (`GEMINI_API_KEY=your_key_here`) for LLM parsing. Without a key, the service will automatically fallback to an offline regex/keyword parser. You can get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

### 4. Database Seeding
Initialize the SQLite database with curated mock data.
```bash
python -m scripts.seed
```
This generates `data/vehicles.db` containing ~450 vehicle rows (using a fixed random seed for reproducibility).

### 5. Running the Service
Start the FastAPI server.
```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to interact with the API via the **Swagger UI**.

---

## Environment Variables

All variables are optional. Define them in your `.env` file to customize behavior.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | *(empty)* | If unset, the service strictly uses the offline fallback parser. |
| `GEMINI_MODEL` | `gemini-2.0-flash` | The Gemini model to use for LLM parsing (must support `generateContent` + `response_schema`). |
| `GEMINI_TIMEOUT_SECONDS` | `8` | The request timeout limit before reverting to the offline parser. |
| `DB_PATH` | `data/vehicles.db` | The filepath to the SQLite database. |

---

## API Documentation

### Natural Language Search
`POST /search`

Processes a natural language string and returns matched vehicles alongside the system's interpretation.

**Request**
```bash
curl -s -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show SUVs under 15L"}'
```
*Note: Append `?no_llm=true` to the URL to force the offline parser, even if a key is configured.*

**Response Details**
- `interpreted_filters`: The exact parsed constraints.
- `explanation`: A human-readable summary of the query interpretation.
- `parser`: Indicates `"llm"` or `"fallback"`.
- `sql`: The parameterized SQL query executed.
- `relaxed`: Explains any constraints that were widened or dropped to avoid returning empty results.
- `results`: The matching vehicle rows.

### Structured Search
`POST /search/filters`

Performs a strict database search bypassing the LLM completely.

**Request**
```bash
curl -s -X POST "http://127.0.0.1:8000/search/filters" \
  -H "Content-Type: application/json" \
  -d '{"fuel_type": ["Diesel"], "seats_min": 7, "limit": 5}'
```

### Additional Endpoints

- **`GET /vehicles/{id}`**: Retrieve detailed information for a single vehicle.
- **`GET /stats`**: Returns catalogue totals and category breakdowns.
- **`GET /health`**: Returns system status, indicating if the LLM path is enabled and which model is configured.
- **`GET /examples`**: Returns sample demo queries for testing.
- **`POST /cache/reset`**: Clears the in-memory query cache.

---

## Testing & Evaluation

The project includes an evaluation harness to benchmark parser accuracy against a suite of test queries. It verifies that interpreted constraints correctly map to expected values.

- Run with the **fallback parser only** (No API key needed):
  ```bash
  python -m tests.eval
  ```
- Run with the **Gemini LLM parser** (Requires `GEMINI_API_KEY` in your `.env`):
  ```bash
  python -m tests.eval --llm
  ```

Add or modify test cases in `tests/eval_queries.json`.
