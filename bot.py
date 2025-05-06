import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация API (через переменные окружения)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "youtube-mp3-2025.p.rapidapi.com"
API_URL = "https://youtube-mp3-2025.p.rapidapi.com/v1/social/youtube/audio"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Привет! Отправь мне ссылку на YouTube видео, и я пришлю аудио.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text
        if not ("youtube.com" in url or "youtu.be" in url):
            await update.message.reply_text("❌ Это не YouTube ссылка!")
            return

        video_id = extract_video_id(url)
        
        # Параметры запроса
        params = {
            "id": video_id,
            "ext": "mp3",
            "quality": "128kbps"
        }

        # Отправка запроса к API
        response = requests.get(
            API_URL,
            headers={
                "X-RapidAPI-Host": API_HOST,
                "X-RapidAPI-Key": RAPIDAPI_KEY
            },
            params=params
        )

        # Обработка ответа
        if response.status_code == 200:
            data = response.json()
            if data.get("url"):
                await update.message.reply_audio(
                    audio=data["url"],
                    title=data.get("title", "Аудио")[:64],
                    duration=data.get("duration", 0)
                )
            else:
                await update.message.reply_text("❌ Аудио не найдено")
        else:
            await update.message.reply_text(f"⚠️ Ошибка API: {response.status_code}")

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("🚫 Произошла ошибка. Попробуйте позже.")

def extract_video_id(url: str) -> str:
    """Извлекает ID видео из разных форматов ссылок"""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url.split("/")[-1]

if __name__ == "__main__":
    # Инициализация бота
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Конфигурация для Render
    if os.getenv("RENDER"):
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 10000)),
            webhook_url=os.getenv("WEBHOOK_URL"),
            secret_token=os.getenv("SECRET_TOKEN", "DEFAULT_SECRET")
        )
    else:
        app.run_polling()