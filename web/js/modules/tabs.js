// js/modules/tabs.js
import { tg } from '../core/telegram.js';

// --- МАГИЯ ПОЛАРОИДОВ ---
const categoryMap = {
    'shift': 'shift',
    'garage': 'garage',
    'route': 'route',
    'envelope': 'envelope',
    'delete': 'history', 
    'export': 'export',
    'analytics': 'analytics',
    'savings': 'savings',
    'settings': 'settings'
};

export function updatePolaroid(tabId) {
    const category = categoryMap[tabId];
    if (!category) return;
    
    const randomNum = Math.floor(Math.random() * 5) + 1;
    const imgElement = document.querySelector(`#${tabId} .kasiaAvatar`);
    
    if (imgElement) {
        let finalCategory = category;
        const statusInput = document.getElementById("statusInput");
        // Если статус "Отпуск" и мы на вкладке Смена, используем категорию vacation
        if (statusInput && tabId === 'shift' && statusInput.value === 'Urlop') {
            finalCategory = 'vacation';
        }
        imgElement.src = `arts/kasia_${finalCategory}_${randomNum}.jpg`;
    }
}

// --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ВКЛАДОК ---
const tabsOrder = ['shift', 'garage', 'route', 'envelope', 'delete', 'export', 'analytics', 'savings', 'settings'];

export function openTab(tabId) {
    const allContents = document.querySelectorAll(".content");
    const allTabs = document.querySelectorAll(".v-tab"); 
  
    allContents.forEach(c => { c.classList.remove("active"); c.classList.remove("page-fade"); });
    allTabs.forEach(t => t.classList.remove("active"));
  
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add("active");
        document.querySelector('.planner-page').scrollTop = 0;
        
        updatePolaroid(tabId); // Вызываем рулетку картинок
        setTimeout(() => { targetContent.classList.add("page-fade"); }, 10);
    }
  
    const targetTab = document.getElementById("tab_" + tabId);
    if (targetTab) targetTab.classList.add("active");

    // Обращаемся к tg, который мы импортировали сверху
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
}

// --- ЛОГИКА СВАЙПОВ ОТКЛЮЧЕНА ---
export function setupSwipes() {
    // Оставляем только проверку статуса для полароида, сами свайпы убраны по запросу.
    const statusInput = document.getElementById("statusInput");
    if (statusInput) {
        statusInput.addEventListener("change", function () {
            updatePolaroid('shift');
        });
    }
}