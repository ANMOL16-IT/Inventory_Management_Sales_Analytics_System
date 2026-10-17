"""
Level 7 - REST API consumption (AsyncIO).

Fetches a live USD -> INR exchange rate from a free, no-key public API
(https://open.er-api.com) so the app can show product prices converted
to another currency. This needs an internet connection to work.

NOTE: this call could not be tested inside the sandbox used to build this
project (its network access is restricted to package registries), so test
it from your own machine after downloading the project.
"""

import asyncio
import logging

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

API_URL = "https://open.er-api.com/v6/latest/USD"


async def fetch_usd_to_inr_rate():
    """Returns the current USD->INR rate as a float, or None on failure."""
    if aiohttp is None:
        logging.error("aiohttp is not installed. Run: pip install aiohttp")
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
                return data["rates"]["INR"]
    except Exception as e:
        logging.error(f"Could not fetch exchange rate: {e}")
        return None


def get_usd_to_inr_rate_sync():
    """Convenience wrapper so Tkinter code (which is synchronous) can call this easily."""
    return asyncio.run(fetch_usd_to_inr_rate())
