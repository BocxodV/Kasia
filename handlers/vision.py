import json
import logging
from google import genai
from google.genai import types as genai_types
from aiogram import Router, F, types

from config import GEMINI_API_KEY
# ДОБАВЛЕНО: импорт get_user_profile для языка
from database import update_user_setting, get_user_profile 
# ДОБАВЛЕНО: импорт функции клавиатуры
from keyboards import get_main_keyboard 
from handlers.webapp import build_app_url

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
        
        # 2. Асинхронно отправляем байты в Gemini (новый SDK)
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
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
            
        # 5. Сохраняем в базу
        await update_user_setting(message.from_user.id, "default_car", final_car_string)

        # ПОЛУЧАЕМ ЯЗЫК ПОЛЬЗОВАТЕЛЯ И НОВУЮ ССЫЛКУ
        profile = await get_user_profile(message.from_user.id)
        user_lang = profile.get("lang", "RUS")
        new_url = await build_app_url(message.from_user.id)
        
        await status_msg.delete()
        
        # ОТПРАВЛЯЕМ СООБЩЕНИЕ С ОБНОВЛЕННОЙ КНОПКОЙ
        await message.answer(
            f"🚗 **Машина успешно распознана!**\n\n"
            f"**Авто:** {car}\n"
            f"**Номер:** {plate}\n\n"
            f"✅ *Теперь {final_car_string} будет автоматически подставляться в твое Web-приложение!*",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(user_lang, new_url) # <--- ПЕРЕДАЕМ НОВУЮ ССЫЛКУ В КНОПКУ
        )
        
    except Exception as e:
        logger.error(f"Vision Error: {e}", exc_info=True)
        # Теперь бот выведет конкретную ошибку прямо в чат, чтобы мы сразу ее увидели!
        await status_msg.edit_text(f"⚠️ Ошибка при анализе фото: {str(e)}")