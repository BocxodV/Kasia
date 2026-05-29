# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder # <--- НОВЫЙ ИМПОРТ ДЛЯ БИЛДЕРА
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

# --- НОВАЯ ФУНКЦИЯ ДЛЯ СПРИНТА 2 (ДИНАМИЧЕСКИЕ КНОПКИ) ---
def get_dynamic_reply_kb(items: list, row_width: int = 2) -> ReplyKeyboardMarkup:
    """
    Универсальный генератор динамической Reply-клавиатуры.
    Принимает список строк (история локаций или авто) и выстраивает их в кнопки.
    """
    builder = ReplyKeyboardBuilder()
    
    # Перебираем наш список (например, 5 последних городов)
    for item in items:
        builder.add(KeyboardButton(text=str(item)))
        
    # Упаковываем кнопки по рядам (например, по 2 в ряд)
    builder.adjust(row_width)
    
    # Возвращаем готовую клавиатуру:
    # resize_keyboard=True делает их маленькими и аккуратными
    # one_time_keyboard=True автоматически скрывает их после нажатия
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)