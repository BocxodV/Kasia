import json
import logging
import urllib.parse
import asyncio 
from datetime import datetime, timedelta
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonWebApp, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from texts import TRANSLATIONS
from keyboards import get_support_keyboard 
from nbp_service import get_eur_rate
from database import (
    get_user_profile, get_work_log_id, 
    upsert_work_log, update_user_setting,
    get_monthly_net_sum, increment_report_count, get_user_subscription_status,
    activate_user_premium, update_user_language,
    increment_shift_count, delete_work_log, get_work_logs_for_month,
    add_user_savings, get_analytics_by_location
)
from handlers.reports import generate_excel_report
from map_service import calculate_driving_hours

router = Router()
logger = logging.getLogger(__name__)

WEB_APP_URL = "https://e-ksiegowa.vercel.app/"

# --- СОСТОЯНИЯ ДЛЯ РУЧНОГО ВВОДА СУММЫ В КОПИЛКУ ---
class SavingsState(StatesGroup):
    waiting_for_amount = State()

# --- ЛОГИКА ПРОГНОЗИСТА ---
async def calculate_forecast(user_id, profile=None):
    if not profile: 
        profile = await get_user_profile(user_id)
    goal_target = profile.get("goal_target", 8000.0)
    current_savings = profile.get("current_savings", 0.0) 
    goal_deadline_str = profile.get("goal_deadline", "")
    
    remaining_money = max(0, goal_target - current_savings)
    
    if current_savings >= goal_target:
        return f"🎉 **ЦЕЛЬ ДОСТИГНУТА!** Ты накопил {current_savings:.2f} zł!"
        
    if not goal_deadline_str:
        return f"Укажи дату цели в настройках, чтобы я рассчитала прогноз! Осталось собрать: {remaining_money:.2f} zł."
        
    try:
        deadline_date = datetime.strptime(goal_deadline_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_left = (deadline_date - today).days
        
        if days_left <= 0:
            return f"⏳ Дедлайн прошел. Осталось собрать: {remaining_money:.2f} zł. Давай обновим дату в настройках!"
            
        weeks_left = max(1, days_left / 7)
        required_per_week = remaining_money / weeks_left
        
        return (f"📈 **Прогноз:**\n"
                f"Осталось собрать: **{remaining_money:.2f} zł**\n"
                f"До дедлайна: **{days_left} дней**\n\n"
                f"💡 Чтобы успеть вовремя, нужно откладывать примерно **{required_per_week:.0f} zł в неделю**.")
    except Exception:
        return f"Осталось собрать: {remaining_money:.2f} zł."

# --- ГЕНЕРАЦИЯ ССЫЛКИ С ДАННЫМИ ---
async def build_app_url(user_id, profile=None):
    if not profile:
        profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    current_month = datetime.now().strftime("%m.%Y")
    current_net = await get_monthly_net_sum(user_id, current_month)
    
    base, extra, eur = profile.get("base_rate", 0), profile.get("extra_rate", 0), profile.get("rate_eur", 0)
    drive, drive_eur = profile.get("rate_drive", 0), profile.get("rate_drive_eur", 0)
    default_car = ""
    
    raw_goal = profile.get("goal_name", "Моя цель")
    if len(raw_goal) > 12:
        raw_goal = raw_goal[:11] + "…"
    goal_name = urllib.parse.quote(raw_goal)
    
    goal_target = profile.get("goal_target", 8000.0)
    
    # НОВОЕ: Данные копилки
    current_savings = profile.get("current_savings", 0.0)
    goal_deadline = profile.get("goal_deadline", "")
    
    # Версия v=11
    return f"{WEB_APP_URL}?v=11&base={base:g}&extra={extra:g}&eur={eur:g}&drive={drive:g}&drive_eur={drive_eur:g}&car={default_car}&g_name={goal_name}&g_target={goal_target:g}&c_net={current_net:.1f}&c_sav={current_savings:g}&g_dead={goal_deadline}&lang={user_lang}"


@router.message(Command("app"))
async def summon_web_app(message: types.Message):
    user_id = message.from_user.id
    profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])
    
    dynamic_url = await build_app_url(user_id, profile)
    
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["menu_btn"], web_app=WebAppInfo(url=dynamic_url))]],
        resize_keyboard=True
    )
    
    await message.bot.set_chat_menu_button(
        chat_id=user_id,
        menu_button=MenuButtonWebApp(text=t["menu_btn"], web_app=WebAppInfo(url=dynamic_url))
    )
    await message.answer(t["menu_msg"], reply_markup=markup)


@router.message(F.web_app_data)
async def web_app_handler(message: types.Message):
    raw_data = message.web_app_data.data
    try:
        data = json.loads(raw_data)
        user_id = message.from_user.id
        profile = await get_user_profile(user_id)
        user_lang = profile.get("lang", "RUS")
        t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])

        if data.get("action") == "add_shift":
            status_msg = await message.answer(t["saving"])
            start_date = datetime.strptime(data.get("date"), "%Y-%m-%d")
            end_date_str = data.get("end_date")
            status = data.get("status", "Work")
            location = data.get("object") or data.get("location") or ""
            
            dates_to_process = [start_date]
            if status in ["L4", "Urlop"] and end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                if end_date > start_date:
                    curr = start_date
                    while curr < end_date:
                        curr += timedelta(days=1)
                        dates_to_process.append(curr)
            
            work_hours = float(data.get("hours") or 0)
            driving_hours = float(data.get("drive") or 0)
            route = data.get("route") or ""
            log_text = "Логістика" if user_lang == "UKR" else "Logistyka" if user_lang == "PL" else "Логистика"

            if route and "-" in route and driving_hours <= 0:
                calc_task = asyncio.create_task(calculate_driving_hours(route))
                frames = [f"🏢 ⠤⠤⠤⠤⠤⠤⠤ 🚗", f"🏢 ⠤⠤⠤⠤⠤ 🚗 ⠤⠤", f"🏢 ⠤⠤⠤ 🚗 ⠤⠤⠤⠤", f"🏢 ⠤ 🚗 ⠤⠤⠤⠤⠤⠤", f"🏢 🚗 ⠤⠤⠤⠤⠤⠤⠤"]
                for frame in frames:
                    try:
                        await status_msg.edit_text(f"🛣 {log_text}: {route}\n{frame}")
                        await asyncio.sleep(0.3)
                    except: pass
                driving_hours = await calc_task

            total_net, total_gross, total_loss, total_cash_diff = 0, 0, 0, 0
            ai_advice = ""
            applied_nbp_rate = await get_eur_rate(data.get("date")) if data.get("is_abroad") else None

            is_trip_int = 1 if data.get("is_trip") else 0
            eff_rate = profile.get("extra_rate", 0)
            eff_drive = profile.get("rate_drive", 20.0)
            
            if data.get("is_abroad") and applied_nbp_rate:
                if profile.get("rate_eur", 0) > 0:
                    eff_rate = profile["rate_eur"] * applied_nbp_rate
                if profile.get("rate_drive_eur", 0) > 0:
                    eff_drive = profile["rate_drive_eur"] * applied_nbp_rate

            for d in dates_to_process:
                f_date, month_y = d.strftime("%d.%m.%Y"), d.strftime("%m.%Y")
                
                days_map = {
                    'RUS': ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
                    'UKR': ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"],
                    'PL': ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
                }
                day_w = days_map.get(user_lang, days_map['PL'])[d.weekday()]

                cash_part, bonuses, hours_50, hours_100 = 0, 0, 0, 0

                if status == "L4":
                    gross = 8 * profile.get("base_rate", 32.0) * 0.8
                    net = gross * profile.get("tax_coeff", 0.71)
                    total_loss += (8 * profile.get("base_rate", 32.0) * profile.get("tax_coeff", 0.71)) - net
                    is_trip_for_db = 0
                elif status == "Urlop":
                    gross = 8 * profile.get("base_rate", 32.0)
                    net = gross * profile.get("tax_coeff", 0.71)
                    is_trip_for_db = 0
                else:
                    is_trip_for_db = is_trip_int
                    weekday_num = d.weekday()
                    if weekday_num == 5: hours_50, hours_100, normal_hours = work_hours, 0, 0 
                    elif weekday_num == 6: hours_50, hours_100, normal_hours = 0, work_hours, 0 
                    else: 
                        hours_50 = max(0, work_hours - 8)
                        normal_hours = min(8, work_hours)
                        hours_100 = 0
                        
                    base_rate = profile.get("base_rate", 32.0)
                    tax_coeff = profile.get("tax_coeff", 0.71)
                    
                    gross = (normal_hours * base_rate) + (hours_50 * base_rate * 1.5) + (hours_100 * base_rate * 2.0)
                    official_net = gross * tax_coeff
                    
                    real_total = (normal_hours * eff_rate) + (hours_50 * eff_rate * 1.5) + (hours_100 * eff_rate * 2.0) + (driving_hours * eff_drive)
                    
                    if is_trip_for_db: 
                        real_total += profile.get("diet_value", 45.0)
                        
                    net = real_total
                    bonuses = max(0, net - official_net)
                    cash_part = bonuses 
                
                await upsert_work_log(
                    user_id, f_date, month_y, day_w, status, 
                    location, data.get("car",""), route, 
                    work_hours, driving_hours, hours_50, hours_100, 
                    is_trip_for_db, bonuses, gross, net
                )
                
                total_net += net
                total_gross += gross
                total_cash_diff += cash_part

            await status_msg.delete()
            
            status_labels = {
                "Work": {"PL": "💼 Praca", "UKR": "💼 Робота", "RUS": "💼 Работа"},
                "L4": {"PL": "💊 Zwolnienie (L4)", "UKR": "💊 Лікарняний (L4)", "RUS": "💊 Больничный (L4)"},
                "Urlop": {"PL": "🌴 Urlop", "UKR": "🌴 Відпустка", "RUS": "🌴 Отпуск"}
            }
            status_icon = status_labels.get(status, status_labels["Work"]).get(user_lang, status_labels["Work"]["RUS"])
            
            if status == "Work" and (work_hours + driving_hours) >= 12:
                ai_advice = f"\n\n🤖 {t['overwork_msg'].format(hours=(work_hours + driving_hours))}"
            
            dyn_url = await build_app_url(user_id) 
            total_shifts = await increment_shift_count(user_id)
            
            coffee_msg = ""
            if total_shifts > 0 and total_shifts % 10 == 0:
                coffee_msg = f"\n\n☕️ <i>P.S. Я сохранила для тебя уже {total_shifts} смен! <a href='https://www.buymeacoffee.com/bocxodv'>Угостить кофе</a></i>"
            
            day_idx = start_date.weekday() 
            day_name = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][day_idx]
            if user_lang == "PL": day_name = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"][day_idx]
            elif user_lang == "UKR": day_name = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"][day_idx]

            final_text = (
                f"✅ <b>Запись сохранена:</b> {start_date.strftime('%d.%m.%Y')} ({day_name})\n"
                f"Статус: {status_icon}\n"
                f"📍 Объект: {location}\n\n"
                f"💰 <b>НА РУКИ: {total_net:.2f} zł</b>\n"
                f"➖ ➖ ➖ ➖ ➖\n"
                f"🕒 Работа: {work_hours} ч. | 🚗 За рулем: {driving_hours} ч.\n"
                f"➖ ➖ ➖ ➖ ➖\n"
                f"📊 <b>Детализация:</b>\n"
                f"• Брутто: {total_gross:.2f} zł\n"
                f"• Конверт (наличка): {total_cash_diff:.2f} zł\n"
                f"{ai_advice}"
                f"{coffee_msg}" 
            )
            
            markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t["menu_btn"], web_app=WebAppInfo(url=dyn_url))]], resize_keyboard=True)
            await message.bot.set_chat_menu_button(chat_id=user_id, menu_button=MenuButtonWebApp(text=t["menu_btn"], web_app=WebAppInfo(url=dyn_url)))
            await message.answer(final_text, reply_markup=markup, parse_mode="HTML")

        elif data.get("action") == "update_settings":
            for field in ["base_rate", "extra_rate", "rate_eur", "rate_drive", "rate_drive_eur", "goal_target"]:
                val = data.get(field)
                if val is not None and str(val).strip() != "":
                    try:
                        clean_val = str(val).replace(",", ".").strip()
                        if clean_val: await update_user_setting(user_id, field, float(clean_val))
                    except ValueError: pass
            if "goal_name" in data: await update_user_setting(user_id, "goal_name", str(data["goal_name"]))
            # СОХРАНЯЕМ ДЕДЛАЙН
            if "goal_deadline" in data: await update_user_setting(user_id, "goal_deadline", str(data["goal_deadline"]))
            if data.get("lang"): await update_user_language(user_id, str(data["lang"]))
            
            dyn_url = await build_app_url(user_id)
            markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t["menu_btn"], web_app=WebAppInfo(url=dyn_url))]], resize_keyboard=True)
            await message.bot.set_chat_menu_button(chat_id=user_id, menu_button=MenuButtonWebApp(text=t["menu_btn"], web_app=WebAppInfo(url=dyn_url)))
            await message.answer(t["set_ok"], parse_mode="HTML", reply_markup=markup)

        elif data.get("action") == "get_report":
            target_month = data.get("month") or datetime.now().strftime("%m.%Y")
            status_msg = await message.answer(t["report_wait"].format(month=target_month))
            await generate_excel_report(callback=None, target_user_id=user_id, target_month=target_month, bot=message.bot)
            await status_msg.delete()
            await increment_report_count(user_id)
            reports_count, is_premium = await get_user_subscription_status(user_id)
            if not is_premium and reports_count > 0 and reports_count % 5 == 0:
                await message.answer(t["freemium"].format(count=reports_count), parse_mode="Markdown", reply_markup=get_support_keyboard(user_lang))

        # --- ОБНОВЛЕННЫЙ АУДИТ С ПРЕДЛОЖЕНИЕМ КОПИЛКИ ---
        elif data.get("action") == "audit":
            target_month = data.get("month")
            card_amount = float(data.get("card", 0))
            total_net = await get_monthly_net_sum(user_id, target_month)
            if total_net > 0:
                envelope = total_net - card_amount
                ten_percent = round(total_net * 0.10, 2)
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"💰 Закинуть 10% ({ten_percent} zł)", callback_data=f"add_savings_{ten_percent}")],
                    [InlineKeyboardButton(text="✍️ Ввести свою сумму", callback_data="custom_savings")]
                ])
                
                msg_text = (t["audit_ok"].format(month=target_month, card=card_amount, total=f"{total_net:.2f}", env=f"{max(0, envelope):.2f}") +
                            f"\n\n💡 *Совет от Каси:*\nОтличный месяц! Рекомендую отложить 10% от заработанного ({ten_percent} zł) в копилку на твою цель.")
                
                await message.answer(msg_text, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await message.answer(t["audit_err"].format(month=target_month))

        elif data.get("action") == "analytics":
            target_month = data.get("month")
            analytics_data = await get_analytics_by_location(user_id, target_month)
            
            if not analytics_data:
                await message.answer(t["hist_err"].format(month=target_month))
                return
            
            # --- ПОДГОТОВКА ДАННЫХ ДЛЯ ГРАФИКА ---
            labels = [row[0] for row in analytics_data] # Названия объектов
            values = [row[3] for row in analytics_data] # Суммы Netto
            
            # Формируем конфиг для QuickChart (JSON)
            chart_config = {
                "type": "pie",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "data": values,
                        "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
                    }]
                },
                "options": {
                    "title": { "display": True, "text": f"Доходы по объектам ({target_month})", "fontSize": 20 },
                    "plugins": { "datalabels": { "color": "white", "font": { "weight": "bold" } } }
                }
            }
            
            # Кодируем ссылку
            encoded_config = urllib.parse.quote(json.dumps(chart_config))
            chart_url = f"https://quickchart.io/chart?c={encoded_config}&width=500&height=300&bkg=white"

            # --- ФОРМИРУЕМ ТЕКСТОВЫЙ ТОП ---
            msg_text = f"📊 **Аналитика по объектам за {target_month}**\n\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, row in enumerate(analytics_data):
                loc, t_work, t_drive, t_net = row[0], row[1], row[2], row[3]
                medal = medals[i] if i < 3 else "🔸"
                msg_text += f"{medal} **{loc}**: {t_net:.2f} zł\n"

            # Отправляем фото с графиком и описанием
            await message.answer_photo(
                photo=chart_url,
                caption=msg_text,
                parse_mode="Markdown"
            )

        elif data.get("action") == "history":
            target_month = data.get("month")
            logs = await get_work_logs_for_month(user_id, target_month)
            if not logs:
                await message.answer(t["hist_err"].format(month=target_month))
                return
            text = t["hist_ok"].format(month=target_month)
            keyboard = []
            for log in logs:
                date_str, status, net = log[0], log[2], log[13]     
                icon = "💼" if status == "Work" else "💊" if status == "L4" else "🌴"
                btn_text = f"❌ {date_str} ({icon} {net:.2f} zł)"
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"del_log_{date_str}")])
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"WebApp Error: {e}")
        t = TRANSLATIONS.get("RUS", TRANSLATIONS["RUS"])
        await message.answer(t["err"])

# --- ОБРАБОТЧИКИ КНОПОК КОПИЛКИ ---
@router.callback_query(F.data.startswith("add_savings_"))
async def add_savings_fast(callback: types.CallbackQuery):
    amount = float(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    
    await add_user_savings(user_id, amount)
    profile = await get_user_profile(user_id)
    forecast = await calculate_forecast(user_id, profile)
    
    await callback.message.edit_text(
        f"✅ **Отложено {amount} zł в копилку!**\n\n{forecast}", 
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "custom_savings")
async def ask_custom_savings(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("✍️ Напиши сумму, которую хочешь отложить (в злотых):")
    await state.set_state(SavingsState.waiting_for_amount)
    await callback.answer()

@router.message(SavingsState.waiting_for_amount)
async def process_custom_savings(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", ".").strip())
        user_id = message.from_user.id
        
        await add_user_savings(user_id, amount)
        profile = await get_user_profile(user_id)
        forecast = await calculate_forecast(user_id, profile)
        
        await message.answer(f"✅ **Отложено {amount} zł в копилку!**\n\n{forecast}", parse_mode="Markdown")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введи только число (например, 150 или 150.5):")

@router.callback_query(F.data.startswith("del_log_"))
async def delete_log_handler(callback: types.CallbackQuery):
    date_to_delete = callback.data.replace("del_log_", "")
    user_id = callback.from_user.id 
    profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])
    deleted_count = await delete_work_log(user_id, date_to_delete)
    if deleted_count > 0:
        await callback.answer(t["del_ok_alert"].format(date=date_to_delete), show_alert=True)
        await callback.message.answer(t["del_ok_msg"].format(date=date_to_delete), parse_mode="Markdown")
        await callback.message.delete() 
    else:
        await callback.answer(t["del_err"], show_alert=True)

@router.callback_query(F.data == "activate_premium")
async def process_premium_activation(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await activate_user_premium(user_id)
    profile = await get_user_profile(user_id)
    user_lang = profile.get("lang", "RUS")
    t = TRANSLATIONS.get(user_lang, TRANSLATIONS["RUS"])
    await callback.answer(t["pro_alert"], show_alert=True)
    await callback.message.edit_text(t["pro_msg"], parse_mode="Markdown")