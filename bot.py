import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация API
API_KEY = "d6b3cbc8c6msh937aca5d90c4dc5p1c1a7fjsn8d19c67c0361"
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
        
        params = {
            "id": video_id,
            "ext": "mp3",
            "quality": "128kbps"
        }

        response = requests.get(
            API_URL,
            headers={"X-RapidAPI-Host": API_HOST, "X-RapidAPI-Key": API_KEY},
            params=params
        )

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
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return url.split("/")[-1]

if __name__ == "__main__":
    app = Application.builder().token("8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()