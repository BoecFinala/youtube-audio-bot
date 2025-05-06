import requests
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import nest_asyncio

nest_asyncio.apply()

TOKEN = '8027258642:AAFjyM9Bze0bXITSOKKwBYjnxJ5Vt6JpLAk'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Скинь ссылку на YouTube — я вырежу аудио и пришлю тебе 🎧")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "youtube.com" in url or "youtu.be" in url:
        await update.message.reply_text("Обрабатываю... ⏳")
        
        try:
            # Формируем POST-запрос к сервису
            data = {'video_url': url}
            response = requests.post('https://www.youtube-audio-extractor.com/extract', data=data)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                download_link = soup.find('a', {'class': 'download_file'})

                if download_link and 'href' in download_link.attrs:
                    mp3_url = download_link['href']
                    title = soup.find('input', {'id': 'file_name'}).get('value', 'audio').replace("/", "_").replace("\\", "_") + ".mp3"

                    # Загружаем и отправляем аудиофайл
                    with requests.get(mp3_url, stream=True) as r:
                        r.raise_for_status()
                        with open(title, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)

                    with open(title, 'rb') as audio_file:
                        await update.message.reply_audio(audio_file)

                    # Очистка
                    os.remove(title)
                else:
                    await update.message.reply_text("Не удалось найти аудиофайл.")
            else:
                await update.message.reply_text(f"Ошибка сервера: {response.status_code}")
        
        except Exception as e:
            await update.message.reply_text(f"Ошибка при обработке: {str(e)}")
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