import os
import logging
import requests
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация API
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "youtube-mp3-2025.p.rapidapi.com"
API_URL = "https://youtube-mp3-2025.p.rapidapi.com/v1/social/youtube/audio"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Привет! Отправь мне ссылку на YouTube видео, и я пришлю аудио.")

def extract_video_id(url: str) -> str:
    """Извлекает ID видео из различных форматов ссылок"""
    # Очистка URL от параметров и якорей
    clean_url = url.split("?")[0].split("#")[0]
    
    if "youtu.be/" in clean_url:
        return clean_url.split("youtu.be/")[1].split("/")[0]
    if "v=" in clean_url:
        return clean_url.split("v=")[1].split("&")[0]
    if "embed/" in clean_url:
        return clean_url.split("embed/")[1].split("/")[0]
    return clean_url.split("/")[-1]

def download_audio(url: str) -> str:
    """Резервное скачивание через yt-dlp"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3")
            return filename
    except Exception as e:
        logger.error(f"Ошибка yt-dlp: {str(e)}", exc_info=True)
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text
        if not ("youtube.com" in url or "youtu.be" in url):
            await update.message.reply_text("❌ Это не YouTube ссылка!")
            return

        video_id = extract_video_id(url)
        logger.info(f"Извлеченный ID: {video_id}")

        # Попытка через RapidAPI
        params = {"id": video_id, "ext": "mp3", "quality": "128kbps"}
        headers = {"X-RapidAPI-Host": API_HOST, "X-RapidAPI-Key": RAPIDAPI_KEY}
        
        response = requests.get(API_URL, headers=headers, params=params)
        logger.info(f"Ответ API: {response.status_code} - {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and data.get("url"):
                await update.message.reply_audio(
                    audio=data["url"],
                    title=data.get("title", "Аудио")[:64],
                    duration=data.get("duration", 0)
                )
                return
            error_msg = data.get('msg', 'Аудио не найдено')
        else:
            error_msg = f"Ошибка API: {response.status_code}"

        # Резервный метод через yt-dlp
        await update.message.reply_text(f"⚠️ {error_msg}. Пробую через резервный метод...")
        
        audio_path = download_audio(url)
        if audio_path:
            try:
                await update.message.reply_audio(audio=open(audio_path, "rb"))
            finally:
                os.remove(audio_path)  # Удаление файла после отправки
        else:
            await update.message.reply_text("❌ Не удалось получить аудио ни одним способом")

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        await update.message.reply_text("🚫 Произошла внутренняя ошибка. Попробуйте позже.")

if __name__ == "__main__":
    # Создаем папку для загрузок
    os.makedirs("downloads", exist_ok=True)
    
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