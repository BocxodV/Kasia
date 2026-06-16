// js/core/telegram.js

// Экспортируем объект tg, чтобы другие модули могли отправлять данные и вызывать алерты
export const tg = window.Telegram.WebApp;

// Функция для первичной настройки приложения при старте
export function initTelegram() {
    tg.expand();
    tg.ready();

    // Устанавливаем точную высоту от Telegram, чтобы контент не уходил за пределы экрана
    function syncViewportHeight() {
        const h = tg.viewportStableHeight || tg.viewportHeight || window.innerHeight;
        document.documentElement.style.setProperty('--tg-viewport-height', `${h}px`);
    }
    syncViewportHeight();
    tg.onEvent('viewportChanged', syncViewportHeight);
}