import json
import logging
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from aiogram import Router, F, types

from config import GEMINI_API_KEY
from app.graph import app_graph
from app.state import AgentState

router = Router()
logger = logging.getLogger(__name__)

# Initialize GenAI client using our API key
client = genai.Client(api_key=GEMINI_API_KEY)

@router.message(F.voice)
async def handle_voice_shift(message: types.Message):
    status_msg = await message.answer("🎧 Слушаю и анализирую...")
    
    try:
        # 1. Download voice message directly into memory
        file_info = await message.bot.get_file(message.voice.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)
        audio_bytes = downloaded_file.read()
        audio_part = genai_types.Part.from_bytes(data=audio_bytes, mime_type='audio/ogg')
        
        # 2. Transcribe voice message using Gemini
        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt_text = f"""
        Ты — финансовый AI-ассистент. Твоя единственная задача — прослушать это голосовое сообщение от работника и перевести его в текст (сделать точную транскрипцию). 
        Верни только текст транскрипции без каких-либо комментариев и введений. 
        Сегодняшняя дата: {today_str}.
        """
        
        await status_msg.edit_text("🧠 Расшифровываю аудио...")
        response = await client.aio.models.generate_content(
            model='gemini-3.5-flash',
            contents=[prompt_text, audio_part],
            config=genai_types.GenerateContentConfig(temperature=0.1)
        )
        transcribed_text = response.text.strip()
        logger.info(f"Transcribed voice: '{transcribed_text}'")
        
        # 3. Setup initial state for LangGraph Agent
        initial_state = AgentState(
            user_id=message.from_user.id,
            raw_input=transcribed_text,
            parsed_data=None,
            validation_errors=[],
            is_confirmed=False
        )
        
        # 4. Setup thread config for MemorySaver persistence
        config = {"configurable": {"thread_id": str(message.from_user.id)}}
        
        # 5. Run the graph until the human_review interrupt point
        await status_msg.edit_text("🤖 Анализирую смену с помощью ИИ...")
        async for event in app_graph.astream(initial_state, config=config):
            pass
            
        # 6. Retrieve state after interrupt
        state_snapshot = await app_graph.aget_state(config)
        current_state = state_snapshot.values
        
        # 7. Check for validation errors
        errors = current_state.get("validation_errors", [])
        if errors:
            error_list = "\n".join(f"• {err}" for err in errors)
            await status_msg.delete()
            await message.answer(f"⚠️ **Ошибка валидации данных:**\n\n{error_list}", parse_mode="Markdown")
            return
            
        # 8. Send shift draft for user confirmation
        parsed_data = current_state.get("parsed_data") or {}
        draft_msg = (
            f"📝 **Черновик смены:**\n\n"
            f"📅 Дата: `{parsed_data.get('date') or 'Не указана'}`\n"
            f"📍 Локация: `{parsed_data.get('location') or 'Не указана'}`\n"
            f"🕒 Работа: `{parsed_data.get('work_hours') or 0.0} ч.`\n"
            f"🚗 Вождение: `{parsed_data.get('driving_hours') or 0.0} ч.`\n"
            f"📋 Статус: `{parsed_data.get('status') or 'Не указан'}`\n\n"
            f"**Сохранить эту смену в базу данных?**"
        )
        
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Да ✅", callback_data="confirm_shift_yes"),
                types.InlineKeyboardButton(text="Нет ❌", callback_data="confirm_shift_no")
            ]
        ])
        
        await status_msg.delete()
        await message.answer(draft_msg, reply_markup=kb, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Voice Error: {e}", exc_info=True)
        await status_msg.edit_text(f"⚠️ Ошибка расшифровки: {str(e)}")

@router.callback_query(F.data == "confirm_shift_yes")
async def handle_confirm_yes(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("💾 Сохраняю смену в базу данных...")
    
    try:
        config = {"configurable": {"thread_id": str(callback.from_user.id)}}
        
        # 1. Update state flag to True
        await app_graph.aupdate_state(config, {"is_confirmed": True})
        
        # 2. Resume graph to run human_review and database saver node
        async for event in app_graph.astream(None, config=config):
            pass
            
        await callback.message.edit_text("✅ **Смена успешно сохранена в базу данных!**", parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error saving shift via callback: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при сохранении смены в базу данных.")

@router.callback_query(F.data == "confirm_shift_no")
async def handle_confirm_no(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("❌ **Ввод смены отменен.**", parse_mode="Markdown")