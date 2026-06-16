from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_ID

router = Router()

@router.message(Command("feedback"))
async def cmd_feedback(message: types.Message):
    # Убираем саму команду из текста
    text = message.text.replace("/feedback", "").strip()
    
    if not text:
        await message.answer(
            "💡 Пожалуйста, напиши свой отзыв или предложение после команды.\n\n"
            "Пример: `/feedback Добавьте возможность выбирать цвет темы!`",
            parse_mode="Markdown"
        )
        return
        
    user_info = f"От: {message.from_user.full_name} (@{message.from_user.username}, ID: {message.from_user.id})"
    feedback_msg = f"📬 **НОВЫЙ ОТЗЫВ**\n{user_info}\n\n{text}"
    
    try:
        await message.bot.send_message(ADMIN_ID, feedback_msg, parse_mode="Markdown")
        await message.answer("✅ Спасибо! Твой отзыв успешно отправлен разработчику.")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при отправке отзыва. Пожалуйста, попробуй позже.")
