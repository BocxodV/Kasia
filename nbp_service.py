import aiohttp
import logging
from datetime import datetime

# Setup module-level logger
logger = logging.getLogger(__name__)

async def get_eur_rate(shift_date: str = None):
    """
    Asynchronously retrieves the Euro (EUR) exchange rate from the NBP API.
    If shift_date (format YYYY-MM-DD) is provided, requests the rate for that specific day.
    Falls back to a standard default rate (4.30 PLN/EUR) if the API call fails or times out.
    """
    DEFAULT_FALLBACK_RATE = 4.30
    
    # If no date is provided, request the latest current exchange rate
    if not shift_date:
        url = "http://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
    else:
        # Request the exchange rate for the specified historical date
        url = f"http://api.nbp.pl/api/exchangerates/rates/a/eur/{shift_date}/?format=json"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    rate = data['rates'][0]['mid']
                    return rate
                
                # If HTTP 404 is returned (weekend or public holiday),
                # fallback to fetching the latest available current rate.
                elif response.status == 404 and shift_date:
                    logger.warning(f"Exchange rate for {shift_date} not found. Attempting to fetch current rate.")
                    current_rate = await get_eur_rate()
                    return current_rate if current_rate else DEFAULT_FALLBACK_RATE
                
                else:
                    logger.error(f"NBP API error: HTTP status {response.status}. Using fallback rate: {DEFAULT_FALLBACK_RATE}")
                    return DEFAULT_FALLBACK_RATE
                    
    except Exception as e:
        logger.error(f"Failed to connect to NBP API: {e}. Using fallback rate: {DEFAULT_FALLBACK_RATE}", exc_info=True)
        return DEFAULT_FALLBACK_RATE