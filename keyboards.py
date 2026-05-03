# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from texts import TRANSLATIONS

def get_main_keyboard(lang, dynamic_url=None):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["RUS"])
    
    # Если передана ссылка со свежими данными - используем её.
    # Если нет (например, при первом запуске /start), передаем хотя бы язык.
    if dynamic_url:
        url = dynamic_url
    else:
        url = f"https://e-ksiegowa.vercel.app/?lang={lang}"
    
    # Используем .get() для безопасного перевода кнопки
    btn_text = t.get("btn_panel", "📱 Открыть панель")
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=btn_text, web_app=WebAppInfo(url=url))],
            [KeyboardButton(text=t["btn_help"]), KeyboardButton(text=t["btn_feedback"])]
        ],
        resize_keyboard=True
    )

def get_support_keyboard(lang):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["RUS"])
    buttons = [
        [InlineKeyboardButton(text=t["btn_coffee_10"], url="https://revolut.me/bocxodv")],
        [InlineKeyboardButton(text=t["btn_lunch_30"], url="https://revolut.me/bocxodv")],
        [InlineKeyboardButton(text=t["btn_pro"], callback_data="activate_premium")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)