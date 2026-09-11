# System Design Document

This document explains the core architectural choices for the AI Vehicle Search Engine.

![Architecture](data/architecture.png)

## Core Architecture: Decoupled Natural Language Understanding

The system strictly decouples natural language understanding from database querying:

`Sentence -> Parser (LLM or Regex Fallback) -> VehicleFilter -> Validation -> Parameterized SQL -> Results`

**Why the LLM never writes SQL:**
1. **Security:** By completely avoiding dynamic SQL generation from LLM output, the system is immune to SQL injection. All outputs from the parser are bound as standard `?` parameters in a secure SQL builder (`app/sql_builder.py`).
2. **Reliability:** The model is constrained to returning filter criteria (e.g., maximum price, preferred body type). It cannot invent nonexistent columns, tables, or vehicle records.
3. **Testability:** Both the LLM parser and the fallback regex parser return identical `VehicleFilter` schemas, enabling seamless, deterministic evaluation (`tests/eval.py`) of query comprehension without requiring a live model.

## Storage Choice: SQLite

For a catalog of ~450 curated rows, SQLite is the ideal choice.
- **Simplicity:** It requires zero setup, no daemon, and no Docker container. A single file (`data/vehicles.db`) is all that is needed.
- **Performance:** The entire dataset can be queried instantly without indexes.
- **When to upgrade:** If the application requires concurrent writers, scales beyond 100k+ rows where simple `LIKE` searches become slow, or requires managed backups, migrating to Postgres would be justified.

## Search Strategy: Why No Vector Store

Despite handling "fuzzy concepts" and "vague intent," the system avoids vector embeddings for the following reasons:
- **Fuzzy concepts:** Phrases like "family car" map to a small, fixed vocabulary. These are efficiently resolved via a lookup table (`app/concepts.py`).
- **Vague intent:** Queries like "good for city commutes" fall back to lexical `LIKE` scans over vehicle descriptions, which provides sufficient recall for this dataset size.
- **Simplicity:** Avoiding vector stores removes the need for embedding models, index-building steps, and additional infrastructure dependencies.

## The Fallback Parser

The fallback offline parser exists for two critical reasons:
1. **High Availability:** If the API key is missing, rate-limited, or the network fails, the system seamlessly degrades to the fallback parser, guaranteeing that `/search` continues to function.
2. **Evaluation Baseline:** Both the LLM and fallback parsers utilize the same concept mapping (`app/concepts.py`), providing a reliable baseline to evaluate the LLM's understanding against hardcoded logic.

## Search Relaxation

To prevent returning empty results, `app/relaxation.py` implements a graceful degradation strategy. It incrementally widens or drops constraints in order of least-to-most importance:
1. Widen `price_max` (budget is often a soft limit).
2. Drop `km_max`, `safety_rating_min`, `seats_min`, `transmission`, `fuel_type`, `body_type`.
3. Drop `keywords`.
4. Drop exact identifiers (`make`, `model`) last, as they define the core identity of the request.

Every relaxation step is documented in the API response so clients are explicitly aware of which constraints were modified.

## Current Limitations

- **Comparative Queries:** Queries like "cheaper than X" are not supported.
- **Multi-turn Context:** The API is stateless; follow-up questions are treated as entirely new queries.
- **Negation:** The parser logic is additive only ("not white" is not currently supported).
- **Ambiguous Names:** Certain car models share names with common words (e.g., Honda *City*, Tata *Punch*). The fallback parser only triggers exact model matching if the manufacturer is also mentioned to avoid false positives.
