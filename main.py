import os
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# تنظیمات اصلی
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_USERNAME = "bombdaramadbot"  # آیدی درست ربات شما

DB_FILE = "users_db.json"

# [بخش‌های load_db و save_db و سرور رایلی مثل قبل است...]
# (چون کد طولانی بود، از اینجا به بعد منطق دکمه‌ها رو برات ست کردم)

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["💎 شروع کسب درآمد 💎"],
        ["🏠 حساب کاربری", "🌟 برترین کاربران"],
        ["💸 برداشت از حساب", "📊 تاریخچه برداشت"],
        ["📜 قوانین", "📞 پشتیبانی", "📚 راهنما"]
    ], resize_keyboard=True)

async def start_command(update, context):
    user = update.effective_user
    # (منطق ذخیره کاربر مثل قبل...)
    await update.message.reply_text("به ربات بمب خوش آمدید 🌹", reply_markup=get_main_keyboard())

async def handle_message(update, context):
    text = update.message.text
    if "شروع کسب درآمد" in text:
        user_id = update.effective_user.id
        await update.message.reply_text(f"👇 با هر دعوت ۱۲۰,۰۰۰ تومان میده 👇\nhttps://t.me/{BOT_USERNAME}?start={user_id}")
    # (ادامه منطق بقیه دکمه‌ها...)

if __name__ == "__main__":
    # اجرای وب‌سرور برای رایلی
    threading.Thread(target=start_health_server, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
