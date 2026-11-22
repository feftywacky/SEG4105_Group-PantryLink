"""Presentation / API layer: REST endpoints and a simple HTML dashboard."""
from flask import Blueprint, current_app, jsonify, render_template_string, request

from app.core import services

api_bp = Blueprint("api", __name__)
web_bp = Blueprint("web", __name__)


def repo():
    return current_app.config["REPO"]


@api_bp.errorhandler(services.ValidationError)
def bad_request(err):
    return jsonify(error=str(err)), 400


@web_bp.get("/health")
def health():
    return jsonify(status="ok", service="pantrylink")


@api_bp.get("/lots")
def list_lots():
    return jsonify(repo().list_lots())


@api_bp.post("/donations")
def create_donation():
    return jsonify(services.record_donation(repo(), request.get_json(silent=True) or {})), 201


@api_bp.post("/orders")
def create_order():
    return jsonify(services.place_order(repo(), request.get_json(silent=True) or {})), 201


@api_bp.get("/orders")
def list_orders():
    return jsonify(repo().list_orders())


@api_bp.get("/alerts/expiring")
def expiring():
    days = request.args.get("days", default=7, type=int)
    return jsonify(services.expiring_soon(repo(), days))


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>PantryLink</title>
<style>body{font-family:system-ui,sans-serif;margin:2rem;color:#1d2b36}h1{color:#1a5276}
table{border-collapse:collapse;min-width:640px}th,td{border:1px solid #ccd;padding:.4rem .7rem;text-align:left}
th{background:#1a5276;color:#fff}tr.soon td{background:#fdebd0}</style></head><body>
<h1>PantryLink &mdash; Capital Harvest Food Bank</h1>
<p>Live inventory by lot, earliest expiry first (FEFO). Highlighted rows expire within 7 days.</p>
<table><tr><th>Lot</th><th>Item</th><th>Category</th><th>Qty (kg)</th><th>Expiry</th><th>Donor</th></tr>
{% for l in lots %}<tr class="{{ 'soon' if l.id in soon else '' }}"><td>{{ l.id }}</td><td>{{ l.item }}</td>
<td>{{ l.category }}</td><td>{{ '%g' % l.quantity_kg }}</td><td>{{ l.expiry }}</td><td>{{ l.donor }}</td></tr>{% endfor %}
</table><p>API: <code>/api/lots</code> &middot; <code>/api/alerts/expiring</code> &middot;
<code>POST /api/donations</code> &middot; <code>POST /api/orders</code> &middot; <code>/health</code></p></body></html>"""


@web_bp.get("/")
def dashboard():
    soon = {l["id"] for l in services.expiring_soon(repo(), 7)}
    return render_template_string(PAGE, lots=repo().list_lots(), soon=soon)
