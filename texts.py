# texts.py

TRANSLATIONS = {
    "RUS": {
        "saving": "⏳ Сохраняю...",
        "report_wait": "⏳ Формирую отчет за {month}...",
        "total_month": "Итого за месяц:",
        "freemium": "🤝 **Напарник, минутку внимания!**\n\nЭто твой **{count}-й** сгенерированный отчет. Я экономлю тебе кучу времени на сверках с офисом и расчетах налогов.\n\nЧтобы бот работал стабильно и развивался дальше, ты можешь поддержать проект символической суммой «на кофе ☕».",
        "audit_ok": "📊 **Аудит за {month}**\n\n💳 Пришло на карту: **{card} zł**\n💰 Твой общий заработок: **{total} zł**\n〰️〰️〰️〰️〰️〰️〰️\n✉️ **В КОНВЕРТЕ: {env} zł**",
        "audit_err": "⚠️ Нет записей о рабочих днях за {month}.",
        "hist_err": "📭 За {month} нет сохраненных смен.",
        "hist_ok": "📜 **История смен за {month}**\nНажми ❌ для удаления ошибочной записи:\n\n",
        "set_ok": "⚙️ <b>Настройки успешно сохранены!</b>",
        "err": "⚠️ Ошибка обработки данных.",
        "del_ok_alert": "✅ Смена за {date} удалена!",
        "del_ok_msg": "🗑 Запись за **{date}** была успешно удалена из базы.",
        "del_err": "⚠️ Запись не найдена или уже удалена.",
        "pro_alert": "⭐ PRO-подписка успешно активирована!",
        "pro_msg": "🎉 **Добро пожаловать в PRO-клуб!**\n\nТвой статус успешно обновлен. Теперь все твои Excel-отчеты формируются в профессиональном виде.\nСпасибо, что инвестируешь в свое время и поддерживаешь проект!",
        
        "excel_headers": ["Дата", "День", "Статус","Объект", "Авто", "Маршрут", "Всего ч.", "Руль", "50%", "100%", "Командировка", "Бонусы", "Брутто", "NETTO"],
        "excel_caption": "📊 Твоя зарплата за {month}\n🕒 Отработано: **{hours} ч.**\n💰 Всего заработано : **{net} zł**",
        "empty_db": "🤷‍♂️ В базе пока нет сохраненных отчетов.",
        
        "btn_panel": "📱 Открыть панель",
        "btn_help": "🚀 Как это работает?",
        "btn_feedback": "💬 Отзывы и идеи",
        "btn_coffee_10": "☕️ Угостить напарника кофе (10 zł)",
        "btn_lunch_30": "🍕 Обед для коллеги (30 zł)",
        "btn_pro": "⭐ Активировать PRO-подписку",
        "opt_work": "💼 Работа",
        "opt_l4": "💊 Больничный (L4)",
        "opt_urlop": "🌴 Отпуск",
        "help_text": (
            "🤖 **Как я работаю? Все просто!**\n\n"
            "📱 **ИНТЕРАКТИВНАЯ ПАНЕЛЬ**\n"
            "Нажми кнопку «Открыть панель» — это твой главный инструмент. Там три вкладки:\n"
            "1️⃣ **Смена** — для записи отработанных часов, больничных и отпусков.\n"
            "2️⃣ **Отчеты** — для выгрузки Excel, аудита зарплаты и удаления ошибочных смен.\n"
            "3️⃣ **Настройки** — для указания твоих ставок и финансовой цели.\n\n"
            "🌍 **УМНАЯ ЛОГИСТИКА И ВАЛЮТА**\n"
            "Если ты впишешь маршрут, но не укажешь часы вождения, я посчитаю их сам! А если отметишь галочку «Заграница», я переведу заработок из Евро в Злотые по актуальному курсу NBP."
        ),
        "feedback_msg": "💡 Есть идея, как улучшить приложение? Или нашел баг?\n\nНапиши напрямую разработчику:\n👉 [Написать программисту](https://t.me/+1tajf8L_zck5NTQy)",
        "overwork_msg": "{hours} ч. за смену — это мощно! Но не забывай про отдых и личные дела. Здоровье важнее переработок!",        
        "l4_loss_msg": "**ИИ-Аналитика:** Здоровье важнее денег! Но для справки: больничный ({count} дн.) стоил тебе потери около **{loss} zł** чистыми.",
        
        # --- НОВЫЕ КЛЮЧИ ---
        "menu_btn": "📱 Панель",
        "menu_msg": "⚡️ Интерактивная панель теперь всегда доступна по кнопке меню слева от поля ввода!",
        "welcome_text": "Привет! Я твоя ИИ-бухгалтерша 👩‍💼\n\nЯ помогу тебе вести учет рабочих смен, логистики и точно рассчитаю твою зарплату (брутто, нетто и даже «в конверте»).\n\nЧтобы начать, нажми кнопку **«📱 Панель»** в меню слева внизу! 👇"
    },
    "UKR": {
        "saving": "⏳ Зберігаю...",
        "report_wait": "⏳ Формую звіт за {month}...",
        "total_month": "Всього за місяць:",
        "freemium": "🤝 **Напарнику, хвилинку уваги!**\n\nЦе твій **{count}-й** згенерований звіт. Я економлю тобі купу часу на звірках з офісом та розрахунках податків.\n\nЩоб бот працював стабільно і розвивався далі, ти можеш підтримати проєкт символічною сумою «на каву ☕».",
        "audit_ok": "📊 **Аудит за {month}**\n\n💳 Прийшло на карту: **{card} zł**\n💰 Твій загальний заробіток: **{total} zł**\n〰️〰️〰️〰️〰️〰️〰️\n✉️ **У КОНВЕРТІ: {env} zł**",
        "audit_err": "⚠️ Немає записів про робочі дні за {month}.",
        "hist_err": "📭 За {month} немає збережених змін.",
        "hist_ok": "📜 **Історія змін за {month}**\nНатисни ❌ для видалення помилкового запису:\n\n",
        "set_ok": "⚙️ <b>Налаштування успішно збережено!</b>",
        "err": "⚠️ Помилка обробки даних.",
        "del_ok_alert": "✅ Зміну за {date} видалено!",
        "del_ok_msg": "🗑 Запис за **{date}** був успішно видалений з бази.",
        "del_err": "⚠️ Запис не знайдено або вже видалено.",
        "pro_alert": "⭐ PRO-підписку успішно активовано!",
        "pro_msg": "🎉 **Ласкаво просимо до PRO-клубу!**\n\nТвій статус успішно оновлено. Тепер усі твої Excel-звіти формуються у професійному вигляді.\nДякую, що інвестуєш у свій час і підтримуєш проєкт!",
        
        "excel_headers": ["Дата", "День", "Статус","Об'єкт", "Авто", "Маршрут", "Всього год.", "Кермо", "50%", "100%", "Відрядження", "Бонуси", "Брутто", "NETTO"],
        "excel_caption": "📊 Твоя зарплата за {month}\n🕒 Відпрацьовано: **{hours} год.**\n💰 Всього зароблено : **{net} zł**",
        "empty_db": "🤷‍♂️ В цьому місяці у тебе ще немає збережених звітів.",
        
        "btn_panel": "📱 Відкрити панель",
        "btn_help": "🚀 Як це працює?",
        "btn_feedback": "💬 Відгуки та ідеї",
        "btn_coffee_10": "☕️ Пригостити напарника кавою (10 zł)",
        "btn_lunch_30": "🍕 Обід для колеги (30 zł)",
        "btn_pro": "⭐ Активувати PRO-підписку",
        "opt_work": "💼 Робота",
        "opt_l4": "💊 Лікарняний (L4)",
        "opt_urlop": "🌴 Відпустка",
        "help_text": (
            "🤖 **Як я працюю? Це дуже просто!**\n\n"
            "📱 **ІНТЕРАКТИВНА ПАНЕЛЬ**\n"
            "Тисни кнопку «Відкрити панель» — це твій головний інструмент. Там три вкладки:\n"
            "1️⃣ **Зміна** — для запису відпрацьованих годин, лікарняних та відпусток.\n"
            "2️⃣ **Звіти** — для вивантаження Excel, аудиту зарплати та видалення помилкових змін.\n"
            "3️⃣ **Налаштування** — для вказівки твоїх ставок та фінансової цілі.\n\n"
            "🌍 **РОЗУМНА ЛОГІСТИКА ТА ВАЛЮТА**\n"
            "Якщо ти впишеш маршрут, але не вкажеш години за кермом, я порахую їх сам! А якщо відмітиш «Закордон», я переведу заробіток з Євро в Злоті за актуальним курсом NBP."
        ),
        "feedback_msg": "💡 Є ідея, як покращити додаток? Або знайшов помилку?\n\nНапиши безпосередньо розробнику:\n👉 [Написати програмісту](https://t.me/+1tajf8L_zck5NTQy)",
        "overwork_msg": "{hours} год за зміну — це потужно! Але не забувай про відпочинок та особисті справи. Здоров'я важливіше!",        
        "l4_loss_msg": "**Штучний Інтелект:** Здоров'я дорожче за гроші! Але для довідки: цей лікарняний ({count} дн.) коштував тобі втрати близько **{loss} zł** чистими.",
        
        # --- НОВЫЕ КЛЮЧИ ---
        "menu_btn": "📱 Панель",
        "menu_msg": "⚡️ Інтерактивна панель тепер завжди доступна за кнопкою меню зліва від поля введення!",
        "welcome_text": "Привіт! Я твоя ШІ-бухгалтерка 👩‍💼\n\nЯ допоможу тобі вести облік робочих змін, логістики та точно розрахую твою зарплату (брутто, нетто і навіть «у конверті»).\n\nЩоб почати, натисни кнопку **«📱 Панель»** у меню зліва внизу! 👇"
    },
    "PL": {
        "saving": "⏳ Zapisuję...",
        "report_wait": "⏳ Generuję raport za {month}...",
        "total_month": "Razem za miesiąc:",
        "freemium": "🤝 **Kolego, chwila uwagi!**\n\nTo Twój **{count}.** wygenerowany raport. Oszczędzam Ci mnóstwo czasu na rozliczeniach z biurem i podatkach.\n\nAby bot działał stabilnie i się rozwijał, możesz wesprzeć projekt symboliczną kwotą «na kawę ☕».",
        "audit_ok": "📊 **Audyt za {month}**\n\n💳 Wpłynęło na konto: **{card} zł**\n💰 Całkowity zarobek: **{total} zł**\n〰️〰️〰️〰️〰️〰️〰️\n✉️ **W KOPERCIE: {env} zł**",
        "audit_err": "⚠️ Brak zapisów o dniach pracy w {month}.",
        "hist_err": "📭 Brak zapisanych zmian w {month}.",
        "hist_ok": "📜 **Historia zmian w {month}**\nKliknij ❌, aby usunąć błędny wpis:\n\n",
        "set_ok": "⚙️ <b>Ustawienia zostały zapisane!</b>",
        "err": "⚠️ Błąd przetwarzania danych.",
        "del_ok_alert": "✅ Zmiana z {date} została usunięta!",
        "del_ok_msg": "🗑 Wpis z **{date}** został pomyślnie usunięty z bazy.",
        "del_err": "⚠️ Wpis nie został znaleziony lub już go usunięto.",
        "pro_alert": "⭐ Subskrypcja PRO została pomyślnie aktywowana!",
        "pro_msg": "🎉 **Witamy w klubie PRO!**\n\nTwój status został pomyślnie zaktualizowany. Teraz wszystkie Twoje raporty Excel są generowane w profesjonalnym formacie.\nDziękujemy za wsparcie projektu!",
        
        "excel_headers": ["Data", "Dzień", "Status","Obiekt", "Auto", "Trasa", "Suma h", "Jazda", "50%", "100%", "Delegacja", "Dodatki", "Brutto", "NETTO"],
        "excel_caption": "📊 Twoja wypłata za {month}\n🕒 Przepracowano: **{hours} h.**\n💰 Zarobiono łącznie : **{net} zł**",
        "empty_db": "🤷‍♂️ W tym miesiącu nie masz jeszcze zapisanych raportów.",
        
        "btn_panel": "📱 Otwórz panel",
        "btn_help": "🚀 Jak to działa?",
        "btn_feedback": "💬 Opinie i pomysły",
        "btn_coffee_10": "☕️ Postaw koledze kawę (10 zł)",
        "btn_lunch_30": "🍕 Obiad dla kolegi (30 zł)",
        "btn_pro": "⭐ Aktywuj subskrypcję PRO",
        "opt_work": "💼 Praca",
        "opt_l4": "💊 Zwolnienie (L4)",
        "opt_urlop": "🌴 Urlop",
        "help_text": (
            "🤖 **Jak działam? To proste!**\n\n"
            "📱 **INTERAKTYWNY PANEL**\n"
            "Kliknij przycisk «Otwórz panel» — to Twoje główne narzędzie. Są tam trzy zakładki:\n"
            "1️⃣ **Zmiana** — do wpisywania przepracowanych godzin, L4 i urlopów.\n"
            "2️⃣ **Raporty** — do pobierania Excela, audytu wypłaty i usuwania błędnych wpisów.\n"
            "3️⃣ **Ustawienia** — do podania swoich stawek i celu finansowego.\n\n"
            "🌍 **INTELIGENTNA LOGISTYKA I WALUTA**\n"
            "Jeśli wpiszesz trasę, ale nie podasz godzin jazdy, sam je policzę! A jeśli zaznaczysz «Zagranica», przeliczę zarobek z Euro na Złotówki według aktualnego kursu NBP."
        ),
        "feedback_msg": "💡 Masz pomysł jak ulepszyć aplikację? Albo znalazłeś błąd?\n\nNapisz bezpośrednio do twórcy:\n👉 [Napisz do programisty](https://t.me/+1tajf8L_zck5NTQy)",
        "overwork_msg": "{hours}h na jednej zmianie to sporo! Pamiętaj o odpoczynku i życiu prywatnym. Zdrowie jest najważniejsze!",        
        "l4_loss_msg": "**AI-Asystent:** Zdrowie jest ważniejsze niż pieniądze! Ale informacyjnie: to L4 ({count} dni) kosztowało Cię ok. **{loss} zł** na czysto.",
        
        # --- НОВЫЕ КЛЮЧИ ---
        "menu_btn": "📱 Panel",
        "menu_msg": "⚡️ Interaktywny panel jest teraz zawsze dostępny pod przyciskiem menu po lewej stronie pola wprowadzania!",
        "welcome_text": "Cześć! Jestem Twoją księgową AI 👩‍💼\n\nPomogę Ci prowadzić ewidencję zmian, logistyki i dokładnie obliczę Twoją wypłatę (brutto, netto, a nawet «w kopercie»).\n\nAby zacząć, kliknij przycisk **«📱 Panel»** w menu w lewym dolnym rogu! 👇"
    }
}