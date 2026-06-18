from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_ID
from database import get_user_profile
from texts import TRANSLATIONS

router = Router()

@router.message(Command("feedback"))
async def cmd_feedback(message: types.Message):
    user_id = message.from_user.id
    profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])

    # Убираем саму команду из текста
    text = message.text.replace("/feedback", "").strip()
    
    if not text:
        await message.answer(
            t["feedback_help"],
            parse_mode="Markdown"
        )
        return
        
    user_info = f"От: {message.from_user.full_name} (@{message.from_user.username}, ID: {message.from_user.id})"
    feedback_msg = f"📬 **НОВЫЙ ОТЗЫВ**\n{user_info}\n\n{text}"
    
    try:
        await message.bot.send_message(ADMIN_ID, feedback_msg, parse_mode="Markdown")
        await message.answer(t["feedback_sent"])
    except Exception as e:
        await message.answer(t["feedback_error"])
