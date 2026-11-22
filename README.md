# PantryLink

PantryLink is a prototype of the inventory and agency-ordering service for **Capital Harvest Food Bank** (SEG 4105 term project). It records donations by lot and expiry date, picks stock **first-expiry-first-out (FEFO)** when partner agencies order, and flags lots that are about to expire so they can be distributed before they spoil.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest                                   # run the test suite
flask --app "app:create_app()" run       # http://127.0.0.1:5000
```

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | HTML dashboard of current inventory |
| GET | `/health` | Liveness check |
| GET | `/api/lots` | Inventory by lot (earliest expiry first) |
| POST | `/api/donations` | Record a donation lot |
| POST | `/api/orders` | Place an agency order (FEFO allocation) |
| GET | `/api/alerts/expiring?days=7` | Lots expiring within N days |

## Documentation
- [Software Components](docs/COMPONENTS.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Development Methodology](docs/METHODOLOGY.md)
