import aiohttp
import logging

logger = logging.getLogger(__name__)

async def get_coordinates(city_name: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "eKsiegowaBot_Alex_Pro/1.0"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return float(data[0]["lon"]), float(data[0]["lat"])
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
    return None, None

async def calculate_driving_hours(route: str) -> float:
    if not route or "-" not in route: return 0.0
    try:
        parts = route.split("-")
        lon1, lat1 = await get_coordinates(parts[0].strip())
        lon2, lat2 = await get_coordinates(parts[1].strip())
        if not all([lon1, lat1, lon2, lat2]): return 0.0
        
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
        async with aiohttp.ClientSession() as session:
            async with session.get(osrm_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == "Ok":
                        return round((data["routes"][0]["duration"] / 3600) * 2) / 2
    except Exception as e:
        logger.error(f"Navigation routing error: {e}")
    return 0.0

async def get_country_by_city(city_name: str) -> str:
    clean_city = city_name.split('/')[-1].strip() if '/' in city_name else city_name.strip()
    if not clean_city: return "PL"
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": clean_city, "format": "json", "addressdetails": 1, "limit": 1}
    headers = {"User-Agent": "eKsiegowaBot_Alex_Pro/1.0"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data: return data[0].get("address", {}).get("country_code", "").upper()
    except Exception as e:
        logger.error(f"Geo API country lookup error: {e}")
    return "PL"