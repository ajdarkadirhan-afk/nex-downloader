
import os
import asyncio
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
MAX_SIZE = 45 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я NexDownloaderBot 📥\n"
        "Отправь ссылку на видео, которое разрешено скачивать."
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        await update.message.reply_text("Отправь корректную ссылку на видео.")
        return

    await update.message.reply_text("⏳ Пробую загрузить видео...")

    try:
        with tempfile.TemporaryDirectory() as folder:
            opts = {
                "format": "best[ext=mp4][filesize<45000000]/best[ext=mp4]",
                "outtmpl": str(Path(folder) / "video.%(ext)s"),
                "noplaylist": True,
                "max_filesize": MAX_SIZE,
                "quiet": True,
            }

            await asyncio.to_thread(
                lambda: yt_dlp.YoutubeDL(opts).download([url])
            )

            files = list(Path(folder).glob("video.*"))
            if not files or files[0].stat().st_size > MAX_SIZE:
                await update.message.reply_text(
                    "Видео не найдено или файл слишком большой."
                )
                return

            with files[0].open("rb") as video:
                await update.message.reply_video(video=video)

    except Exception:
        await update.message.reply_text(
            "Не получилось скачать видео. Попробуй другую ссылку."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пришли ссылку на поддерживаемый видеосайт. "
        "Доступность зависит от сайта и размера видео."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    app.run_polling()

if __name__ == "__main__":
    main()
