// js/core/telegram.js

// Export the tg WebApp context to allow messaging and alerts
export const tg = window.Telegram.WebApp;

// Initialize client application and expand container on load
export function initTelegram() {
    tg.expand();
    tg.ready();

    // Calculate the exact viewport height dynamically to prevent scroll clipping
    function syncViewportHeight() {
        const h = tg.viewportStableHeight || tg.viewportHeight || window.innerHeight;
        document.documentElement.style.setProperty('--tg-viewport-height', `${h}px`);
    }
    syncViewportHeight();
    tg.onEvent('viewportChanged', syncViewportHeight);
}