"""
Level 7 - GUI, API & Integration

Ties every earlier level together behind a Tkinter interface:
- Products tab  -> db.database CRUD (Level 2), Product class (Level 1)
- Sales tab     -> record_sale() (Level 7 addition to Level 2's db)
- Reports tab   -> processing.analytics (Level 3), concurrency.tasks (Level 4),
                   data_handling.data_tools (Level 5), analytics.charts (Level 6)
- Currency panel -> api.supplier_api (AsyncIO REST call)
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from db.database import (
    init_db, add_product, get_all_products, update_product,
    delete_product, record_sale, get_all_sales,
)
from data_handling.data_tools import inventory_summary, export_products_csv, export_products_json
from analytics.charts import plot_stock_value_by_product, plot_quantity_vs_reorder_level, get_reorder_alerts
from api.supplier_api import get_usd_to_inr_rate_sync

# ---------- colour palette (kept in one place so the look is easy to tweak) ----------
BG = "#F4F6F8"
PRIMARY = "#2F5D8A"
ACCENT = "#4C9F70"
DANGER = "#C44E52"
TEXT = "#1F2A37"


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management & Sales Analytics System")
        self.geometry("960x580")
        self.minsize(900, 520)
        self.configure(bg=BG)

        self._init_style()
        init_db()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.products_tab = ProductsTab(notebook)
        self.sales_tab = SalesTab(notebook, on_sale=self.products_tab.refresh)
        self.reports_tab = ReportsTab(notebook)

        notebook.add(self.products_tab, text="  Products  ")
        notebook.add(self.sales_tab, text="  Record Sale  ")
        notebook.add(self.reports_tab, text="  Reports & Analytics  ")

    def _init_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground=PRIMARY)
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Primary.TButton", background=PRIMARY, foreground="white")
        style.map("Primary.TButton", background=[("active", "#254A6E")])
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


class ProductsTab(ttk.Frame):
    """CRUD screen for products."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Products", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        form = ttk.Frame(self)
        form.grid(row=1, column=0, sticky="w", padx=14)

        self.name_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.reorder_var = tk.StringVar(value="5")

        for i, (label, var) in enumerate([
            ("Name", self.name_var), ("Price", self.price_var),
            ("Quantity", self.qty_var), ("Reorder level", self.reorder_var),
        ]):
            ttk.Label(form, text=label).grid(row=0, column=i * 2, padx=(0, 4))
            ttk.Entry(form, textvariable=var, width=12).grid(row=0, column=i * 2 + 1, padx=(0, 12))

        ttk.Button(form, text="Add Product", style="Primary.TButton",
                   command=self.add_product).grid(row=0, column=8, padx=(6, 0))

        columns = ("id", "name", "price", "qty", "reorder")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for col, label, width in [
            ("id", "ID", 50), ("name", "Name", 220), ("price", "Price", 100),
            ("qty", "Quantity", 100), ("reorder", "Reorder Level", 110),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w")
        self.tree.grid(row=2, column=0, sticky="nsew", padx=14, pady=10)
        self.rowconfigure(2, weight=1)

        btns = ttk.Frame(self)
        btns.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 14))
        ttk.Button(btns, text="Delete Selected", command=self.delete_selected).pack(side="left")

        self.refresh()

    def add_product(self):
        try:
            name = self.name_var.get().strip()
            price = float(self.price_var.get())
            qty = int(self.qty_var.get())
            reorder = int(self.reorder_var.get() or 5)
            if not name:
                raise ValueError("Name cannot be empty.")
            add_product(name=name, price=price, quantity=qty, reorder_level=reorder)
            self.name_var.set(""); self.price_var.set(""); self.qty_var.set("")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        product_id = self.tree.item(selected[0])["values"][0]
        delete_product(product_id)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in get_all_products():
            self.tree.insert("", "end", values=(
                p["product_id"], p["name"], f"{p['price']:.2f}", p["quantity"], p["reorder_level"]))


class SalesTab(ttk.Frame):
    """Record a sale against an existing product; shows the sales history."""

    def __init__(self, parent, on_sale=None):
        super().__init__(parent)
        self.on_sale = on_sale
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Record a Sale", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        form = ttk.Frame(self)
        form.grid(row=1, column=0, sticky="w", padx=14)

        ttk.Label(form, text="Product").grid(row=0, column=0, padx=(0, 4))
        self.product_combo = ttk.Combobox(form, state="readonly", width=28)
        self.product_combo.grid(row=0, column=1, padx=(0, 12))

        ttk.Label(form, text="Quantity sold").grid(row=0, column=2, padx=(0, 4))
        self.qty_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.qty_var, width=10).grid(row=0, column=3, padx=(0, 12))

        ttk.Button(form, text="Record Sale", style="Primary.TButton",
                   command=self.record).grid(row=0, column=4)

        columns = ("sale_id", "product", "qty", "price", "date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for col, label, width in [
            ("sale_id", "Sale ID", 70), ("product", "Product", 220), ("qty", "Qty", 70),
            ("price", "Unit Price", 100), ("date", "Date/Time", 170),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if col != "product" else "w")
        self.tree.grid(row=2, column=0, sticky="nsew", padx=14, pady=10)
        self.rowconfigure(2, weight=1)

        self._products_by_label = {}
        self.refresh_products()
        self.refresh_sales()

    def refresh_products(self):
        products = get_all_products()
        self._products_by_label = {f"{p['name']} (id {p['product_id']})": p["product_id"] for p in products}
        self.product_combo["values"] = list(self._products_by_label.keys())

    def refresh_sales(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in get_all_sales():
            self.tree.insert("", "end", values=(
                s["sale_id"], s["name"], s["quantity"], f"{s['sale_price']:.2f}", s["sale_date"]))

    def record(self):
        label = self.product_combo.get()
        if label not in self._products_by_label:
            messagebox.showerror("Missing selection", "Choose a product first.")
            return
        try:
            qty = int(self.qty_var.get())
            record_sale(self._products_by_label[label], qty)
            self.qty_var.set("")
            self.refresh_sales()
            self.refresh_products()
            if self.on_sale:
                self.on_sale()
        except (ValueError, KeyError) as e:
            messagebox.showerror("Could not record sale", str(e))


class ReportsTab(ttk.Frame):
    """Analytics summary, reorder alerts, chart generation, export, and the live API panel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Reports & Analytics", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        self.summary_box = tk.Text(self, height=8, width=70, bg="white", relief="flat")
        self.summary_box.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, sticky="w", padx=14)
        ttk.Button(btns, text="Refresh Summary", command=self.refresh_summary).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Generate Charts", style="Primary.TButton",
                   command=self.generate_charts).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Export CSV", command=self.export_csv).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Export JSON", command=self.export_json).pack(side="left")

        ttk.Label(self, text="Live USD -> INR rate (REST API over AsyncIO):",
                 style="Header.TLabel").grid(row=3, column=0, sticky="w", padx=14, pady=(18, 4))
        rate_row = ttk.Frame(self)
        rate_row.grid(row=4, column=0, sticky="w", padx=14)
        self.rate_label = ttk.Label(rate_row, text="Not fetched yet.")
        self.rate_label.pack(side="left", padx=(0, 10))
        ttk.Button(rate_row, text="Fetch Live Rate", command=self.fetch_rate_async).pack(side="left")

        self.refresh_summary()

    def refresh_summary(self):
        summary = inventory_summary()
        alerts = get_reorder_alerts()
        self.summary_box.delete("1.0", tk.END)
        if summary.get("total_products", 0) == 0:
            self.summary_box.insert(tk.END, "No products yet. Add some in the Products tab.")
            return
        for k, v in summary.items():
            self.summary_box.insert(tk.END, f"{k}: {v}\n")
        self.summary_box.insert(tk.END, "\nReorder alerts:\n")
        self.summary_box.insert(tk.END, "\n".join(alerts) if alerts else "  None")

    def generate_charts(self):
        p1 = plot_stock_value_by_product()
        p2 = plot_quantity_vs_reorder_level()
        if p1 and p2:
            messagebox.showinfo("Charts saved", f"Saved:\n{p1}\n{p2}")
        else:
            messagebox.showwarning("No data", "Add products before generating charts.")

    def export_csv(self):
        path = export_products_csv()
        messagebox.showinfo("Exported", f"Saved to {path}")

    def export_json(self):
        path = export_products_json()
        messagebox.showinfo("Exported", f"Saved to {path}")

    def fetch_rate_async(self):
        """Runs the AsyncIO API call on a background thread so the GUI never freezes."""
        self.rate_label.config(text="Fetching...")

        def worker():
            rate = get_usd_to_inr_rate_sync()
            text = f"1 USD = {rate:.2f} INR" if rate else "Could not fetch (check internet connection)."
            self.rate_label.config(text=text)

        threading.Thread(target=worker, daemon=True).start()


def main():
    app = InventoryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
