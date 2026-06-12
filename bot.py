import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "BU_YERGA_TOKEN_YOZING")

def is_supported_url(url):
    return any(x in url for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com", "vm.tiktok.com"])

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()

    if not is_supported_url(message):
        await update.message.reply_text("❌ Faqat YouTube, Instagram yoki TikTok havolalarini yuboring!")
        return

    await update.message.reply_text("⏳ Video yuklanmoqda, kuting...")

    output_path = f"video_{update.message.message_id}.mp4"

    ydl_opts = {
        "outtmpl": output_path,
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 50 * 1024 * 1024,  # 50MB (Telegram limiti)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message])

        with open(output_path, "rb") as video:
            await update.message.reply_video(
                video=video,
                caption="✅ Mana videongiz!",
                supports_streaming=True
            )

    except yt_dlp.utils.DownloadError as e:
        if "File is larger than max-filesize" in str(e):
            await update.message.reply_text("❌ Video 50MB dan katta, Telegram qabul qilmaydi!")
        else:
            await update.message.reply_text(f"❌ Yuklab bo'lmadi: {str(e)[:100]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)[:100]}")
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men video yuklovchi botman.\n\n"
        "📥 Quyidagi platformalardan havola yuboring:\n"
        "• YouTube\n"
        "• Instagram (reels, post)\n"
        "• TikTok\n\n"
        "⚠️ Max hajm: 50MB"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/start'), start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
