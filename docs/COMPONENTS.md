# Software Components

## 1. Component Inventory

| Component / Module | Directory / File Path | Primary Responsibility | Key Dependencies |
| :--- | :--- | :--- | :--- |
| Application factory | `/app/__init__.py` | Builds the Flask app, wires the repository into config, seeds sample data, registers blueprints | Flask |
| Presentation / UI | `/app/api/routes.py` (`web_bp`) | HTML inventory dashboard (`/`) and liveness check (`/health`) | Flask, Jinja2 templates |
| REST API / Controller | `/app/api/routes.py` (`api_bp`) | Parses JSON requests, calls core services, maps `ValidationError` to HTTP 400 | Flask, `app.core.services` |
| Core Logic / Service | `/app/core/services.py` | Business rules: donation intake validation, FEFO allocation (`plan_fefo`), order status (FILLED / PARTIAL / BACKORDERED), expiry alerts | Python standard library (`datetime`) |
| Data Access / Storage | `/app/data/repository.py` | SQLite schema, lot/order queries, transactional order save that decrements picked lots | SQLite (`sqlite3`) |
| Seed data | `/app/data/seed.py` | Loads sample lots so a fresh container shows a realistic warehouse | `Repository` |
| Test suite | `/tests/` | Unit tests for services and HTTP tests for the API (8 tests) | pytest, Flask test client |
| Container | `/Dockerfile`, `/.dockerignore` | Builds the production image served by Gunicorn | `python:3.12-slim`, Gunicorn |

## 2. External Interfaces & APIs

- **Input Interfaces:**
  - `POST /api/donations` - JSON `{item, category, quantity_kg, expiry, donor}`; rejects missing fields, non-positive quantities and past expiry dates.
  - `POST /api/orders` - JSON `{agency, item, quantity_kg}`; allocates stock FEFO, never from expired lots.
  - `GET /api/alerts/expiring?days=N` - query parameter for the alert window (default 7 days).
  - Environment variable `PANTRYLINK_DB` - SQLite file path (default: in-memory).
- **Output Interfaces:**
  - JSON payloads: lot list, donation receipt (`lot_id`, `receipt`), order result (`order_id`, `status`, `allocated_kg`, `picks`).
  - HTTP status codes: `201` created, `400` validation error with `{"error": "..."}`.
  - Database writes to `lots`, `orders` and `order_lines` tables.
  - HTML dashboard at `/` highlighting lots that expire within 7 days.
