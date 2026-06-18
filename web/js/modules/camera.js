// js/modules/camera.js
import { tg } from '../core/telegram.js';
import { state, TRANSLATIONS } from '../core/state.js';

let videoStream = null;

export async function triggerCarScan() {
    const video = document.getElementById('cameraVideo');
    const container = document.getElementById('cameraContainer');
    const scanBtn = document.getElementById('btn_scan_car');
    
    // Элементы для вставки результата
    const mainCarInput = document.getElementById("carInput");
    const garageCarInput = document.getElementById("garageCarInput");

    // СЦЕНАРИЙ 1: КАМЕРА ВЫКЛЮЧЕНА -> ВКЛЮЧАЕМ ЕЕ
    if (!videoStream) {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" },
                audio: false
            });
            
            video.srcObject = videoStream;
            
            video.onloadedmetadata = () => {
                video.play().catch(e => console.error("Ошибка запуска видео:", e));
            };

            container.style.display = "block"; 
            
            scanBtn.innerText = TRANSLATIONS[state.currentLang].btn_scan_take_photo || "🔴 Сделать снимок!";
            scanBtn.style.backgroundColor = "#ff7675"; 
        } catch (err) {
            console.error("Camera access denied:", err);
            tg.showAlert(TRANSLATIONS[state.currentLang].camera_no_access || "⚠️ Ошибка: нет доступа к камере. Разреши Telegram использовать камеру в настройках телефона!");
        }
    } 
    // СЦЕНАРИЙ 2: КАМЕРА УЖЕ РАБОТАЕТ -> ДЕЛАЕМ СНИМОК И ОТПРАВЛЯЕМ
    else {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
        container.style.display = "none"; 
        
        scanBtn.innerText = TRANSLATIONS[state.currentLang].kasia_thinking || "Кася думает... 🧠";
        scanBtn.style.backgroundColor = "var(--highlight-green)"; 
        scanBtn.disabled = true;

        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append("photo", blob, "car_scan.jpg");
            formData.append("user_id", tg.initDataUnsafe?.user?.id || "unknown");
            formData.append("initData", tg.initData || "");

            try {
                // Прямой вызов нашего API-шлюза на Cloud Run
                const backendUrl = "https://e-ksiegowa-254558688282.europe-central2.run.app/api/scan-car";
                const response = await fetch(backendUrl, { method: "POST", body: formData });
                
                if (response.ok) {
                    const result = await response.json();
                    
                    // Проверяем, есть ли хоть что-то (машина ИЛИ номер)
                    if (result && (result.car || result.plate)) {
                        // Склеиваем всё в одну строку
                        const carName = result.car || "";
                        const plateNumber = result.plate || "";
                        const fullCarString = `${carName} ${plateNumber}`.trim();
                        
                        // Вставляем полную строку в оба поля и генерируем события для их синхронизации
                        if (garageCarInput) {
                            garageCarInput.value = fullCarString;
                            garageCarInput.dispatchEvent(new Event('input'));
                            garageCarInput.dispatchEvent(new Event('change'));
                        }
                        if (mainCarInput) {
                            mainCarInput.value = fullCarString;
                            mainCarInput.dispatchEvent(new Event('input'));
                            mainCarInput.dispatchEvent(new Event('change'));
                        }
                        
                        tg.showAlert((TRANSLATIONS[state.currentLang].scan_recognized || "✅ Распознано: ") + fullCarString);
                    }
                } else {
                    tg.showAlert(TRANSLATIONS[state.currentLang].scan_server_err || "❌ Ошибка сервера (пока не подключен ИИ).");
                }
            } catch (error) {
                console.error("Scan error:", error);
                tg.showAlert(TRANSLATIONS[state.currentLang].scan_backend_offline || "⚠️ Бэкенд с ИИ пока не подключен, но фото успешно сделано!");
            } finally {
                scanBtn.innerText = TRANSLATIONS[state.currentLang].btn_scan_car || "📸 Включить сканер";
                scanBtn.disabled = false;
            }
        }, 'image/jpeg', 0.85); 
    }
}