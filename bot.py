import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests  # Заменяем aiohttp на синхронные запросы

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Безопасное хранение данных
TOKEN = os.getenv("8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk")  # Получаем из переменных окружения
RAPID_API_KEY = os.getenv("d6b3cbc8c6msh937aca5d90c4dc5p1c1a7fjsn8d19c67c0361")
RAPID_API_HOST = "youtube-mp3.p.rapidapi.com"
RAPID_API_URL = "https://youtube-mp3.p.rapidapi.com/get"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Привет! Пришли ссылку на YouTube видео, и я отправлю тебе аудио!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    try:
        # Проверка и извлечение ID
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Некорректная YouTube ссылка")
        
        await update.message.reply_text("⏳ Обрабатываю запрос...")

        # Отправка запроса к API
        response = requests.get(
            RAPID_API_URL,
            headers={
                "X-RapidAPI-Key": RAPID_API_KEY,
                "X-RapidAPI-Host": RAPID_API_HOST
            },
            params={"id": video_id}
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка API: {response.text}")

        data = response.json()
        
        if data.get("status") != "ok":
            raise Exception(data.get("msg", "Неизвестная ошибка сервиса"))

        # Отправка аудио
        await update.message.reply_audio(
            audio=data['link'],
            title=f"{data.get('title', 'audio')[:64]}.mp3",
            performer="YouTube Audio Bot"
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def extract_video_id(url: str) -> str:
    # Улучшенная обработка разных форматов ссылок
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "youtube.com/embed/" in url:
        return url.split("embed/")[1].split("?")[0]
    return None

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🟢 Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()