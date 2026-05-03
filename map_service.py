import aiohttp
import logging

logger = logging.getLogger(__name__)

async def get_coordinates(city_name: str):
    """Переводит название города в GPS координаты (долгота, широта)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    # Добавили "Accept-Encoding": "gzip, deflate", чтобы сервер не слал нам формат "br"
    headers = {
        "User-Agent": "eKsiegowaBot_Logistics/1.0",
        "Accept-Encoding": "gzip, deflate" 
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return float(data[0]["lon"]), float(data[0]["lat"])
        except Exception as e:
            logger.error(f"Ошибка геокодирования для {city_name}: {e}")
    return None, None

async def calculate_driving_hours(route: str) -> float:
    """
    Принимает строку вида 'Познань - Берлин',
    считает время в пути через OSRM и возвращает часы с округлением.
    """
    if not route or "-" not in route:
        return 0.0
    
    try:
        parts = route.split("-")
        origin = parts[0].strip()
        destination = parts[1].strip()
        
        # 1. Получаем координаты точек А и Б
        lon1, lat1 = await get_coordinates(origin)
        lon2, lat2 = await get_coordinates(destination)
        
        if not all([lon1, lat1, lon2, lat2]):
            logger.warning(f"Не удалось найти координаты для маршрута: {route}")
            return 0.0
            
        # 2. Стучимся в навигатор OSRM
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
        params = {"overview": "false"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(osrm_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == "Ok":
                        duration_seconds = data["routes"][0]["duration"]
                        duration_hours = duration_seconds / 3600
                        
                        # 3. ОКРУГЛЕНИЕ: до ближайших 0.5 часа (30 минут)
                        # Если нужно до десятых, используй: round(duration_hours, 1)
                        rounded_hours = round(duration_hours * 2) / 2
                        
                        return rounded_hours
    except Exception as e:
        logger.error(f"Ошибка OSRM навигации: {e}")
        
    return 0.0