"""
Quick manual test for Level 6 (analytics & visualization).
Run with:  python test_level6.py
"""

from db.database import init_db, add_product, get_all_products
from analytics.charts import (
    plot_stock_value_by_product, plot_quantity_vs_reorder_level, get_reorder_alerts,
)


def main():
    init_db()
    if len(get_all_products()) < 3:
        add_product(name="Rice 5kg", price=360, quantity=15, reorder_level=5)
        add_product(name="Milk 1L", price=55, quantity=2, reorder_level=5)
        add_product(name="Sugar 1kg", price=45, quantity=50, reorder_level=10)
        add_product(name="Oil 1L", price=180, quantity=4, reorder_level=6)

    path1 = plot_stock_value_by_product()
    print("Saved chart 1 to:", path1)

    path2 = plot_quantity_vs_reorder_level()
    print("Saved chart 2 to:", path2)

    print("\nReorder alerts:")
    alerts = get_reorder_alerts()
    if not alerts:
        print("  None - all stock levels are fine.")
    for a in alerts:
        print(" ", a)


if __name__ == "__main__":
    main()
