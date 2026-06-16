// js/app.js
import { tg, initTelegram } from './core/telegram.js';
import { state, TRANSLATIONS } from './core/state.js';
import { openTab, setupSwipes, updatePolaroid } from './modules/tabs.js';
import { triggerCarScan } from './modules/camera.js';
import { sendShift, sendReportReq, sendBossReportReq, sendHistoryReq, sendAnalyticsReq, sendSettings, sendAuditReq, openGoogleMaps } from './modules/api.js';

document.addEventListener('DOMContentLoaded', () => {
    initTelegram();
    setupSwipes();
    document.getElementById("dateInput").valueAsDate = new Date();

    // --- ЛОГИКА ПЕРЕВОДОВ И ЦЕЛЕЙ ---
    function updateMotivationText() {
        let t = TRANSLATIONS[state.currentLang] || TRANSLATIONS["RUS"];
        let motText = t.mot_start || "Вперед!";
        if (state.percent > 0) motText = t.mot_good || "Отлично!";
        if (state.percent > 30) motText = t.mot_fast || "Быстро!";
        if (state.percent > 70) motText = t.mot_close || "Почти!";
        if (state.percent >= 100) motText = t.mot_done || "Готово!";
        let motEl = document.getElementById("goalMotivation");
        if (motEl) motEl.innerText = motText;
    }

    function applyLanguage(lang) {
        try {
            state.currentLang = lang;
            const t = TRANSLATIONS[lang] || TRANSLATIONS["RUS"];
            for (let key in t) {
                let el = document.getElementById(key);
                if (el) {
                    if (el.tagName === 'INPUT' && (el.type === 'text' || el.type === 'number')) {
                        el.placeholder = t[key];
                    } else if (el.tagName !== 'INPUT') {
                        el.innerText = t[key];
                    }
                }
            }
            document.getElementById("langInput").value = lang;
            let goalInput = document.getElementById("goalNameInput");
            let customGoalName = goalInput ? goalInput.value : "";
            let goalDisplay = document.getElementById("goalNameDisplay");
            if (goalDisplay) {
                goalDisplay.innerText = !customGoalName ? (t.default_goal || "Моя цель") : customGoalName;
            }
            updateMotivationText();
        } catch (e) {
            console.error("Language switch error:", e);
        }
    }

    function changeLanguage() {
        let lang = document.getElementById("langInput").value;
        applyLanguage(lang);
    }

    // --- ЧТЕНИЕ ДАННЫХ ИЗ URL ---
    const urlParams = new URLSearchParams(window.location.search);
    state.gTarget = parseFloat(urlParams.get("g_target")) || 8000;
    state.cSav = parseFloat(urlParams.get("c_sav")) || 0; 
    state.percent = (state.gTarget > 0 && state.cSav > 0) ? Math.min((state.cSav / state.gTarget) * 100, 100) : 0;

    applyLanguage(urlParams.get("lang") || "RUS"); 

    ["base", "extra", "eur", "drive", "drive_eur", "car", "g_target", "g_dead"].forEach(key => {
        if (urlParams.has(key)) {
            let inputMap = {"base":"baseRateInput", "extra":"extraRateInput", "eur":"eurRateInput", "drive":"driveRateInput", "drive_eur":"driveEurRateInput", "car":"carInput", "g_target":"goalTargetInput", "g_dead":"goalDeadlineInput"};
            if(document.getElementById(inputMap[key])) document.getElementById(inputMap[key]).value = urlParams.get(key);
        }
    });

    let passedGName = urlParams.get("g_name");
    if (passedGName && passedGName !== "Моя цель" && passedGName !== "null") {
        let gNameInput = document.getElementById("goalNameInput");
        if(gNameInput) gNameInput.value = passedGName;
        let gNameDisp = document.getElementById("goalNameDisplay");
        if(gNameDisp) gNameDisp.innerText = passedGName;
    }

    let goalTxtDisp = document.getElementById("goalTextDisplay");
    if(goalTxtDisp) goalTxtDisp.innerText = `${state.cSav.toFixed(0)} / ${state.gTarget} zł`;
    setTimeout(() => { 
        let pb = document.getElementById("goalProgressBar");
        if(pb) pb.style.width = state.percent + "%"; 
    }, 300);

    function populateDatalist(listId, dataString) {
        const list = document.getElementById(listId);
        if (!list || !dataString) return;
        decodeURIComponent(dataString).split(',').forEach(item => {
            if (item.trim() !== "") {
                const option = document.createElement('option');
                option.value = item;
                list.appendChild(option);
            }
        });
    }
    populateDatalist('locationsList', urlParams.get('locs') || "");
    populateDatalist('carsList', urlParams.get('cars') || "");
    populateDatalist('garageCarsList', urlParams.get('cars') || "");

    // --- СИНХРОНИЗАЦИЯ МАШИН И ДАТ ---
    const mainCarInput = document.getElementById("carInput");
    const garageCarInput = document.getElementById("garageCarInput");
    if (mainCarInput && garageCarInput) {
        mainCarInput.addEventListener("input", (e) => { garageCarInput.value = e.target.value; });
        garageCarInput.addEventListener("input", (e) => { mainCarInput.value = e.target.value; });
    }

    document.getElementById("statusInput").addEventListener("change", function () {
        document.getElementById("endDateRow").style.display = (this.value === "L4" || this.value === "Urlop") ? "flex" : "none";
    });

    // --- СИНХРОНИЗАЦИЯ МАРШРУТА ---
    const routeFrom = document.getElementById("routeFrom");
    const routeTo = document.getElementById("routeTo");
    const mainRouteInput = document.getElementById("routeInput");

    function syncRoute() {
        if (!mainRouteInput) return;
        const fromText = routeFrom ? routeFrom.value.trim() : "";
        const toText = routeTo ? routeTo.value.trim() : "";

        if (fromText && toText) {
            mainRouteInput.value = `${fromText} - ${toText}`;
        } else if (fromText) {
            mainRouteInput.value = fromText;
        } else if (toText) {
            mainRouteInput.value = toText;
        } else {
            mainRouteInput.value = "";
        }
    }

    if (routeFrom) routeFrom.addEventListener("input", syncRoute);
    if (routeTo) routeTo.addEventListener("input", syncRoute);

    // --- ПРИВЯЗКА ФУНКЦИЙ К WINDOW (ЧТОБЫ РАБОТАЛ HTML ONCLICK) ---
    window.openTab = openTab;
    window.changeLanguage = changeLanguage;
    window.triggerCarScan = triggerCarScan;
    window.sendShift = sendShift;
    window.sendReportReq = sendReportReq;
    window.sendBossReportReq = sendBossReportReq;
    window.sendHistoryReq = sendHistoryReq;
    window.sendAnalyticsReq = sendAnalyticsReq;
    window.sendSettings = sendSettings;
    window.sendAuditReq = sendAuditReq;
    window.openGoogleMaps = openGoogleMaps;

    window.showHelp = function(sectionId) {
        const modal = document.getElementById("helpModal");
        const titleEl = document.getElementById("helpTitle");
        const textEl = document.getElementById("helpText");
        
        let t = TRANSLATIONS[state.currentLang] || TRANSLATIONS["RUS"];
        
        const texts = {
            work_data: t.help_work_data || "Здесь заполняются базовые данные о смене: Дата, Статус (Работа/Больничный/Отпуск), Локация. Если смена за границей или полагается диета - отметьте это галочкой.",
            logistics: t.help_logistics || "Укажите часы работы на объекте и часы в пути. Обязательно впишите маршрут и авто, если вы были за рулем.",
            lang: t.help_lang || "Выберите язык интерфейса и приложения. Все дальнейшие сообщения от бота будут приходить на этом языке.",
            goal: t.help_goal || "Установите свою финансовую цель! Введите название (например, 'Машина'), нужную сумму и дату. Кася рассчитает, сколько нужно откладывать.",
            profile: t.help_profile || "Укажите ваши актуальные ставки (базовая, переработки, евро, за рулем). Эта информация будет использоваться для расчетов."
        };
        
        titleEl.innerText = t.help_title || "Справка";
        textEl.innerText = texts[sectionId] || "";
        modal.style.display = "block";
    };

    window.closeHelp = function() {
        document.getElementById("helpModal").style.display = "none";
    };

    window.onclick = function(event) {
        const modal = document.getElementById("helpModal");
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Запуск первой вкладки
    openTab('shift');
});