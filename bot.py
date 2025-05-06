import os
import uuid
import logging
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логгера
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk'

# Конфигурация yt-dlp для аудио
YDL_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'cookiefile': 'cookies.txt',
    'noplaylist': True,
    'quiet': True,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Привет! Пришли ссылку на YouTube видео, и я пришлю тебе аудио!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    url = update.message.text.strip()
    
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("⚠️ Это не YouTube ссылка! Попробуйте еще раз.")
        return

    try:
        # Генерируем уникальный ID для файла
        file_id = str(uuid.uuid4())
        temp_audio = f"downloads/{file_id}.mp3"
        
        await update.message.reply_text("⏳ Скачиваю аудио...")
        
        # Скачиваем и конвертируем в MP3
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            os.rename(filename, temp_audio)
        
        # Получаем метаданные
        title = info.get('title', 'Аудио трек')[:50]
        performer = info.get('uploader', 'Неизвестный исполнитель')[:30]
        duration = info.get('duration', 0)

        # Отправляем аудио
        await update.message.reply_audio(
            audio=open(temp_audio, 'rb'),
            title=title,
            performer=performer,
            duration=duration
        )
        
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        await update.message.reply_text("❌ Ошибка скачивания. Проверьте ссылку и попробуйте снова.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text("🔥 Произошла непредвиденная ошибка. Попробуйте позже.")
    finally:
        # Всегда очищаем временные файлы
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

def main():
    # Создаем папку для загрузок
    os.makedirs("downloads", exist_ok=True)
    
    # Настройка приложения
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Для Render.com (раскомментировать при деплое)
    # application.run_webhook(
    #     listen="0.0.0.0",
    #     port=int(os.environ.get("PORT", 10000)),
    #     webhook_url=os.environ.get("WEBHOOK_URL")
    # )
    
    # Для локального тестирования
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()