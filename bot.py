from flask import Flask
import threading
import telebot
from telebot import types

# --- تنظیمات ---
API_TOKEN = '8975437459:AAEAKWcbIGu16xfTnfpmJuAr5MBGF2BZvM8'
ADMIN_ID = 2083289229       # آیدی عددی خودت
REVIEWER_ID = 6912730774    # آیدی عددی بررسی‌کننده

bot = telebot.TeleBot(API_TOKEN)

# --- وب سرور برای بیدار موندن ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# --- دریافت ویدیو ---
@bot.message_handler(content_types=['video'])
def handle_video(message):
    # پیدا کردن اطلاعات فرستنده اصلی
    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    username = message.from_user.username

    # اگر ویدیو فوروارد شده باشه
    if message.forward_from:
        user_id = message.forward_from.id
        first_name = message.forward_from.first_name or ""
        username = message.forward_from.username

    # ساخت متن آیدی
    if username:
        user_info = f"@{username}"
    else:
        user_info = f"[{first_name}](tg://user?id={user_id})"

    # ساخت دکمه‌ها
    markup = types.InlineKeyboardMarkup()
    btn_ok = types.InlineKeyboardButton('✅ تایید', callback_data=f'ok_{user_id}_{username or "none"}_{first_name}')
    btn_no = types.InlineKeyboardButton('❌ رد', callback_data=f'no_{user_id}_{username or "none"}_{first_name}')
    markup.add(btn_ok, btn_no)

    # ارسال برای بررسی‌کننده
    caption = (
        f"🎥 ویدیو جدید\n\n"
        f"👤 فرستنده: {user_info}\n"
        f"🆔 آیدی عددی: `{user_id}`"
    )

    bot.send_video(
        REVIEWER_ID,
        message.video.file_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )

    bot.reply_to(message, "✅ ویدیو شما برای بررسی ارسال شد.")

# --- پردازش دکمه تایید یا رد ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    parts = call.data.split('_', 3)
    action = parts[0]
    user_id = parts[1]
    username = parts[2]
    first_name = parts[3] if len(parts) > 3 else ""

    # ساخت لینک قابل کلیک برای ادمین
    if username != "none":
        user_link = f"@{username}"
    else:
        user_link = f"[{first_name}](tg://user?id={user_id})"

    if action == "ok":
        # ارسال نتیجه برای ادمین
        bot.send_message(
            ADMIN_ID,
            f"✅ *تایید شد*\n\n"
            f"👤 فرستنده: {user_link}\n"
            f"🆔 آیدی: `{user_id}`",
            parse_mode="Markdown"
        )

        # ارسال خود ویدیو هم برای ادمین
        bot.send_video(ADMIN_ID, call.message.video.file_id)

        bot.answer_callback_query(call.id, "✅ تایید شد")
        bot.edit_message_caption(
            "✅ این ویدیو تایید شد",
            call.message.chat.id,
            call.message.message_id
        )

    elif action == "no":
        bot.send_message(
            ADMIN_ID,
            f"❌ *رد شد*\n\n"
            f"👤 فرستنده: {user_link}\n"
            f"🆔 آیدی: `{user_id}`",
            parse_mode="Markdown"
        )

        bot.answer_callback_query(call.id, "❌ رد شد")
        bot.edit_message_caption(
            "❌ این ویدیو رد شد",
            call.message.chat.id,
            call.message.message_id
        )

bot.infinity_polling()
