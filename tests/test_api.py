from datetime import date, timedelta

from app import create_app


def client():
    return create_app(with_seed=False).test_client()


def test_health():
    assert client().get("/health").get_json()["status"] == "ok"


def test_donation_then_order_flow():
    c = client()
    exp = (date.today() + timedelta(days=5)).isoformat()
    r = c.post("/api/donations", json={"item": "Rice", "category": "Dry goods", "quantity_kg": 25,
                                       "expiry": exp, "donor": "Food drive"})
    assert r.status_code == 201
    r = c.post("/api/orders", json={"agency": "Pantry 7", "item": "Rice", "quantity_kg": 10})
    assert r.status_code == 201 and r.get_json()["status"] == "FILLED"
    assert c.get("/api/lots").get_json()[0]["quantity_kg"] == 15
    assert len(c.get("/api/alerts/expiring?days=7").get_json()) == 1


def test_bad_request_returns_400():
    r = client().post("/api/orders", json={"agency": "", "item": "Rice", "quantity_kg": 1})
    assert r.status_code == 400 and "error" in r.get_json()


def test_dashboard_renders_seed_data():
    html = create_app().test_client().get("/").get_data(as_text=True)
    assert "PantryLink" in html and "Canned beans" in html
