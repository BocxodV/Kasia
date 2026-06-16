import os
from aiogram import Router, types
from aiogram.filters import Command
from database import get_system_stats, get_all_users, get_user_profile
import json

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

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("⚠️ Использование: /broadcast <текст или JSON>\nНапример: `{\"RUS\": \"Привет\", \"PL\": \"Cześć\"}`", parse_mode="Markdown")
        return
        
    is_json = False
    data = {}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            is_json = True
    except:
        pass

    users = await get_all_users()
    count = 0
    await message.answer("⏳ Начинаю рассылку...")
    for u in users:
        user_id = u[0]
        try:
            profile = await get_user_profile(user_id)
            lang = profile.get("lang", "RUS")
            
            if is_json:
                msg_text = data.get(lang, data.get("RUS", text))
            else:
                msg_text = text
                
            if msg_text:
                await message.bot.send_message(user_id, msg_text)
                count += 1
        except Exception as e:
            pass
    await message.answer(f"✅ Рассылка завершена! Доставлено: {count} пользователям.")