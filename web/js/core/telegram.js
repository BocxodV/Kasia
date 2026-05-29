// js/core/telegram.js

// Экспортируем объект tg, чтобы другие модули могли отправлять данные и вызывать алерты
export const tg = window.Telegram.WebApp;

// Функция для первичной настройки приложения при старте
export function initTelegram() {
    tg.expand();
    tg.ready();
}