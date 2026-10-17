"""
Quick manual test for Level 4 (concurrency & performance).
Run with:  python test_level4.py
"""

from db.database import init_db, add_product, get_all_products
from concurrency.tasks import (
    run_stock_watcher_demo, run_multiprocessing_demo, run_asyncio_demo,
)


def main():
    init_db()
    if not get_all_products():
        add_product(name="Rice 5kg", price=360, quantity=15, reorder_level=5)
        add_product(name="Milk 1L", price=55, quantity=3, reorder_level=5)
        add_product(name="Sugar 1kg", price=45, quantity=50, reorder_level=10)

    print("=== Threading demo (background stock watcher) ===")
    run_stock_watcher_demo()

    print("\n=== Multiprocessing demo (inventory value: single vs multi) ===")
    run_multiprocessing_demo()

    print("\n=== AsyncIO demo (concurrent supplier price fetches) ===")
    run_asyncio_demo()

    print("\nCheck inventory.log for the logged messages too.")


if __name__ == "__main__":
    main()
