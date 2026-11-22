"""Data access layer: SQLite persistence for food lots, agencies and orders."""
import sqlite3
import threading

SCHEMA = """
CREATE TABLE IF NOT EXISTS lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity_kg REAL NOT NULL CHECK (quantity_kg >= 0),
    expiry TEXT NOT NULL,            -- ISO date YYYY-MM-DD
    donor TEXT NOT NULL,
    received TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agency TEXT NOT NULL,
    item TEXT NOT NULL,
    requested_kg REAL NOT NULL,
    allocated_kg REAL NOT NULL,
    status TEXT NOT NULL,
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS order_lines (
    order_id INTEGER NOT NULL REFERENCES orders(id),
    lot_id INTEGER NOT NULL REFERENCES lots(id),
    quantity_kg REAL NOT NULL
);
"""


class Repository:
    def __init__(self, path=":memory:"):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._conn.executescript(SCHEMA)

    # ---- lots
    def add_lot(self, item, category, quantity_kg, expiry, donor, received):
        with self._lock, self._conn:
            cur = self._conn.execute(
                "INSERT INTO lots (item, category, quantity_kg, expiry, donor, received) VALUES (?,?,?,?,?,?)",
                (item, category, quantity_kg, expiry, donor, received))
            return cur.lastrowid

    def count_lots(self):
        return self._conn.execute("SELECT COUNT(*) FROM lots").fetchone()[0]

    def list_lots(self, in_stock_only=True):
        sql = "SELECT * FROM lots" + (" WHERE quantity_kg > 0" if in_stock_only else "") + " ORDER BY expiry, id"
        return [dict(r) for r in self._conn.execute(sql)]

    def lots_for_item(self, item):
        """Lots of one item that still have stock, earliest expiry first (FEFO order)."""
        rows = self._conn.execute(
            "SELECT * FROM lots WHERE lower(item) = lower(?) AND quantity_kg > 0 ORDER BY expiry, id", (item,))
        return [dict(r) for r in rows]

    # ---- orders
    def save_order(self, agency, item, requested_kg, picks, status, created):
        """Persist an order and decrement the picked lots in one transaction."""
        with self._lock, self._conn:
            allocated = sum(q for _, q in picks)
            cur = self._conn.execute(
                "INSERT INTO orders (agency, item, requested_kg, allocated_kg, status, created) VALUES (?,?,?,?,?,?)",
                (agency, item, requested_kg, allocated, status, created))
            oid = cur.lastrowid
            for lot_id, qty in picks:
                self._conn.execute("UPDATE lots SET quantity_kg = quantity_kg - ? WHERE id = ?", (qty, lot_id))
                self._conn.execute("INSERT INTO order_lines VALUES (?,?,?)", (oid, lot_id, qty))
            return oid

    def list_orders(self):
        return [dict(r) for r in self._conn.execute("SELECT * FROM orders ORDER BY id")]
