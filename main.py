import os
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------------------------------------------------
# تنظیمات اصلی ادمین و توکن تلگرام شما
# ---------------------------------------------------------
TOKEN = "8848328373:AAEC9baFxeSen7okKWv6bk6-tdejCP6_l6A"
ADMIN_ID = "5989298023"
BOT_USERNAME = "Havijbkbot"  

# ---------------------------------------------------------
# پایگاه داده ساده متنی برای ذخیره اطلاعات کاربران
# ---------------------------------------------------------
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# وب‌سرور داخلی برای زنده نگه داشتن ربات روی Railway
# ---------------------------------------------------------
class RailwayHealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Telegram Income Bot is Active on Railway!")
    def log_message(self, format, *args):
        return  

def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), RailwayHealthCheck)
    server.serve_forever()

# ---------------------------------------------------------
# منوهای کیبورد تلگرام
# ---------------------------------------------------------
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("💎 شروع کسب درآمد 💎")],
        [KeyboardButton("🏠 حساب کاربری"), KeyboardButton("🌟 برترین کاربران")],
        [KeyboardButton("💸 برداشت از حساب"), KeyboardButton("📊 تاریخچه برداشت")],
        [KeyboardButton("📜 قوانین"), KeyboardButton("📞 پشتیبانی"), KeyboardButton("📚 راهنما")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("📊 آمار کل ربات"), KeyboardButton("📢 ارسال پیام همگانی")],
        [KeyboardButton("🔙 بازگشت به منو اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_withdraw_keyboard():
    keyboard = [
        [KeyboardButton("💳 کارت به کارت"), KeyboardButton("🎁 پاکت هدیه")],
        [KeyboardButton("🔙 بازگشت به منو اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_option_keyboard():
    keyboard = [
        [KeyboardButton("🛠️ پنل ادمین")],
        [KeyboardButton("🔙 بازگشت به منو اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------------------------------------------------------
# مدیریت دستور /start و سیستم زیرمجموعه‌گیری
# ---------------------------------------------------------
async def start_command(update, context):
    user = update.effective_user
    user_id = str(user.id)
    db = load_db()

    if user_id not in db:
        db[user_id] = {
            "balance": 0,
            "invited_by": None,
            "invites_count": 0,
            "username": user.username or user.first_name or "کاربر تلگرام",
            "step": "none"
        }
        save_db(db)

        if context.args:
            inviter_id = context.args[0]
            if inviter_id in db and inviter_id != user_id:
                db[user_id]["invited_by"] = inviter_id
                db[inviter_id]["balance"] += 120000
                db[inviter_id]["invites_count"] += 1
                save_db(db)
                try:
                    await context.bot.send_message(
                        chat_id=int(inviter_id),
                        text=f"🎉 یک کاربر جدید با لینک شما وارد شد!\n💰 مبلغ ۱۲۰,۰۰۰ تومان به حساب شما اضافه شد."
                    )
                except:
                    pass

    welcome_text = "به ربات بمب خوش آمدید 🌹\nهر دعوت ≈ ۱۲۰,۰۰۰ تومان 💰\nموفق باشید☘️"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

# ---------------------------------------------------------
# مدیریت پیام‌های متنی منو
# ---------------------------------------------------------
async def handle_message(update, context):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    db = load_db()

    if user_id not in db:
        return

    user_data = db[user_id]

    if user_id == ADMIN_ID and user_data.get("step") == "broadcasting":
        db[ADMIN_ID]["step"] = "none"
        save_db(db)
        await update.message.reply_text("⏳ در حال ارسال پیام همگانی به تمام کاربران...")
        
        success_count = 0
        for uid in list(db.keys()):
            if uid == ADMIN_ID:
                continue
            try:
                await context.bot.send_message(chat_id=int(uid), text=text)
                success_count += 1
            except:
                pass
        
        await update.message.reply_text(f"📢 پیام همگانی شما با موفقیت به {success_count} کاربر ارسال شد.", reply_markup=get_main_keyboard())
        return

    if user_data.get("step") == "entering_withdraw_amount":
        db[user_id]["step"] = "none"
        save_db(db)
        
        notification_text = (
            f"🚨 **درخواست جدید برداشت از حساب!**\n\n"
            f"👤 کاربر: {user_data['username']}\n"
            f"🆔 آیدی عددی: `{user_id}`\n"
            f"💰 مبلغ درخواستی: {text} تومان\n"
            f"💼 کل موجودی کاربر: {user_data['balance']:,} تومان"
        )
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=notification_text)
        except:
            pass
            
        await update.message.reply_text("✅ درخواست برداشت شما ثبت شد و برای ادمین ارسال گردید.\nپس از بررسی واریز خواهد شد.", reply_markup=get_main_keyboard())
        return

    if "شروع کسب درآمد" in text:
        bot_text = (
            f"👇 با هر دعوت ۱۲۰,۰۰۰ تومان میده 👇\n"
            f"https://t.me/{BOT_USERNAME}?start={user_id}\n\n"
            f"☝️ لینک اختصاصی شما ☝️\n"
            f"با پخش بنر بالا و هر دعوت ۱۲۰,۰۰۰ کسب کنید 🎁🥰"
        )
        await update.message.reply_text(bot_text)

    elif "حساب کاربری" in text:
        profile_text = (
            f"👇 جزئیات حساب کاربری 👇\n\n"
            f"💼 موجودی کیف پول شما: {user_data['balance']:,} تومان\n"
            f"👥 تعداد زیرمجموعه‌های شما: {user_data['invites_count']}\n"
            f"✅ تعداد زیرمجموعه‌های احراز شده: {user_data['invites_count']}\n"
            f"❌ تعداد زیرمجموعه‌های احراز نشده: 0"
        )
        if user_id == ADMIN_ID:
            await update.message.reply_text(profile_text + "\n\n⚙️ شما ادمین اصلی ربات هستید.", reply_markup=get_admin_option_keyboard())
        else:
            await update.message.reply_text(profile_text)

    elif "برترین کاربران" in text:
        top_users = sorted(db.items(), key=lambda x: x[1]["invites_count"], reverse=True)[:10]
        leaderboard = "🌟 برترین کاربران 🌟\n\n"
        medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
        for i, (uid, udata) in enumerate(top_users):
            if i < len(medals):
                leaderboard += f"{medals[i]} - {udata['invites_count']} زیرمجموعه | {uid}\n"
        await update.message.reply_text(leaderboard)

    elif "برداشت از حساب" in text:
        await update.message.reply_text("لطفاً یکی از روش‌های برداشت زیر را انتخاب کنید:", reply_markup=get_withdraw_keyboard())

    elif "کارت به کارت" in text or "پاکت هدیه" in text:
        db[user_id]["step"] = "entering_withdraw_amount"
        save_db(db)
        await update.message.reply_text(f"💸 لطفاً مبلغ مورد نظر برای برداشت را وارد کنید:\n\n💰 موجودی حساب شما: {user_data['balance']:,} تومان")

    elif "تاریخچه برداشت" in text:
        await update.message.reply_text("📊 تاریخچه برداشت‌ها\n\n❌ هیچ برداشتی اخیر یافت نشد.")

    elif "قوانین" in text:
        await update.message.reply_text("📋 واریزی -\nصبور باشید بعد از برداشت شما پس از تایید داخل صف قرار می‌گره.\nتا یک هفته پردازش انجام میشه و پرداخت میشه.")

    elif "پشتیبانی" in text:
        await update.message.reply_text("اگر سوالی دارید، تیم پشتیبانی بمب آماده پاسخگویی به شماست\n💬 پشتیبانی ۲۴ ساعته بمب:\nپیام خود را بگذارید")

    elif "راهنما" in text:
        help_guide = (
            "مرحله اول: ربات رو استارت کن\n"
            "مرحله دوم: بزن رو دکمه 💎 شروع کسب درآمد 💎\n"
            "مرحله سوم: لینک مخصوص رو برای همه دوستانت بفرست\n"
            "و در آخر با هر دعوت پاداش میگیری ❤️"
        )
        await update.message.reply_text(help_guide)

    elif "بازگشت به منو اصلی" in text:
        db[user_id]["step"] = "none"
        save_db(db)
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=get_main_keyboard())

    elif "پنل ادمین" in text and user_id == ADMIN_ID:
        await update.message.reply_text("به پنل مدیریت ربات خوش آمدید، ادمین عزیز. 🛠️", reply_markup=get_admin_keyboard())

    elif "آمار کل ربات" in text and user_id == ADMIN_ID:
        await update.message.reply_text(f"📊 آمار کل ربات شما:\n\n👥 تعداد کل کاربران ثبت‌نام شده: {len(db)} نفر")

    elif "ارسال پیام همگانی" in text and user_id == ADMIN_ID:
        db[ADMIN_ID]["step"] = "broadcasting"
        save_db(db)
        await update.message.reply_text("✍️ لطفاً پیام مورد نظر خود را بفرستید تا به صورت همگانی برای همه ارسال شود:")

# ---------------------------------------------------------
# اجرای اصلی برنامه
# ---------------------------------------------------------
if __name__ == "__main__":
    web_thread = threading.Thread(target=start_health_server, daemon=True)
    web_thread.start()

    print("[Success] Telegram Bot is Starting on Railway...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
