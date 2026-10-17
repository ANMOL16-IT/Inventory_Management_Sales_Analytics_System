"""
Quick manual test for Level 3 (functional processing).
Run with:  python test_level3.py
Make sure you've run test_level2.py at least once so inventory.db has data.
"""

from db.database import init_db, add_product, get_all_products
from processing.analytics import (
    total_inventory_value, low_stock_products, product_names_sorted_by_price,
    apply_discount_to_all, stream_products, InventoryIterator,
)


def main():
    init_db()

    # Make sure there's some data to work with
    if not get_all_products():
        add_product(name="Rice 5kg", price=360, quantity=15, reorder_level=5)
        add_product(name="Milk 1L", price=55, quantity=3, reorder_level=5,
                    expiry_date="2026-10-20")
        add_product(name="Sugar 1kg", price=45, quantity=50, reorder_level=10)

    products = get_all_products()

    # --- map/filter/reduce via total_inventory_value (also shows the decorator) ---
    print("Total inventory value:", total_inventory_value(products))

    # --- filter ---
    print("\nLow stock products:")
    for p in low_stock_products(products):
        print(" ", p["name"], p["quantity"])

    # --- lambda as sort key + comprehension ---
    print("\nProducts sorted by price:", product_names_sorted_by_price(products))

    # --- closure ---
    print("\n10% discounted prices:", apply_discount_to_all(products, 10))

    # --- generator ---
    print("\nStreaming products one at a time:")
    for p in stream_products():
        print(" ", p["name"])

    # --- custom iterator ---
    print("\nIterating with InventoryIterator:")
    for p in InventoryIterator(products):
        print(" ", p["name"])


if __name__ == "__main__":
    main()
