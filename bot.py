import os
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = '8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk'

# Настройки API (обновленные)
RAPID_API_URL = "https://youtube-mp3.p.rapidapi.com/get"
RAPID_API_KEY = "d6b3cbc8c6msh937aca5d90c4dc5p1c1a7fjsn8d19c67c0361"
RAPID_API_HOST = "youtube-mp3.p.rapidapi.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Привет! Пришли ссылку на YouTube видео, и я отправлю тебе аудио!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("⚠️ Пожалуйста, отправьте корректную YouTube ссылку")
        return

    await update.message.reply_text("⏳ Обрабатываю запрос...")
    
    try:
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Не удалось извлечь ID видео")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                RAPID_API_URL,
                headers={
                    "X-RapidAPI-Key": RAPID_API_KEY,
                    "X-RapidAPI-Host": RAPID_API_HOST
                },
                params={"id": video_id}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                data = await response.json()
                
                if data.get("status") != "ok":
                    raise Exception(f"Сервисная ошибка: {data.get('msg', 'Unknown error')}")
                
                download_link = data.get("link")
                title = f"{data.get('title', 'audio')}.mp3".replace("/", "_")

                await update.message.reply_audio(
                    audio=download_link,
                    title=title[:64],  # Ограничение Telegram
                    performer="YouTube Audio Bot"
                )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def extract_video_id(url: str) -> str:
    # Извлечение ID видео из разных форматов ссылок
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    return url.split("/")[-1]

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🟢 Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()