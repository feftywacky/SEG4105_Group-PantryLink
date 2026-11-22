"""Sample data so a fresh container shows a realistic warehouse."""
from datetime import date, timedelta

SAMPLE = [  # item, category, kg, days until expiry, donor
    ("Milk 2%", "Dairy", 120, 3, "Farm Boy Ottawa"),
    ("Milk 2%", "Dairy", 200, 9, "Loblaws Rideau"),
    ("Apples", "Produce", 350, 5, "Orchard Hill Farm"),
    ("Apples", "Produce", 180, 14, "Community food drive"),
    ("Canned beans", "Canned goods", 600, 400, "Metro Bank St"),
    ("Pasta", "Dry goods", 450, 300, "Costco Merivale"),
    ("Bread", "Bakery", 90, 2, "Ottawa Bagelshop"),
    ("Yogurt", "Dairy", 75, 6, "Farm Boy Ottawa"),
]


def seed(repo, today=None):
    today = today or date.today()
    for item, cat, kg, days, donor in SAMPLE:
        repo.add_lot(item, cat, kg, (today + timedelta(days=days)).isoformat(), donor, today.isoformat())
