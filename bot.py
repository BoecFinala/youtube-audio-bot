import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import nest_asyncio

nest_asyncio.apply()

TOKEN = '8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk'

# Настройки API
RAPID_API_KEY = "d6b3cbc8c6msh937aca5d90c4dc5p1c1a7fjsn8d19c67c0361"
RAPID_API_HOST = "youtube-mp36.p.rapidapi.com/get"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Скинь ссылку на YouTube — я отправлю тебе аудиодорожку через сторонний сервис 🎧")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("Отправляю на обработку... ⏳")
        
        # Отправляем запрос на внешний сервис
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": RAPID_API_HOST
        }
        params = {"url": url}

        try:
            response = requests.get(RAPID_API_HOST, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                mp3_url = data.get('link')
                title = data.get('title', 'audio').replace("/", "_").replace("\\", "_") + ".mp3"

                if mp3_url:
                    # Отправляем ссылку как аудиофайл
                    await update.message.reply_audio(mp3_url, filename=title)
                else:
                    await update.message.reply_text(f"Не удалось обработать ссылку:\n{data}")
            else:
                await update.message.reply_text(f"Ошибка при обработке: {response.status_code}")
        except Exception as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")
    else:
        await update.message.reply_text("Пришли корректную ссылку с YouTube.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    await app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    asyncio.run(main())