import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. CONFIGURATION ---
# @BotFather se naya token lekar yahan daalein (Zaroori hai)
API_TOKEN = '8435434656:AAH4FzsCtgUw4V9PXnj5GN_HJbdA659Df2s' 
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"
DEVELOPER_ID = "@TFQdeadlox636"
CHANNEL_LINK = "https://t.me/termuxwalee"
DB_LINK = "https://t.me/+MN_TO1H8nmMzNzM1"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- 2. FORMATTING LOGIC ---
def format_result(res, title="💠 *RESULT FOUND*"):
    # Phone number (+ prefix, no copy)
    raw_phone = str(res.get('Phone', 'N/A')).strip()
    if raw_phone != 'N/A' and not raw_phone.startswith('+'):
        phone = f"\\+{raw_phone}"
    else:
        phone = raw_phone.replace('+', '\\+')

    # Username (@ prefix, no copy)
    raw_user = str(res.get('Username', 'N/A')).strip()
    if raw_user != 'N/A' and not raw_user.startswith('@'):
        username = f"@{raw_user}".replace('_', '\\_')
    else:
        username = raw_user.replace('_', '\\_')

    # Clickable data (Name & ID only)
    name = f"{res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}".replace('-', '\\-').replace('.', '\\.')
    user_id = str(res.get('User_ID', 'N/A')).replace('-', '\\-')

    response = (
        f"{title}\n\n"
        f"👤 *Name:* `{name}`\n"
        f"📞 *Phone:* {phone}\n"
        f"🆔 *User ID:* `{user_id}`\n"
        f"🌐 *Username:* {username}\n\n"
        f"🛠️ *Powered by @termuxwalee*"
    )
    return response

# --- 3. WEB SERVER FOR RENDER ---
@app.route('/')
def health_check():
    return "Bot Status: Running", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 4. KEYBOARD ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Search ID")
    btn2 = types.KeyboardButton("🎯 Random")
    btn3 = types.KeyboardButton("📊 Bot Database")
    btn4 = types.KeyboardButton("👑 Dev")
    btn5 = types.KeyboardButton("📡 Channel")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# --- 5. HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "👋 *Welcome\\!*\n\nSelect an option to start searching\\.",
        parse_mode="MarkdownV2", 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    if message.text == "🚀 Search ID":
        msg = bot.send_message(chat_id, "⌨️ *Enter the ID:*", parse_mode="MarkdownV2")
        bot.register_next_step_handler(msg, process_search)

    elif message.text == "🎯 Random":
        temp_msg = bot.send_message(chat_id, "🌀 *Fetching random data...*", parse_mode="MarkdownV2")
        try:
            r = requests.get(f"{BASE_URL}/random", timeout=20)
            data = r.json()
            if data.get("status") == "success":
                resp = format_result(data["result"], title="🎯 *RANDOM DATA*")
                bot.send_message(chat_id, resp, parse_mode="MarkdownV2")
                bot.delete_message(chat_id, temp_msg.message_id)
        except:
            bot.edit_message_text("❌ *Server Timeout\\!*", chat_id, temp_msg.message_id, parse_mode="MarkdownV2")

    elif message.text == "📊 Bot Database":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Access Database 📂", url=DB_LINK))
        bot.send_message(chat_id, "📊 *Click below to join:*", reply_markup=markup, parse_mode="MarkdownV2")

    elif message.text == "👑 Dev":
        bot.send_message(chat_id, f"👑 *Developer:* `{DEVELOPER_ID}`", parse_mode="MarkdownV2")

    elif message.text == "📡 Channel":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("JOIN NOW ⚡", url=CHANNEL_LINK))
        bot.send_message(chat_id, "📢 *Stay updated:*", reply_markup=markup, parse_mode="MarkdownV2")

def process_search(message):
    uid = message.text.strip()
    chat_id = message.chat.id
    
    if not uid.isdigit():
        bot.send_message(chat_id, "⚠️ *Numeric ID only\\!*", parse_mode="MarkdownV2")
        return

    search_msg = bot.send_message(chat_id, f"🔍 *Searching:* `{uid}`", parse_mode="MarkdownV2")
    
    try:
        r = requests.get(f"{BASE_URL}/search?uid={uid}", timeout=20)
        data = r.json()
        if data.get("status") == "success":
            resp = format_result(data["result"])
            bot.send_message(chat_id, resp, parse_mode="MarkdownV2")
            bot.delete_message(chat_id, search_msg.message_id)
        else:
            bot.edit_message_text(f"❌ *ID `{uid}` not found\\.*", chat_id, search_msg.message_id, parse_mode="MarkdownV2")
    except:
        bot.edit_message_text("⚠️ *API Error\\!*", chat_id, search_msg.message_id, parse_mode="MarkdownV2")

# --- 6. STARTUP LOGIC (Fixed for TypeError) ---
if __name__ == '__main__':
    # Start Flask thread
    Thread(target=run_flask, daemon=True).start()
    
    print("🧹 Cleaning old sessions...")
    try:
        bot.remove_webhook()
        # Manually clear pending updates to avoid 409 Conflict
        bot.get_updates(offset=-1)
        time.sleep(1)
    except Exception as e:
        print(f"Cleanup error: {e}")

    print("🤖 Bot is active and ready!")
    # Infinity polling without the problematic skip_pending_updates argument
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
