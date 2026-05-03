import aiohttp
import logging
from datetime import datetime

# Подключаем логгер для отслеживания ошибок
logger = logging.getLogger(__name__)

async def get_eur_rate(shift_date: str = None):
    """
    Асинхронно запрашивает курс Евро (EUR) из API NBP.
    Если передан параметр shift_date (в формате YYYY-MM-DD), запрашивает курс на этот день.
    """
    # Если дата не передана, берем текущий курс (сегодняшний)
    if not shift_date:
        url = "http://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
    else:
        # API NBP позволяет получить курс на конкретную дату через URL
        url = f"http://api.nbp.pl/api/exchangerates/rates/a/eur/{shift_date}/?format=json"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    rate = data['rates'][0]['mid']
                    return rate
                
                # Если 404 (курс не найден), значит это выходной или праздник.
                # В этом случае запрашиваем просто текущий доступный курс.
                elif response.status == 404 and shift_date:
                    logger.warning(f"Курс за {shift_date} не найден. Пробую получить текущий.")
                    return await get_eur_rate()
                
                else:
                    logger.error(f"Ошибка API NBP: Статус {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Сбой соединения с NBP API: {e}", exc_info=True)
        return None