import json
import logging
from google import genai
from google.genai import types as genai_types
from aiogram import Router, F, types

from config import GEMINI_API_KEY
from database import update_user_setting

router = Router()
logger = logging.getLogger(__name__)

# Инициализация нового клиента
client = genai.Client(api_key=GEMINI_API_KEY)

@router.message(F.photo)
async def handle_car_photo(message: types.Message):
    status_msg = await message.answer("👁 Изучаю фото...")
    
    try:
        # 1. Скачиваем фото прямо в ОПЕРАТИВНУЮ ПАМЯТЬ (без сохранения на диск)
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)
        image_bytes = downloaded_file.read() # Читаем байты
        
        prompt = """
        Ты - умный парсер автомобильных данных. Посмотри на это фото.
        Определи марку и модель автомобиля. Если видно номерной знак, прочитай его.
        Верни ТОЛЬКО валидный JSON. Без форматирования markdown (без ```json).
        Формат: {"car": "Марка и Модель", "plate": "НОМЕР"}
        Если чего-то нет на фото, оставь значение пустым.
        """
        
        # 2. Асинхронно отправляем байты в Gemini
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                prompt,
                genai_types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg'
                )
            ]
        )
        
        # 3. Обрабатываем ответ
        raw_text = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(raw_text)
        
        car = data.get("car", "")
        plate = data.get("plate", "")
        
        if not car and not plate:
            await status_msg.edit_text("🤷‍♂️ Не смог распознать машину или номер. Попробуй другой ракурс!")
            return
            
        # 4. Формируем красивую строку
        final_car_string = f"{car} {plate}".strip()
            
        # 5. Сохраняем в базу (машина запишется, чтобы попасть в будущие выпадающие списки)
        await update_user_setting(message.from_user.id, "default_car", final_car_string)

        await status_msg.delete()
        
        # НОВЫЙ ЧИСТЫЙ ТЕКСТ БЕЗ КНОПОК
        final_text = (
            f"🚗 **Машина успешно распознана!**\n\n"
            f"**Авто:** {car}\n"
            f"**Номер:** {plate}\n\n"
            f"✅ Отличный аппарат! Введи его один раз при заполнении следующей смены, и он навсегда сохранится в твоем выпадающем списке гаража."
        )
        
        await message.answer(final_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Vision Error: {e}", exc_info=True)
        # Бот выведет конкретную ошибку прямо в чат
        await status_msg.edit_text(f"⚠️ Ошибка при анализе фото: {str(e)}")