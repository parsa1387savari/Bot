import telebot
from telebot import types

# --- تنظیمات اصلی ---
API_TOKEN = '8141425282:AAEq3AcFGewC59Xt95TxHswwmqNfh9gpqs8'
ADMIN_ID = 2083289229  # آیدی عددی خودت
REVIEWER_ID = 6912730774  # آیدی عددی کسی که باید تایید کنه

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    # پیدا کردن آیدی فرستنده اصلی (حتی اگر فوروارد شده باشه)
    user_id = message.from_user.id
    username = message.from_user.username or "نامشخص"
    
    if message.forward_from:
        user_id = message.forward_from.id
        username = message.forward_from.username or "نامشخص"
    elif message.forward_origin and hasattr(message.forward_origin, 'sender_user'):
        user_id = message.forward_origin.sender_user.id
        username = message.forward_origin.sender_user.username or "نامشخص"

    # ساخت دکمه برای Reviewer
    markup = types.InlineKeyboardMarkup()
    item_ok = types.InlineKeyboardButton('✅ تایید', callback_data=f'ok_{user_id}')
    item_no = types.InlineKeyboardButton('❌ رد', callback_data=f'no_{user_id}')
    markup.add(item_ok, item_no)

    # ارسال ویدیو برای Reviewer
    caption = f"🎥 ویدیو جدید\n👤 فرستنده: @{username}\n🆔 آیدی عددی: {user_id}"
    bot.send_video(REVIEWER_ID, message.video.file_id, caption=caption, reply_markup=markup)
    bot.reply_to(message, "✅ ویدیو شما برای بررسی ارسال شد.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    action, user_id = call.data.split('_')
    
    if action == "ok":
        bot.send_message(ADMIN_ID, f"✅ ویدیو کاربر {user_id} توسط بررسی‌کننده تایید شد.")
        bot.answer_callback_query(call.id, "تایید شد")
        bot.edit_message_caption("✅ این ویدیو تایید شد", call.message.chat.id, call.message.message_id)
    
    elif action == "no":
        bot.send_message(ADMIN_ID, f"❌ ویدیو کاربر {user_id} رد شد.")
        bot.answer_callback_query(call.id, "رد شد")
        bot.edit_message_caption("❌ این ویدیو رد شد", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
