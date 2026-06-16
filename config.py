# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Токены и ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL") 
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Константы расчетов
DIET_VALUE = 45.0
NIGHT_COEFF = 0.2