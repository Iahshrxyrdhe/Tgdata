import os
import telebot
import requests
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. CONFIGURATION ---
API_TOKEN = '8435434656:AAH4FzsCtgUw4V9PXnj5GN_HJbdA659Df2s' 
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"
DEVELOPER_ID = "@TFQdeadlox636"
CHANNEL_LINK = "https://t.me/termuxwalee"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- 2. FORMATTING LOGIC (Click-to-Copy & +Phone) ---
def format_result(res, title="✅ *Record Found\\!*"):
    """Data ko clickable aur +phone ke saath format karta hai"""
    
    # Phone number formatting (+ add karna)
    raw_phone = str(res.get('Phone', 'N/A')).strip()
    if raw_phone != 'N/A' and not raw_phone.startswith('+'):
        phone = f"\\+{raw_phone}"
    else:
        phone = raw_phone.replace('+', '\\+') # Special char escape for MarkdownV2

    # MarkdownV2 mein special characters escape karne hote hain
    name = f"{res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}".replace('-', '\\-').replace('.', '\\.')
    user_id = str(res.get('User_ID', 'N/A')).replace('-', '\\-')
    username = str(res.get('Username', 'N/A')).replace('_', '\\_').replace('*', '\\*')

    # Response layout (Backticks `` make it clickable to copy)
    response = (
        f"{title}\n\n"
        f"👤 Name: `{name}`\n"
        f"📞 Phone: `{phone}`\n"
        f"🆔 ID: `{user_id}`\n"
        f"🌐 User: `@{username}`\n\n"
        f"💡 *Detail par click karke copy karein*"
    )
    return response

# --- 3. WEB SERVER FOR RENDER ---
@app.route('/')
def health_check():
    return "Bot is Running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 4. KEYBOARD ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Search ID")
    btn2 = types.KeyboardButton("🎲 Random Search")
    btn3 = types.KeyboardButton("👨‍💻 Developer")
    btn4 = types.KeyboardButton("📢 Channel")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# --- 5. HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "🔥 *System Online\\!*\n\nNiche diye gaye buttons ka use karein\\.",
        parse_mode="MarkdownV2", 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    if message.text == "🔍 Search ID":
        msg = bot.send_message(chat_id, "🆔 *Enter User ID to search:*", parse_mode="MarkdownV2")
        bot.register_next_step_handler(msg, process_search)

    elif message.text == "🎲 Random Search":
        bot.send_message(chat_id, "⏳ Fetching random record...")
        try:
            r = requests.get(f"{BASE_URL}/random", timeout=20)
            data = r.json()
            if data.get("status") == "success":
                resp = format_result(data["result"], title="🎲 *Random Result:*")
                bot.send_message(chat_id, resp, parse_mode="MarkdownV2")
        except:
            bot.send_message(chat_id, "⚠️ Server Error. Try again.")

    elif message.text == "👨‍💻 Developer":
        bot.send_message(chat_id, f"👨‍💻 *Developer:* `{DEVELOPER_ID}`", parse_mode="MarkdownV2")

    elif message.text == "📢 Channel":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel 🚀", url=CHANNEL_LINK))
        bot.send_message(chat_id, "📢 *Updates ke liye join karein:*", reply_markup=markup, parse_mode="MarkdownV2")

def process_search(message):
    uid = message.text.strip()
    if not uid.isdigit():
        bot.send_message(message.chat.id, "❌ Valid Number bhejein\\.")
        return

    bot.send_message(message.chat.id, f"🔎 Searching `{uid}`\\.\\.\\.", parse_mode="MarkdownV2")
    try:
        r = requests.get(f"{BASE_URL}/search?uid={uid}", timeout=20)
        data = r.json()
        if data.get("status") == "success":
            resp = format_result(data["result"])
            bot.send_message(message.chat.id, resp, parse_mode="MarkdownV2")
        else:
            bot.send_message(message.chat.id, "❌ Not Found\\.")
    except:
        bot.send_message(message.chat.id, "⚠️ Connection Error\\.")

# --- 6. STARTUP ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    print("🤖 Bot is starting...")
    bot.infinity_polling()
