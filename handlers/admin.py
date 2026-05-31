import os
from aiogram import Router, types
from aiogram.filters import Command
from database import get_system_stats

router = Router()

# Получаем твой личный Telegram ID из переменных окружения Cloud Run
# Если переменной нет, ставим 0 (никто не получит доступ)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

@router.message(Command("admin", "boss", "stat"))
async def commander_panel(message: types.Message):
    # Секретная проверка: если ID не совпадает, бот просто игнорирует сообщение
    if message.from_user.id != ADMIN_ID:
        return 
        
    # Запрашиваем цифры из базы данных
    stats = await get_system_stats()
    
    text = (
        "👑 <b>ПАНЕЛЬ КОМАНДИРА</b> 👑\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Пользователей в БД: <b>{stats.get('users_count', 0)}</b>\n"
        f"📝 Сохранено смен: <b>{stats.get('shifts_count', 0)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<i>Все системы в облаке функционируют в штатном режиме.</i> 🚀"
    )
    
    await message.answer(text, parse_mode="HTML")