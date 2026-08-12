import os
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

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
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,  # 50 MB
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'referer': 'https://www.eporner.com/',
        'nocheckcertificate': True,
        'force_generic_extractor': False, # মূল এক্সট্র্যাক্টর কাজ না করলে
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
        # Fallback Strategy: Generic Extractor ট্রাই করা
        try:
            ydl_opts['force_generic_extractor'] = True
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await status_msg.edit_text("ভিডিও আপলোড করা হচ্ছে...")
            with open(filename, 'rb') as video_file:
                await update.message.reply_video(video=video_file)

            if filename and os.path.exists(filename):
                os.remove(filename)
            await status_msg.delete()

        except Exception as err:
            await status_msg.edit_text(f"দুঃখিত, সাইটের নতুন আপডেটের কারণে ডাউনলোড করা সম্ভব হয়নি।\n\nত্রুটি: {str(err)}")
            if filename and os.path.exists(filename):
                os.remove(filename)

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN পাওয়া যায়নি!")

    Thread(target=run_health_check_server, daemon=True).start()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_video))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
