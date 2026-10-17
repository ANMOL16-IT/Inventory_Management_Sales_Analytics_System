"""
Quick manual test for Level 2 (database + CRUD).
Run with:  python test_level2.py
"""

from db.database import (
    init_db, add_product, get_all_products, get_product_by_id,
    update_product, reduce_stock_in_db, delete_product, get_low_stock_products,
)


def main():
    init_db()  # creates inventory.db and the products table if needed

    # --- CREATE ---
    rice_id = add_product(name="Rice 5kg", price=350, quantity=20, reorder_level=5)
    milk_id = add_product(name="Milk 1L", price=55, quantity=3, reorder_level=5,
                           expiry_date="2026-10-20")
    print(f"Inserted Rice with id={rice_id}, Milk with id={milk_id}")

    # --- READ ---
    print("\nAll products:")
    for p in get_all_products():
        print(" ", p)

    print("\nSingle lookup (rice):", get_product_by_id(rice_id))

    # --- UPDATE ---
    update_product(rice_id, price=360)
    print("\nAfter price update:", get_product_by_id(rice_id))

    # --- Stock reduction (simulates a sale) ---
    new_qty = reduce_stock_in_db(rice_id, 5)
    print(f"\nSold 5 units of rice, new quantity = {new_qty}")

    try:
        reduce_stock_in_db(rice_id, 10000)
    except ValueError as e:
        print("Caught expected error:", e)

    # --- Low stock check ---
    print("\nLow stock products (milk should appear, qty=3 <= reorder 5):")
    for p in get_low_stock_products():
        print(" ", p)

    # --- DELETE ---
    deleted = delete_product(milk_id)
    print(f"\nDeleted milk? {deleted}")
    print("All products after delete:")
    for p in get_all_products():
        print(" ", p)


if __name__ == "__main__":
    main()
