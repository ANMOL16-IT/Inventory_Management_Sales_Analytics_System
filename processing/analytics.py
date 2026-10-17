"""
Level 3 - Functional Processing
Functional-programming utilities that work on top of the Level 2 database layer.

Demonstrates:
- lambda expressions
- map(), filter(), reduce()
- comprehensions
- a generator
- a custom iterator/iterable
- a decorator
- a closure
"""

import functools
import time
from db.database import get_all_products


# ---------------------- DECORATOR ----------------------
def log_timing(func):
    """Decorator that logs how long a function took to run."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[LOG] {func.__name__} took {elapsed:.6f} seconds")
        return result
    return wrapper


# ---------------------- CLOSURE ----------------------
def make_discount_applier(discount_percent):
    """
    Returns a function that applies a fixed discount percentage to a price.
    discount_percent and the inner function form a closure.
    """
    def apply_discount(price):
        return round(price * (1 - discount_percent / 100), 2)
    return apply_discount


# ---------------------- GENERATOR ----------------------
def stream_products():
    """
    Yields products one at a time instead of loading everything into a
    list at once. Useful for processing large inventories efficiently.
    """
    for product in get_all_products():
        yield product


# ---------------------- CUSTOM ITERATOR ----------------------
class InventoryIterator:
    """A simple iterable/iterator wrapping a list of products."""

    def __init__(self, products):
        self._products = products
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._products):
            raise StopIteration
        product = self._products[self._index]
        self._index += 1
        return product


# ---------------------- lambda / map / filter / reduce ----------------------
@log_timing
def total_inventory_value(products):
    """Total value of all stock = sum(price * quantity) using map + reduce."""
    values = map(lambda p: p["price"] * p["quantity"], products)
    return functools.reduce(lambda total, v: total + v, values, 0)


def low_stock_products(products):
    """Products at or below their reorder level, using filter()."""
    return list(filter(lambda p: p["quantity"] <= p["reorder_level"], products))


def product_names_sorted_by_price(products):
    """Names of products sorted by price, cheapest first (lambda as sort key)."""
    sorted_products = sorted(products, key=lambda p: p["price"])
    return [p["name"] for p in sorted_products]  # comprehension


def apply_discount_to_all(products, discount_percent):
    """Return {name: discounted_price} for every product, using a closure."""
    apply_discount = make_discount_applier(discount_percent)
    return {p["name"]: apply_discount(p["price"]) for p in products}  # comprehension
