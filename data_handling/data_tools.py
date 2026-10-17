"""
Level 5 - Data Handling & Validation

Demonstrates:
- NumPy (numeric calculations)
- Pandas (loading/cleaning/aggregating)
- Regular expressions (validation)
- CSV and JSON (structured data exchange)
"""

import csv
import json
import re

import numpy as np
import pandas as pd

from db.database import get_all_products

# ---------------------- REGEX VALIDATION ----------------------
PRODUCT_CODE_PATTERN = re.compile(r"^[A-Z]{2}\d{3,5}$")      # e.g. RI1023
EMAIL_PATTERN = re.compile(r"^[\w.\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
PHONE_PATTERN = re.compile(r"^\d{10}$")


def is_valid_product_code(code):
    """e.g. 'RI1023' is valid, 'rice123' is not."""
    return bool(PRODUCT_CODE_PATTERN.match(code))


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email))


def is_valid_phone(phone):
    return bool(PHONE_PATTERN.match(phone))


# ---------------------- PANDAS / NUMPY ANALYTICS ----------------------
def products_to_dataframe():
    """Load all products from the database into a Pandas DataFrame."""
    products = get_all_products()
    df = pd.DataFrame(products)
    if df.empty:
        return df
    df["stock_value"] = df["price"] * df["quantity"]  # derived column
    return df


def inventory_summary():
    """
    Use Pandas for aggregation and NumPy for the numeric summary stats.
    Returns a dict of useful figures for the analytics/report layer.
    """
    df = products_to_dataframe()
    if df.empty:
        return {"total_products": 0}

    prices = df["price"].to_numpy()  # NumPy array
    return {
        "total_products": len(df),
        "total_stock_value": float(df["stock_value"].sum()),
        "average_price": float(np.mean(prices)),
        "price_std_dev": float(np.std(prices)),
        "most_expensive": df.loc[df["price"].idxmax(), "name"],
        "lowest_stock": df.loc[df["quantity"].idxmin(), "name"],
    }


def low_stock_dataframe():
    """Pandas filtering: products at or below reorder level."""
    df = products_to_dataframe()
    if df.empty:
        return df
    return df[df["quantity"] <= df["reorder_level"]]


# ---------------------- CSV EXPORT / IMPORT ----------------------
def export_products_csv(filepath="products_export.csv"):
    df = products_to_dataframe()
    df.to_csv(filepath, index=False)
    return filepath


def import_products_csv(filepath):
    """Read a CSV of products back into a list of dicts (ready for add_product)."""
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------- JSON EXPORT / IMPORT ----------------------
def export_products_json(filepath="products_export.json"):
    products = get_all_products()
    with open(filepath, "w") as f:
        json.dump(products, f, indent=2)
    return filepath


def import_products_json(filepath):
    with open(filepath) as f:
        return json.load(f)
