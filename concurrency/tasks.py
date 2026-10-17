"""
Level 4 - Concurrency & Performance

Demonstrates:
- logging
- exception handling / assertions
- multithreading (I/O-bound background task)
- multiprocessing (CPU-bound computation)
- AsyncIO (multiple simulated API calls)
- performance measurement
"""

import asyncio
import logging
import multiprocessing
import threading
import time

from db.database import get_all_products, get_low_stock_products

# ---------------------- LOGGING ----------------------
logging.basicConfig(
    filename="inventory.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def log_and_print(message, level="info"):
    print(message)
    getattr(logging, level)(message)


# ---------------------- MULTITHREADING ----------------------
def stock_watcher(stop_event, interval_seconds=2, cycles=3):
    """
    Background thread that periodically checks for low-stock products.
    Simulates an I/O-bound task (e.g. polling the database every few seconds).
    """
    count = 0
    while not stop_event.is_set() and count < cycles:
        try:
            low_stock = get_low_stock_products()
            if low_stock:
                names = ", ".join(p["name"] for p in low_stock)
                log_and_print(f"[Thread] Low stock alert: {names}")
            else:
                log_and_print("[Thread] Stock check OK, nothing low.")
        except Exception as e:  # exception handling
            log_and_print(f"[Thread] Error during stock check: {e}", level="error")
        count += 1
        time.sleep(interval_seconds)
    stop_event.set()


def run_stock_watcher_demo():
    stop_event = threading.Event()
    t = threading.Thread(target=stock_watcher, args=(stop_event,))
    t.start()
    t.join()  # wait for the demo cycles to finish


# ---------------------- MULTIPROCESSING ----------------------
def _value_of_one_product(product):
    """CPU-ish work unit: used by the multiprocessing pool below."""
    # a little artificial work so the timing difference is visible
    total = 0
    for _ in range(200_000):
        total += 1
    return product["price"] * product["quantity"]


def total_value_multiprocess(products):
    """Compute total inventory value using multiple processes."""
    assert isinstance(products, list), "products must be a list"
    if not products:
        return 0
    with multiprocessing.Pool(processes=min(4, len(products))) as pool:
        values = pool.map(_value_of_one_product, products)
    return sum(values)


def total_value_single_process(products):
    """Same calculation, single process -- used to compare timing."""
    return sum(_value_of_one_product(p) for p in products)


def run_multiprocessing_demo():
    products = get_all_products()
    if not products:
        log_and_print("[Process] No products to process.")
        return

    start = time.perf_counter()
    single_result = total_value_single_process(products)
    single_time = time.perf_counter() - start

    start = time.perf_counter()
    multi_result = total_value_multiprocess(products)
    multi_time = time.perf_counter() - start

    log_and_print(f"[Process] Single-process result={single_result}, time={single_time:.3f}s")
    log_and_print(f"[Process] Multi-process  result={multi_result}, time={multi_time:.3f}s")


# ---------------------- ASYNCIO ----------------------
async def fetch_supplier_price(supplier_name, delay):
    """Simulates an API call to a supplier for a price quote."""
    await asyncio.sleep(delay)  # stands in for real network latency
    return {"supplier": supplier_name, "price": 100 + delay * 10}


async def fetch_all_supplier_prices():
    """Run several simulated API calls concurrently instead of one by one."""
    suppliers = [("SupplierA", 1.0), ("SupplierB", 0.5), ("SupplierC", 1.5)]
    tasks = [fetch_supplier_price(name, delay) for name, delay in suppliers]
    results = await asyncio.gather(*tasks)
    return results


def run_asyncio_demo():
    start = time.perf_counter()
    results = asyncio.run(fetch_all_supplier_prices())
    elapsed = time.perf_counter() - start
    log_and_print(f"[AsyncIO] Got {len(results)} quotes in {elapsed:.3f}s (concurrently): {results}")
