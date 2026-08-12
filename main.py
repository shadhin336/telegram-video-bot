import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("স্বাগতম! আমাকে যেকোনো ভিডিওর লিংক দিন, আমি ডাউনলোড করে পাঠাচ্ছি।")

async def download_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status_msg = await update.message.reply_text("ভিডিও প্রসেস করা হচ্ছে, কিছুক্ষণ অপেক্ষা করুন...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,  # 50 MB Telegram limit
    }

    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("ভিডিও আপলোড করা হচ্ছে...")

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        if filename and os.path.exists(filename):
            os.remove(filename)
            
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"দুঃখিত, ভিডিওটি ডাউনলোড করা সম্ভব হয়নি।\nকারণ: {str(e)}")
        if filename and os.path.exists(filename):
            os.remove(filename)

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN পাওয়া যায়নি!")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_video))

    print("Bot run হচ্ছে...")
    application.run_polling()

if __name__ == '__main__':
    main()
