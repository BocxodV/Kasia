# database.py
import aiosqlite
from config import DB_NAME

async def init_db():
    """Создает таблицы и обновляет структуру при запуске."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'PL',
                base_rate REAL DEFAULT 32.0,
                extra_rate REAL DEFAULT 4.0,
                tax_coeff REAL DEFAULT 0.71,
                rate_drive REAL DEFAULT 20.0,
                diet_value REAL DEFAULT 45.0,
                night_coeff REAL DEFAULT 0.2,
                last_location TEXT,
                last_country TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                log_date TEXT,
                month_year TEXT,
                day_of_week TEXT,
                status TEXT,
                car TEXT,
                route TEXT,
                work_hours REAL,
                driving_hours REAL,
                hours_50 REAL,
                hours_100 REAL,
                is_trip INTEGER,
                bonuses REAL,
                gross REAL,
                net REAL
            )
        ''')
        # Безопасное обновление старых таблиц
        for column in [
            "language TEXT DEFAULT 'PL'",
            "last_location TEXT", 
            "last_country TEXT", 
            "rate_eur REAL DEFAULT 0.0", 
            "rate_drive_eur REAL DEFAULT 0.0",
            "default_car TEXT DEFAULT ''",
            "reports_generated INTEGER DEFAULT 0",
            "is_premium INTEGER DEFAULT 0",
            "goal_name TEXT DEFAULT 'Финансовая цель'", 
            "goal_target REAL DEFAULT 8000.0",
            "shifts_added INTEGER DEFAULT 0",
            "current_savings REAL DEFAULT 0.0",
            "goal_deadline TEXT DEFAULT ''"
        ]:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {column}")
            except aiosqlite.OperationalError:
                pass
        await db.commit()

async def get_user_profile(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        # 1. Запрашиваем основные настройки и НОВЫЕ поля копилки
        query = '''
            SELECT 
                language, base_rate, extra_rate, tax_coeff, rate_drive, 
                rate_eur, rate_drive_eur, default_car, goal_name, 
                goal_target, current_savings, goal_deadline 
            FROM users WHERE user_id = ?
        '''
        async with db.execute(query, (user_id,)) as cursor:
            user = await cursor.fetchone()

        if not user:
            # Если юзера нет — создаем его и вызываем функцию рекурсивно
            await db.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            await db.commit()
            return await get_user_profile(user_id)
        
        # 2. Собираем всё в удобный словарь (Profile)
        return {
            "lang": user[0],
            "base_rate": user[1],
            "extra_rate": user[2], 
            "tax_coeff": user[3],
            "rate_drive": user[4],
            "rate_eur": user[5], 
            "rate_drive_eur": user[6],
            "default_car": user[7] or "",
            "goal_name": user[8] or "Финансовая цель",     
            "goal_target": user[9] or 8000.0,
            "current_savings": user[10] or 0.0,  # <--- НОВОЕ: Копилка
            "goal_deadline": user[11] or ""      # <--- НОВОЕ: Дедлайн
        }

async def update_user_setting(user_id, field, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
        await db.commit()

async def update_user_language(user_id, lang):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
        await db.commit()

async def update_last_location(user_id, location, country):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET last_location=?, last_country=? WHERE user_id=?", (location, country, user_id))
        await db.commit()

async def get_users_for_audit():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, language FROM users") as cursor:
            return await cursor.fetchall()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            return await cursor.fetchall()

async def get_work_logs_for_month(user_id, month_year):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT log_date, day_of_week, status, location, car, route, work_hours, driving_hours, hours_50, hours_100, is_trip, bonuses, gross, net
            FROM work_logs
            WHERE user_id = ? AND month_year = ?
            ORDER BY log_date ASC
        ''', (user_id, month_year)) as cursor:
            return await cursor.fetchall()

async def delete_work_log(user_id, log_date):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("DELETE FROM work_logs WHERE user_id=? AND log_date=?", (user_id, log_date))
        await db.commit()
        return cursor.rowcount

async def get_monthly_net_sum(user_id, month_year):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT SUM(net) FROM work_logs WHERE user_id=? AND month_year=?", (user_id, month_year)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result and result[0] else 0

async def get_last_geo(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT last_location, last_country FROM users WHERE user_id=?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_work_log_id(user_id, log_date):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT id FROM work_logs WHERE user_id = ? AND log_date = ?', (user_id, log_date)) as cursor:
            return await cursor.fetchone()

async def upsert_work_log(user_id, log_date, month_year, day_of_week, status, location, car, route, work_hours, driving_hours, hours_50, hours_100, is_trip_int, bonuses, gross, net, record_id=None):
    async with aiosqlite.connect(DB_NAME) as db:
        if record_id:
            await db.execute('''
                UPDATE work_logs
                SET day_of_week=?, status=?, location=?, car=?, route=?, work_hours=?, driving_hours=?, hours_50=?, hours_100=?, is_trip=?, bonuses=?, gross=?, net=?
                WHERE id=?
            ''', (day_of_week, status, location, car, route, work_hours, driving_hours, hours_50, hours_100, is_trip_int, bonuses, gross, net, record_id))
        else:
            await db.execute('''
                INSERT INTO work_logs (user_id, log_date, month_year, day_of_week, status, location, car, route, work_hours, driving_hours, hours_50, hours_100, is_trip, bonuses, gross, net)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, log_date, month_year, day_of_week, status, location, car, route, work_hours, driving_hours, hours_50, hours_100, is_trip_int, bonuses, gross, net))
        await db.commit()

async def get_available_months(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT DISTINCT month_year FROM work_logs WHERE user_id = ? ORDER BY month_year DESC', (user_id,)) as cursor:
            return await cursor.fetchall()

async def increment_report_count(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET reports_generated = reports_generated + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_user_subscription_status(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute("SELECT reports_generated, is_premium FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0] or 0, row[1] or 0
        except aiosqlite.OperationalError:
            pass
    return 0, 0

async def activate_user_premium(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (user_id,))
        await db.commit()

async def increment_shift_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        # Увеличиваем счетчик на 1
        await db.execute("UPDATE users SET shifts_added = shifts_added + 1 WHERE user_id = ?", (user_id,))
        await db.commit()
        # Получаем обновленное значение
        async with db.execute("SELECT shifts_added FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 1
        
async def add_user_savings(user_id: int, amount: float) -> float:
    """Добавляет сумму в копилку и возвращает новый баланс."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET current_savings = current_savings + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()
        async with db.execute("SELECT current_savings FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0.0
        
async def get_analytics_by_location(user_id, month_year):
    """Группирует смены по объектам за выбранный месяц и считает статистику."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT 
                location, 
                SUM(work_hours) as total_work, 
                SUM(driving_hours) as total_drive, 
                SUM(net) as total_net
            FROM work_logs
            WHERE user_id = ? AND month_year = ? AND location != '' AND status = 'Work'
            GROUP BY location
            ORDER BY total_net DESC
        ''', (user_id, month_year)) as cursor:
            return await cursor.fetchall()
        
async def get_user_unique_records(user_id: int):
    """
    Извлекает последние уникальные записи (авто и локации) для клавиатуры-подсказки.
    Сортировка по MAX(id) DESC гарантирует, что недавно использованные варианты будут первыми.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        # 1. Последние 5 уникальных авто
        async with db.execute('''
            SELECT car 
            FROM work_logs 
            WHERE user_id = ? AND car IS NOT NULL AND car != '' 
            GROUP BY car 
            ORDER BY MAX(id) DESC 
            LIMIT 5
        ''', (user_id,)) as cursor:
            cars = [row[0] for row in await cursor.fetchall()]

        # 2. Последние 10 уникальных локаций (городов/объектов)
        async with db.execute('''
            SELECT location 
            FROM work_logs 
            WHERE user_id = ? AND location IS NOT NULL AND location != '' 
            GROUP BY location 
            ORDER BY MAX(id) DESC 
            LIMIT 10
        ''', (user_id,)) as cursor:
            locations = [row[0] for row in await cursor.fetchall()]

    return {"cars": cars, "locations": locations}