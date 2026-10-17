"""
Level 1 - OOP Foundation
Core domain class for the Inventory Management and Sales Analytics System.

Demonstrates:
- Constructor / object initialization
- Encapsulation (private attribute + property getter/setter)
- Inheritance (PerishableProduct extends Product)
- Polymorphism / method overriding (describe())
- Dunder methods (__str__, __eq__)
- Class method (from_dict)
- Static method (is_valid_price)
"""


class Product:
    """Represents a single product in the inventory."""

    def __init__(self, product_id, name, price, quantity, reorder_level=5):
        self.product_id = product_id
        self.name = name
        self.price = price
        self._quantity = 0          # private attribute (encapsulation)
        self.quantity = quantity    # goes through the setter below
        self.reorder_level = reorder_level

    # ---------- Encapsulation: property getter/setter ----------
    @property
    def quantity(self):
        """Current stock quantity (read-only from outside except via setter)."""
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            raise ValueError("Quantity cannot be negative.")
        self._quantity = value

    # ---------- Stock operations ----------
    def reduce_stock(self, amount):
        """Reduce stock after a sale. Raises an error if not enough stock."""
        if amount > self._quantity:
            raise ValueError(
                f"Cannot sell {amount} units of '{self.name}'; only "
                f"{self._quantity} in stock."
            )
        self.quantity = self._quantity - amount

    def needs_reorder(self):
        """True if stock has fallen to or below the reorder level."""
        return self._quantity <= self.reorder_level

    # ---------- Polymorphism target ----------
    def describe(self):
        """Human-readable summary. Overridden by subclasses."""
        return f"{self.name} | Rs.{self.price:.2f} | Qty: {self._quantity}"

    # ---------- Dunder methods ----------
    def __str__(self):
        return f"Product({self.product_id} - {self.name}, Rs.{self.price:.2f}, qty {self._quantity})"

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.product_id == other.product_id

    # ---------- Class method ----------
    @classmethod
    def from_dict(cls, data):
        """Build a Product from a dict, e.g. a row loaded from the database."""
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            price=data["price"],
            quantity=data.get("quantity", 0),
            reorder_level=data.get("reorder_level", 5),
        )

    # ---------- Static method ----------
    @staticmethod
    def is_valid_price(price):
        """Basic validation rule, independent of any instance."""
        return isinstance(price, (int, float)) and price > 0


class PerishableProduct(Product):
    """A product that also has an expiry date (inheritance + overriding)."""

    def __init__(self, product_id, name, price, quantity, expiry_date, reorder_level=5):
        super().__init__(product_id, name, price, quantity, reorder_level)
        self.expiry_date = expiry_date  # expected as a string or date object

    # ---------- Overridden method (polymorphism) ----------
    def describe(self):
        base = super().describe()
        return f"{base} | Expires: {self.expiry_date}"

    def __str__(self):
        return f"PerishableProduct({self.product_id} - {self.name}, expires {self.expiry_date})"
