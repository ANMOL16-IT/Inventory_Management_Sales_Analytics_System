"""
Quick manual test for Level 5 (data handling & validation).
Run with:  python test_level5.py
"""

from db.database import init_db, add_product, get_all_products
from data_handling.data_tools import (
    is_valid_product_code, is_valid_email, is_valid_phone,
    inventory_summary, low_stock_dataframe,
    export_products_csv, import_products_csv,
    export_products_json, import_products_json,
)


def main():
    init_db()
    if not get_all_products():
        add_product(name="Rice 5kg", price=360, quantity=15, reorder_level=5)
        add_product(name="Milk 1L", price=55, quantity=3, reorder_level=5)
        add_product(name="Sugar 1kg", price=45, quantity=50, reorder_level=10)

    # --- regex validation ---
    print("Product code 'RI1023' valid?", is_valid_product_code("RI1023"))
    print("Product code 'rice123' valid?", is_valid_product_code("rice123"))
    print("Email 'owner@shop.com' valid?", is_valid_email("owner@shop.com"))
    print("Phone '9876543210' valid?", is_valid_phone("9876543210"))
    print("Phone '98765' valid?", is_valid_phone("98765"))

    # --- pandas + numpy ---
    print("\nInventory summary:")
    for k, v in inventory_summary().items():
        print(f"  {k}: {v}")

    print("\nLow stock (pandas filter):")
    print(low_stock_dataframe())

    # --- CSV round trip ---
    csv_path = export_products_csv("products_export.csv")
    print(f"\nExported CSV to {csv_path}")
    print("Read back from CSV:", import_products_csv(csv_path)[:2])

    # --- JSON round trip ---
    json_path = export_products_json("products_export.json")
    print(f"\nExported JSON to {json_path}")
    print("Read back from JSON:", import_products_json(json_path)[:2])


if __name__ == "__main__":
    main()
