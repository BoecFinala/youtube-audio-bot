import os
import yt_dlp
from moviepy.audio.io.AudioFileClip import AudioFileClip
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import nest_asyncio

# Применяем исправление для Windows
nest_asyncio.apply()

TOKEN = '8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Скинь ссылку на видео с YouTube, и я вырежу аудиодорожку для тебя 🎧")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("Скачиваю видео... ⏳")
        try:
            # Скачивание видео с помощью yt-dlp + cookies.json
            ydl_opts = {
                'format': 'mp4',
                'outtmpl': 'video.mp4',
                'cookiefile': 'cookies.txt',  # ← подключаем файл с куками
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            video_path = "video.mp4"

            # Получаем название видео
            with yt_dlp.YoutubeDL({'cookiefile': 'cookies.json'}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', 'audio').replace("/", "_").replace("\\", "_")

            # Извлечение аудио
            audio_path = f"{video_title}.mp3"
            with AudioFileClip(video_path) as clip:
                clip.write_audiofile(audio_path)

            # Отправка файла
            with open(audio_path, 'rb') as audio_file:
                await update.message.reply_audio(audio_file)

            # Очистка
            os.remove(video_path)
            os.remove(audio_path)

        except Exception as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")
    else:
        await update.message.reply_text("Пришли корректную ссылку с YouTube.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    # Запуск через nest_asyncio
    asyncio.run(main())