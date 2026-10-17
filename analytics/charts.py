"""
Level 6 - Analytics & Visualization

Demonstrates:
- at least two Matplotlib charts built from Pandas data
- reorder-alert logic built on the Level 5 data layer
"""

import matplotlib
matplotlib.use("Agg")  # safe for headless/non-GUI runs; Tkinter embeds separately
import matplotlib.pyplot as plt

from data_handling.data_tools import products_to_dataframe, low_stock_dataframe


# ---------------------- CHART 1 ----------------------
def plot_stock_value_by_product(save_path="chart_stock_value.png"):
    """Bar chart: stock value (price * quantity) per product."""
    df = products_to_dataframe()
    if df.empty:
        print("No data to plot.")
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["name"], df["stock_value"], color="#4C72B0")
    ax.set_title("Stock Value by Product")
    ax.set_xlabel("Product")
    ax.set_ylabel("Stock Value (price x quantity)")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


# ---------------------- CHART 2 ----------------------
def plot_quantity_vs_reorder_level(save_path="chart_reorder.png"):
    """Grouped bar chart: current quantity vs reorder level per product."""
    df = products_to_dataframe()
    if df.empty:
        print("No data to plot.")
        return None

    x = range(len(df))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([i - width / 2 for i in x], df["quantity"], width, label="Current Qty", color="#55A868")
    ax.bar([i + width / 2 for i in x], df["reorder_level"], width, label="Reorder Level", color="#C44E52")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["name"], rotation=30, ha="right")
    ax.set_title("Current Stock vs Reorder Level")
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    return save_path


# ---------------------- REORDER ALERTS ----------------------
def get_reorder_alerts():
    """
    Returns a list of human-readable alert strings for products that
    need restocking (quantity <= reorder_level).
    """
    df = low_stock_dataframe()
    if df.empty:
        return []
    alerts = []
    for _, row in df.iterrows():
        alerts.append(
            f"REORDER: '{row['name']}' has {row['quantity']} left "
            f"(reorder level is {row['reorder_level']})"
        )
    return alerts
