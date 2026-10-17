"""
Level 2 - Database & CRUD
Handles SQLite connection, schema creation, and CRUD operations
for the Product table. Suppliers/Sales tables are added in later levels.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"


def get_connection():
    """Return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the products and sales tables if they don't already exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            reorder_level INTEGER NOT NULL DEFAULT 5,
            expiry_date TEXT  -- NULL for non-perishable products
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    conn.commit()
    conn.close()


# ---------------------- CREATE ----------------------
def add_product(name, price, quantity, reorder_level=5, expiry_date=None):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO products (name, price, quantity, reorder_level, expiry_date)
           VALUES (?, ?, ?, ?, ?)""",
        (name, price, quantity, reorder_level, expiry_date),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# ---------------------- READ ----------------------
def get_all_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product_by_id(product_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM products WHERE product_id = ?", (product_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------------- UPDATE ----------------------
def update_product(product_id, **fields):
    """
    Update one or more columns for a product.
    Example: update_product(5, price=60, quantity=100)
    """
    if not fields:
        return False

    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [product_id]

    conn = get_connection()
    conn.execute(f"UPDATE products SET {columns} WHERE product_id = ?", values)
    conn.commit()
    changed = conn.total_changes
    conn.close()
    return changed > 0


def reduce_stock_in_db(product_id, amount):
    """Reduce stock after a sale, raising an error if not enough is in stock."""
    product = get_product_by_id(product_id)
    if product is None:
        raise ValueError(f"No product with id {product_id}")
    if amount > product["quantity"]:
        raise ValueError(
            f"Cannot sell {amount} units of '{product['name']}'; "
            f"only {product['quantity']} in stock."
        )
    new_qty = product["quantity"] - amount
    update_product(product_id, quantity=new_qty)
    return new_qty


# ---------------------- DELETE ----------------------
def delete_product(product_id):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
    conn.commit()
    changed = conn.total_changes
    conn.close()
    return changed > 0


# ---------------------- SALES ----------------------
def record_sale(product_id, quantity):
    """
    Record a sale: inserts a sales row AND reduces product stock,
    as a single operation. Raises ValueError if stock is insufficient.
    """
    import datetime

    product = get_product_by_id(product_id)
    if product is None:
        raise ValueError(f"No product with id {product_id}")
    if quantity <= 0:
        raise ValueError("Sale quantity must be positive.")
    if quantity > product["quantity"]:
        raise ValueError(
            f"Cannot sell {quantity} units of '{product['name']}'; "
            f"only {product['quantity']} in stock."
        )

    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO sales (product_id, quantity, sale_price, sale_date)
               VALUES (?, ?, ?, ?)""",
            (product_id, quantity, product["price"],
             datetime.datetime.now().isoformat(timespec="seconds")),
        )
        conn.execute(
            "UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
            (quantity, product_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return get_product_by_id(product_id)


def get_all_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.sale_id, s.product_id, p.name, s.quantity, s.sale_price, s.sale_date
        FROM sales s JOIN products p ON s.product_id = p.product_id
        ORDER BY s.sale_date DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ---------------------- ANALYTICS HELPER ----------------------
def get_low_stock_products():
    """Products at or below their reorder level (used again in Level 6)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE quantity <= reorder_level"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
