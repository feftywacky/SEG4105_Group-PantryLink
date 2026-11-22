from datetime import date

import pytest

from app.core import services
from app.data.repository import Repository

TODAY = date(2027, 3, 1)


@pytest.fixture
def repo():
    r = Repository()
    r.add_lot("Milk", "Dairy", 50, "2027-03-10", "A", "2027-03-01")
    r.add_lot("Milk", "Dairy", 30, "2027-03-04", "B", "2027-03-01")
    r.add_lot("Milk", "Dairy", 40, "2027-02-27", "C", "2027-02-20")  # already expired
    return r


def test_fefo_picks_earliest_unexpired_lot_first(repo):
    res = services.place_order(repo, {"agency": "Shelter 1", "item": "milk", "quantity_kg": 45}, today=TODAY)
    assert res["status"] == "FILLED"
    assert res["picks"] == [{"lot_id": 2, "quantity_kg": 30}, {"lot_id": 1, "quantity_kg": 15}]


def test_partial_and_backorder(repo):
    assert services.place_order(repo, {"agency": "X", "item": "Milk", "quantity_kg": 100}, today=TODAY)["status"] == "PARTIAL"
    assert services.place_order(repo, {"agency": "X", "item": "Milk", "quantity_kg": 1}, today=TODAY)["status"] == "BACKORDERED"


def test_donation_validation(repo):
    with pytest.raises(services.ValidationError):
        services.record_donation(repo, {"item": "Rice", "category": "Dry", "donor": "D", "quantity_kg": 5,
                                        "expiry": "2027-01-01"}, today=TODAY)
    with pytest.raises(services.ValidationError):
        services.record_donation(repo, {"item": "Rice", "category": "Dry", "donor": "D", "quantity_kg": -1,
                                        "expiry": "2027-12-01"}, today=TODAY)


def test_expiring_soon(repo):
    ids = [l["id"] for l in services.expiring_soon(repo, days=7, today=TODAY)]
    assert 2 in ids and 1 not in ids
