import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, MenuButtonWebApp, WebAppInfo, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
logging.basicConfig(
    level=logging.INFO,
    filename="bot_errors.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

from texts import TRANSLATIONS
from keyboards import get_main_keyboard

# Импорт асинхронных функций БД
from database import (
    init_db, get_user_profile, update_user_language, 
    update_last_location, get_users_for_audit, get_all_users
)

from handlers import reports, webapp, vision, voice
from handlers.reports import generate_excel_report
from handlers.webapp import build_app_url # Подтягиваем наш генератор
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрация всех модулей
dp.include_router(reports.router)
dp.include_router(vision.router) # Модуль компьютерного зрения
dp.include_router(voice.router) # Модуль обработки голосовых сообщений
dp.include_router(webapp.router) # Модуль Web App

@dp.message(CommandStart())
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    
    profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])
    
    dyn_url = await build_app_url(user_id, profile)
    
    # Оставляем кнопку в меню (для красоты)
    await message.bot.set_chat_menu_button(
        chat_id=user_id,
        menu_button=MenuButtonWebApp(text=t["menu_btn"], web_app=WebAppInfo(url=dyn_url))
    )
    
    # ВОЗВРАЩАЕМ КНОПКУ В ЧАТ (Маленькую и аккуратную!)
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["menu_btn"], web_app=WebAppInfo(url=dyn_url))]],
        resize_keyboard=True # <--- ЭТОТ ПАРАМЕТР СПАСАЕТ ОТ "ОГРОМНЫХ ПУСТЫХ" КНОПОК
    )
    
    photo_file = FSInputFile("/home/BocxodV/e_ksiegowa_bot/welcome.jpg")
    await message.answer_photo(
        photo=photo_file,
        caption=t["welcome_text"],
        parse_mode="Markdown",
        reply_markup=markup
    )

async def main():
    await init_db() 
    
    scheduler = AsyncIOScheduler(timezone="Europe/Warsaw")
    # Твои задачи планировщика остаются активными
    scheduler.start()
    
    logger.info("Бот запущен в штатном режиме.")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())