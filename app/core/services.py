"""Core business logic: donation intake, FEFO allocation and expiry alerts."""
from datetime import date, timedelta


class ValidationError(ValueError):
    pass


def _parse_date(s, field):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be an ISO date (YYYY-MM-DD)")


def _positive(x, field):
    try:
        v = float(x)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number")
    if v <= 0:
        raise ValidationError(f"{field} must be greater than 0")
    return v


def record_donation(repo, payload, today=None):
    today = today or date.today()
    for f in ("item", "category", "donor"):
        if not str(payload.get(f, "")).strip():
            raise ValidationError(f"{f} is required")
    qty = _positive(payload.get("quantity_kg"), "quantity_kg")
    expiry = _parse_date(payload.get("expiry"), "expiry")
    if expiry < today:
        raise ValidationError("expiry is in the past; expired food cannot be received")
    lot_id = repo.add_lot(payload["item"].strip(), payload["category"].strip(), qty,
                          expiry.isoformat(), payload["donor"].strip(), today.isoformat())
    return {"lot_id": lot_id, "receipt": f"Thank you {payload['donor'].strip()} for {qty:g} kg of {payload['item'].strip()}"}


def plan_fefo(lots, requested_kg):
    """Pick from lots earliest-expiry-first until the request is met. Returns [(lot_id, kg)]."""
    picks, remaining = [], requested_kg
    for lot in sorted(lots, key=lambda l: (l["expiry"], l["id"])):
        if remaining <= 0:
            break
        take = min(lot["quantity_kg"], remaining)
        if take > 0:
            picks.append((lot["id"], take))
            remaining -= take
    return picks


def place_order(repo, payload, today=None):
    today = today or date.today()
    agency = str(payload.get("agency", "")).strip()
    item = str(payload.get("item", "")).strip()
    if not agency or not item:
        raise ValidationError("agency and item are required")
    qty = _positive(payload.get("quantity_kg"), "quantity_kg")
    lots = [l for l in repo.lots_for_item(item) if l["expiry"] >= today.isoformat()]  # never ship expired food
    picks = plan_fefo(lots, qty)
    allocated = sum(q for _, q in picks)
    status = "FILLED" if allocated >= qty else ("PARTIAL" if allocated > 0 else "BACKORDERED")
    oid = repo.save_order(agency, item, qty, picks, status, today.isoformat())
    return {"order_id": oid, "status": status, "requested_kg": qty, "allocated_kg": allocated,
            "picks": [{"lot_id": i, "quantity_kg": q} for i, q in picks]}


def expiring_soon(repo, days=7, today=None):
    today = today or date.today()
    cutoff = (today + timedelta(days=days)).isoformat()
    out = []
    for lot in repo.list_lots():
        if lot["expiry"] <= cutoff:
            lot["days_left"] = (date.fromisoformat(lot["expiry"]) - today).days
            out.append(lot)
    return out
