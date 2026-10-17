"""
Quick manual test for Level 1 classes.
Run with:  python test_level1.py
"""

from models.product import Product, PerishableProduct


def main():
    # --- create a normal product ---
    rice = Product(product_id=101, name="Rice 5kg", price=350, quantity=20)
    print(rice)                 # uses __str__
    print(rice.describe())      # base describe()

    # --- create a perishable product (inheritance + override) ---
    milk = PerishableProduct(
        product_id=202, name="Milk 1L", price=55,
        quantity=30, expiry_date="2026-10-20"
    )
    print(milk)                 # overridden __str__
    print(milk.describe())      # overridden describe()

    # --- encapsulation: setter rejects invalid data ---
    try:
        rice.quantity = -5
    except ValueError as e:
        print("Caught expected error:", e)

    # --- stock reduction after a "sale" ---
    rice.reduce_stock(5)
    print("After selling 5:", rice)
    print("Needs reorder?", rice.needs_reorder())

    # --- dunder __eq__ ---
    rice_again = Product(product_id=101, name="Rice 5kg", price=350, quantity=0)
    print("rice == rice_again:", rice == rice_again)   # True, same product_id

    # --- class method ---
    data = {"product_id": 303, "name": "Sugar 1kg", "price": 45, "quantity": 15}
    sugar = Product.from_dict(data)
    print("Built from dict:", sugar)

    # --- static method ---
    print("Is 45 a valid price?", Product.is_valid_price(45))
    print("Is -10 a valid price?", Product.is_valid_price(-10))


if __name__ == "__main__":
    main()
