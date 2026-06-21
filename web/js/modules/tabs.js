// js/modules/tabs.js
import { tg } from '../core/telegram.js';

// --- Polaroid Image Generator ---
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
    
    // File extensions configuration mapping for category assets
    const pngCategories = new Set(['garage', 'envelope', 'analytics']);
    
    if (imgElement) {
        let finalCategory = category;
        const statusInput = document.getElementById("statusInput");
        if (statusInput && tabId === 'shift' && statusInput.value === 'Urlop') {
            finalCategory = 'vacation';
        }
        const ext = pngCategories.has(finalCategory) ? 'png' : 'jpg';
        imgElement.src = `arts/kasia_${finalCategory}_${randomNum}.${ext}`;
    }
}

// --- Tab Switching Logic ---
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
        
        updatePolaroid(tabId); // Randomly update polaroid image
        setTimeout(() => { targetContent.classList.add("page-fade"); }, 10);
    }
  
    const targetTab = document.getElementById("tab_" + tabId);
    if (targetTab) targetTab.classList.add("active");

    // Call Telegram Haptic Feedback interface
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
}

// --- Touch Swipe Event Listeners Disabled ---
export function setupSwipes() {
    // Bind polaroid update specifically to shift status changes
    const statusInput = document.getElementById("statusInput");
    if (statusInput) {
        statusInput.addEventListener("change", function () {
            updatePolaroid('shift');
        });
    }
}