import json
import logging
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from aiogram import Router, F, types

from config import GEMINI_API_KEY
from database import get_user_profile, get_work_log_id, upsert_work_log
from nbp_service import get_eur_rate
from texts import TRANSLATIONS

router = Router()
logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

# --- 1. ОПИСАНИЕ НАВЫКА (TOOL) ДЛЯ ИИ ---
# Мы объясняем Gemini, что у неё есть "руки", и как ими пользоваться
eur_rate_tool = {
    "function_declarations": [
        {
            "name": "get_eur_rate",
            "description": "Получает актуальный курс Евро (EUR) к польскому злотому (PLN) из Нацбанка Польши (NBP). Обязательно используй этот инструмент, если в сообщении упоминается работа за границей (Германия, Берлин, Чехия, Европа и т.д.).",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "date_str": {
                        "type": "STRING",
                        "description": "Дата смены в формате YYYY-MM-DD"
                    }
                },
                "required": ["date_str"]
            }
        }
    ]
}

@router.message(F.voice)
async def handle_voice_shift(message: types.Message):
    user_id = message.from_user.id
    profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])
    status_msg = await message.answer(t["voice_analyzing"])
    
    try:
        # Берем аудио прямо в оперативку
        file_info = await message.bot.get_file(message.voice.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)
        audio_bytes = downloaded_file.read()
        audio_part = genai_types.Part.from_bytes(data=audio_bytes, mime_type='audio/ogg')
        
        # Промпт для ИИ
        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt_text = f"""
        Ты — финансовый AI-ассистент. Прослушай это голосовое сообщение от работника.
        Твоя задача — извлечь данные о смене и вернуть ТОЛЬКО валидный JSON (без форматирования ```json).
        Сегодня: {today_str}. Если дата не названа, используй сегодняшнюю.
        
        Важно: Если работник говорит о работе за границей (например, в Германии), ты ДОЛЖЕН сначала вызвать функцию get_eur_rate, чтобы получить курс валют, и только потом формировать финальный JSON.
        
        ПРАВИЛА ЗАПОЛНЕНИЯ:
        - "hours": Часы работы на объекте (число). Если не названы, ставь 0.
        - "drive": Часы за рулем (число). СТРОГО 0, если работник явно не назвал время в пути.
        - "location": Город или объект. Если не названо, оставь пустую строку "".
        - "is_trip": true, если есть слова "командировка", "диета". Иначе false.
        
        Пример JSON, который ты должен выдать:
        {{
            "date": "YYYY-MM-DD",
            "status": "Work",
            "hours": 12.0,
            "drive": 0.0,
            "location": "Дюссельдорф",
            "is_trip": true
        }}
        """
        
        # Настройка вызова с нашими инструментами
        config = genai_types.GenerateContentConfig(
            tools=[eur_rate_tool],
            temperature=0.1
        )
        
        # --- ШАГ 1: ПЕРВЫЙ ЗАПРОС К ИИ ---
        contents = [prompt_text, audio_part]
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=contents,
            config=config
        )
        
        applied_nbp_rate = None
        is_abroad = False
        
        # --- ШАГ 2: ПРОВЕРЯЕМ, ЗАХОТЕЛ ЛИ ИИ ВЫЗВАТЬ ФУНКЦИЮ ---
        if response.function_calls:
            for call in response.function_calls:
                if call.name == "get_eur_rate":
                    date_arg = call.args.get("date_str", today_str)
                    await status_msg.edit_text(t["voice_nbp_request"].format(date_arg=date_arg))
                    
                    # --- ШАГ 3: ВЫЗЫВАЕМ НАШ PYTHON-КОД ---
                    applied_nbp_rate = await get_eur_rate(date_arg)
                    is_abroad = True
                    
                    # --- ШАГ 4: ОТПРАВЛЯЕМ РЕЗУЛЬТАТ ОБРАТНО ИИ ---
                    # Формируем системное сообщение с ответом от Нацбанка
                    func_resp_part = genai_types.Part.from_function_response(
                        name="get_eur_rate",
                        response={"rate": applied_nbp_rate or 4.3} 
                    )
                    
                    # Собираем контекст общения: Промпт -> Ответ ИИ (вызов) -> Наш ответ (курс)
                    contents.append(response.candidates[0].content) 
                    contents.append(genai_types.Content(parts=[func_resp_part], role="user")) 
                    
                    await status_msg.edit_text(t["voice_finalizing"])
                    # Просим ИИ продолжить работу, имея на руках курс евро
                    response = await client.aio.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=contents,
                        config=config
                    )
        
        # 5. Парсим финальный JSON
        raw_text = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(raw_text)
        
        # 6. Готовим данные для базы
        user_id = message.from_user.id
        profile = await get_user_profile(user_id)
        
        shift_date = data.get("date", today_str)
        date_obj = datetime.strptime(shift_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d.%m.%Y")
        month_year = date_obj.strftime("%m.%Y")
        
        days_map = {
            'RUS': ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
            'UKR': ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"],
            'PL': ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
        }
        day_of_week = days_map.get(profile["lang"], days_map['PL'])[date_obj.weekday()]
        
        status = data.get("status", "Work")
        work_hours = float(data.get("hours") or 0)
        driving_hours = float(data.get("drive") or 0)
        location = data.get("location", "")
        is_trip_int = 1 if data.get("is_trip") else 0
        
        # 7. Включаем сложную математику расчета
        eff_rate = profile["extra_rate"]
        eff_drive = profile.get("rate_drive", 20.0)
        
        if is_abroad and applied_nbp_rate:
            if profile.get("rate_eur", 0) > 0:
                eff_rate = profile["rate_eur"] * applied_nbp_rate
            if profile.get("rate_drive_eur", 0) > 0:
                eff_drive = profile["rate_drive_eur"] * applied_nbp_rate
                
        weekday_num = date_obj.weekday()
        if weekday_num == 5: hours_50, hours_100, normal_hours = work_hours, 0, 0
        elif weekday_num == 6: hours_50, hours_100, normal_hours = 0, work_hours, 0
        else: 
            hours_50 = max(0, work_hours - 8)
            normal_hours = min(8, work_hours)
            hours_100 = 0
            
        gross = (normal_hours * profile["base_rate"]) + (hours_50 * profile["base_rate"] * 1.5) + (hours_100 * profile["base_rate"] * 2.0)
        net = (normal_hours * eff_rate) + (hours_50 * eff_rate * 1.5) + (hours_100 * eff_rate * 2.0) + (driving_hours * eff_drive)
        
        if is_trip_int: net += profile.get("diet_value", 45.0)
        bonuses = max(0, net - (gross * profile["tax_coeff"]))
        
        # 8. Сохраняем смену в БД
        record = await get_work_log_id(user_id, formatted_date)
        default_car = profile.get("default_car", "") 
        
        await upsert_work_log(
            user_id, formatted_date, month_year, day_of_week, 
            status, location, default_car, "", work_hours, driving_hours, 
            hours_50, hours_100, is_trip_int, bonuses, gross, net, record[0] if record else None
        )
        
        eur_text = t["voice_eur_text"].format(rate=applied_nbp_rate) if applied_nbp_rate else ""
        
        await status_msg.delete()
        await message.answer(
            t["voice_received"].format(
                date=formatted_date,
                day=day_of_week,
                loc=location,
                hours=work_hours,
                drive=driving_hours,
                net=net,
                eur=eur_text
            ),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Voice Error: {e}", exc_info=True)
        await status_msg.edit_text(t["voice_error"].format(err=str(e)))