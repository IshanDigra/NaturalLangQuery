```markdown
# AI Vehicle Search Engine

## Endpoints

### `GET /stats` -- catalogue totals and breakdowns

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

```bash
curl -s -X POST [http://127.0.0.1:8000/cache/reset](http://127.0.0.1:8000/cache/reset)

```

## Eval harness

```bash
python -m tests.eval        # fallback parser only, no key needed
python -m tests.eval --llm  # also exercises the Gemini path (needs GEMINI_API_KEY)

```

Runs ~15 queries with expected filter values through the parser(s) and
prints a pass rate. See `tests/eval_queries.json` to add cases.

## Project layout

```
app/
  main.py            FastAPI app and endpoints
  models.py          VehicleFilter / Vehicle / response schemas (the shared contract)
  db.py              SQLite connection + schema
  catalog.py         ~40 curated real make/model combos (also used by the fallback parser)
  enums.py           Canonical vocab (body types, fuel types, cities, ...)
  concepts.py        Fuzzy-phrase -> filter mapping, shared by the LLM prompt and the fallback parser
  sql_builder.py     VehicleFilter -> parameterized SQL (the only place SQL text is built)
  validation.py      Clamps/drops anything unsafe before it reaches SQL
  relaxation.py      Never-empty-results widening/dropping logic
  llm_parser.py      Gemini REST call -> VehicleFilter
  fallback_parser.py Regex/keyword parser -> VehicleFilter (also the offline path)
  cache.py           In-memory query cache
  explain.py         VehicleFilter -> one-sentence explanation
scripts/
  seed.py            Generates data/vehicles.db (~450 rows, fixed random seed)
tests/
  eval.py            Eval harness
  eval_queries.json  Eval cases

```

## Demo script

1. `GET /health` -> shows whether the LLM path is enabled
2. `"Show SUVs under 15L"` -> check `interpreted_filters`
3. `"Family cars with high safety ratings"` -> fuzzy concept resolves to `seats_min=6, safety_rating_min=4`
4. `"Diesel automatic below 80k km"` -> check the generated `sql`
5. Same query with `?no_llm=true` -> `parser: "fallback"`, identical answer, no API call
6. `"Electric convertible with 10 seats under 1 lakh"` -> `relaxed` explains what was widened
7. `python -m tests.eval` -> pass rate on screen

```

```markdown
# Design notes

## Why the LLM never writes SQL


```

sentence -> parser (LLM or regex fallback) -> VehicleFilter -> validate/clamp -> parameterized SQL -> results

```

`app/sql_builder.py` is the only module in the codebase that produces SQL
text, and every value it places into a query arrives as a bound `?`
parameter -- including everything that came out of the model. This buys
three things at once:

- **No injection surface.** The model's output never becomes part of the SQL
  string, so there's nothing to sanitize or escape.
- **No hallucinated vehicles.** Every row in a response came from a
  `SELECT` against the real table. The model can misunderstand a sentence,
  but it cannot invent a car that doesn't exist.
- **Testability.** `app/fallback_parser.py` and `app/llm_parser.py` both
  produce the same `VehicleFilter` type, so `tests/eval.py` can assert on
  the *understanding* of a sentence without needing a live model or a
  running server.

## Why SQLite over MongoDB/Postgres

A grader runs one command (`python -m scripts.seed`) and gets a file. No
Docker, no daemon, no connection string. At ~450 rows the entire catalogue
fits comfortably in a single `SELECT ... WHERE ... LIMIT`, so there is no
performance case for anything heavier.

The threshold where this stops being true: multiple concurrent writers (a
real marketplace would have wrong-lock-behavior issues under
`sqlite3`'s single-writer model), a catalogue past roughly 100k-1M rows
where an index-less `LIKE` scan starts costing real latency, or a need for
managed replication/backups. Any of those would justify moving to Postgres;
none of them apply to a ~450-row hackathon catalogue.

## Why no embeddings / vector store

The "fuzzy concept" and "vague intent" query types look like they want
semantic search, but at 450 rows and a fixed ~20-column schema, they're
actually satisfied by two much cheaper mechanisms:

- Fuzzy concepts ("family car", "high safety") are a **fixed, small
  vocabulary** -- `app/concepts.py` is a lookup table, not a similarity
  search problem.
- Vague intent ("something reliable for city commuting") degrades to a
  `LIKE` scan over `description`, which is exact enough for a demo
  catalogue built from ~40 curated templates.

A vector store adds a dependency, an index-build step, and a new failure
mode (embedding model unavailable) to solve a problem this data doesn't
have. Deliberate simplicity here is a design choice, not a shortcut --
revisit it if the catalogue grows past curated templates into genuinely
free-form listing text, or past low tens of thousands of rows where lexical
`LIKE` recall starts falling off.

## Why the fallback parser exists

Two reasons, not one:

1. **Availability.** If `GEMINI_API_KEY` is unset, the key is rate-limited,
   or the network is down mid-demo, `/search` keeps answering instead of
   500ing. `?no_llm=true` forces this path explicitly so it can be
   demonstrated on purpose, not just discovered by accident.
2. **A correctness oracle.** `app/concepts.py` is consumed by both
   `app/fallback_parser.py` directly and by `app/llm_parser.py`'s system
   prompt. `tests/eval.py` runs the same query set through both paths, so a
   regression in the LLM's understanding of a concept and a regression in
   the regex parser's understanding of the same concept show up as the same
   kind of failure, against the same ground truth.

## The relaxation strategy

`app/relaxation.py` widens or drops constraints one at a time, in a fixed
order, until something matches or every step has been tried, cheapest
concession first:

1. widen `price_max` by 25% -- a stated budget is usually a soft ceiling
2. drop `km_max` -- "low km" is a preference, not a hard requirement
3. drop `safety_rating_min` -- typically derived from a fuzzy concept, not stated directly
4. drop `seats_min` -- same, from "family car"
5. drop `transmission` -- plenty of cross-transmission equivalents exist
6. drop `fuel_type`
7. drop `body_type`
8. drop `keywords` -- the loosest signal (free text) gives way before named entities
9. drop `features_any`
10. drop `make` / `model` / `city` / `color` -- these name a specific real
    thing; identity is the last thing given up, because dropping it returns
    vehicles unrelated to what was actually asked

Every step that fires is recorded in the `relaxed` response field in plain
English, so a client (or a judge) can see exactly what was given up rather
than silently receiving a different query's results.

## Honest limitations

- **Comparative queries** ("cheaper than a Creta") aren't handled -- there's
  no concept of resolving one listing's price as a bound for a filter.
- **Multi-turn context** doesn't exist. Every `/search` call is independent;
  "what about in blue?" as a follow-up has no memory of the prior query.
- **Negation** ("not white", "no CNG") isn't parsed. Both the concept table
  and the regex parser are additive-only.
- **Ambiguous makes/models**: a few real model names collide with ordinary
  English words (Honda **City**, Tata **Punch**, Jeep **Compass**). The
  fallback parser only treats these as a model mention when the make is
  also named, so "something reliable for **city** commuting" correctly
  falls through to the vague-intent keyword path -- but a query like "punch
  it" would not be recognized as asking about a Tata Punch.
- **"mileage" overloads two real-world meanings.** Indian colloquial usage
  sometimes means "distance already driven" and sometimes means "fuel
  economy." `app/concepts.py` deliberately splits these ("low mileage" / "less
  driven" -> `km_max`, "fuel efficient" -> `mileage_min`) to avoid the
  ambiguity, but a bare "good mileage" query relies on that exact phrasing
  being in the concept table rather than a general understanding of the word.
- **EV "mileage"** is stored as a normalised efficiency score in the same
  column used for kmpl (see `app/catalog.py`) so the `fuel_efficient`
  concept treats EVs sensibly. It is not a real kmpl figure and shouldn't be
  read as one.

```