import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. CONFIGURATION ---
API_TOKEN = '8435434656:AAGTLSsmkRxsCi_Xil-C5o6w9d_I0IIUSLc' 
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"
DEVELOPER_ID = "@TFQdeadlox636"
CHANNEL_LINK = "https://t.me/termuxwalee"
DB_LINK = "https://t.me/+MN_TO1H8nmMzNzM1"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- 2. FORMATTING LOGIC ---
def format_result(res, title="🔍 RESULT FOUND"):
    # API ke response se data nikalna
    phone = str(res.get('phone', 'N/A')).strip()
    if phone != 'N/A' and phone != "" and not phone.startswith('+'):
        phone = f"+{phone}"

    username = str(res.get('username', 'N/A')).strip()
    if username != 'N/A' and username != "" and not username.startswith('@'):
        username = f"@{username}"

    first_name = res.get('first_name', '')
    last_name = res.get('last_name', '')
    name = f"{first_name} {last_name}".strip() or "N/A"
    
    user_id = str(res.get('user_id', 'N/A'))
    status = res.get('status', 'N/A')

    return (
        f"*{title}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 **NAME:** `{name}`\n"
        f"📞 **PHONE:** `{phone}`\n"
        f"🆔 **USER ID:** `{user_id}`\n"
        f"🌐 **USERNAME:** {username}\n"
        f"📝 **STATUS:** `{status}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Powered By @TFQdeadlox636"
    )

# --- 3. WEB SERVER FOR RENDER ---
@app.route('/')
def health_check():
    return "BOT ONLINE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 4. KEYBOARD ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("SEARCH ID", "RANDOM", "BOT DATABASE", "DEV", "CHANNEL", "RESTART")
    return markup

# --- 5. HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "🚀 **Welcome to OsintBot!**\n\nSearch 429 Million+ Telegram Records in seconds.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    if message.text == "SEARCH ID":
        msg = bot.send_message(chat_id, "⌨️ **ENTER THE TELEGRAM ID TO LOOK UP:**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_search)

    elif message.text == "RANDOM":
        temp_msg = bot.send_message(chat_id, "🎲 **FETCHING RANDOM DATA...**", parse_mode="Markdown")
        try:
            # Random API Call (Sahi endpoint)
            r = requests.get(f"{BASE_URL}/random", timeout=30)
            if r.status_code == 200:
                data = r.json()
                if data.get("found") == True:
                    res_data = data.get("data")
                    resp = format_result(res_data, title="🎲 RANDOM DATA")
                    bot.send_message(chat_id, resp, parse_mode="Markdown")
                    bot.delete_message(chat_id, temp_msg.message_id)
                else:
                    bot.edit_message_text("❌ Database is busy, try again.", chat_id, temp_msg.message_id)
            else:
                bot.edit_message_text(f"⚠️ API Error: {r.status_code}", chat_id, temp_msg.message_id)
        except Exception as e:
            bot.edit_message_text("🕒 Timeout: API is waking up, try in 10s", chat_id, temp_msg.message_id)

    elif message.text == "RESTART":
        start(message)

    elif message.text == "BOT DATABASE":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("ACCESS DATABASE", url=DB_LINK))
        bot.send_message(chat_id, "📂 **CLICK BELOW TO JOIN OUR DATABASE:**", reply_markup=markup, parse_mode="Markdown")

    elif message.text == "DEV":
        bot.send_message(chat_id, f"👨‍💻 **DEVELOPER:** {DEVELOPER_ID}", parse_mode="Markdown")

    elif message.text == "CHANNEL":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("JOIN NOW", url=CHANNEL_LINK))
        bot.send_message(chat_id, "📢 **STAY UPDATED:**", reply_markup=markup, parse_mode="Markdown")

def process_search(message):
    uid = message.text.strip()
    chat_id = message.chat.id
    
    if not uid.isdigit():
        bot.send_message(chat_id, "❌ **Error:** Please enter a numeric Telegram ID only.")
        return

    search_msg = bot.send_message(chat_id, f"🔍 **SEARCHING:** `{uid}`...", parse_mode="Markdown")
    
    try:
        # Search API Call (Sahi URL path format)
        r = requests.get(f"{BASE_URL}/search/{uid}", timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data.get("found") == True:
                res_data = data.get("data")
                resp = format_result(res_data)
                bot.send_message(chat_id, resp, parse_mode="Markdown")
                bot.delete_message(chat_id, search_msg.message_id)
            else:
                bot.edit_message_text(f"❌ ID `{uid}` not found in our database.", chat_id, search_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"⚠️ API ERROR ({r.status_code})", chat_id, search_msg.message_id)
    except Exception as e:
        bot.edit_message_text("🔌 Connection failed. Please try again.", chat_id, search_msg.message_id)

# --- 6. STARTUP ---
if __name__ == '__main__':
    # Start Flask in a separate thread
    Thread(target=run_flask, daemon=True).start()
    
    # Fix Conflict
    try:
        bot.remove_webhook()
        time.sleep(1)
    except:
        pass

    print("🚀 Bot is active and ready to search!")
    bot.infinity_polling(skip_pending=True)
