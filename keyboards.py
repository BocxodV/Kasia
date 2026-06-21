# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from texts import TRANSLATIONS

def get_main_keyboard(lang, dynamic_url=None):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["RUS"])
    
    # Use the fresh dynamic URL if provided, otherwise fallback to the default entry point with the selected language
    if dynamic_url:
        url = dynamic_url
    else:
        url = f"https://e-ksiegowa.vercel.app/?lang={lang}"
    
    # Use safe lookup for localized button labels
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

# Dynamic keyboard generation function
def get_dynamic_reply_kb(items: list, row_width: int = 2) -> ReplyKeyboardMarkup:
    """
    Generates a dynamic reply keyboard from a list of strings (e.g., location history, recent vehicles).
    """
    builder = ReplyKeyboardBuilder()
    
    # Add keyboard buttons for each item
    for item in items:
        builder.add(KeyboardButton(text=str(item)))
        
    # Structure the grid using custom row width
    builder.adjust(row_width)
    
    # Return formatted keyboard markup
    # resize_keyboard=True reduces button sizes to fit the interface neatly
    # one_time_keyboard=True automatically hides the keyboard after selection
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)