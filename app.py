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
def format_result(res, title="RESULT FOUND"):
    # Pattern Recognition for different keys
    raw = {str(k).lower(): v for k, v in res.items()}
    
    phone = str(raw.get('phone', 'N/A')).strip()
    if phone != 'N/A' and not phone.startswith('+'):
        phone = f"+{phone}"

    username = str(raw.get('username', 'N/A')).strip()
    if username != 'N/A' and not username.startswith('@'):
        username = f"@{username}"

    name = f"{raw.get('first_name', 'N/A')} {raw.get('last_name', '')}".strip()
    user_id = str(raw.get('user_id', 'N/A'))

    return (
        f"*{title}*\n\n"
        f"NAME: `{name}`\n"
        f"PHONE: {phone}\n"
        f"USER ID: `{user_id}`\n"
        f"USERNAME: {username}"
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
        "Your Welcome In OisntBot Made By @TFQdeadlox636",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    if message.text == "SEARCH ID":
        msg = bot.send_message(chat_id, "ENTER THE ID TO LOOK UP:")
        bot.register_next_step_handler(msg, process_search)

    elif message.text == "RANDOM":
        temp_msg = bot.send_message(chat_id, "🎲 FETCHING RANDOM DATA...")
        try:
            # Random API Call
            r = requests.get(f"{BASE_URL}/random", timeout=60)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    # Supporting both 'result' or 'results' key
                    res_data = data.get("results") or data.get("result")
                    resp = format_result(res_data, title="RANDOM DATA")
                    bot.send_message(chat_id, resp, parse_mode="Markdown")
                    bot.delete_message(chat_id, temp_msg.message_id)
                else:
                    bot.edit_message_text("DATABASE BUSY", chat_id, temp_msg.message_id)
            else:
                bot.edit_message_text(f"API ERROR: {r.status_code}", chat_id, temp_msg.message_id)
        except Exception as e:
            bot.edit_message_text("TIMEOUT: API is waking up, try again in 10s", chat_id, temp_msg.message_id)

    elif message.text == "RESTART":
        start(message)

    elif message.text == "BOT DATABASE":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("ACCESS DATABASE", url=DB_LINK))
        bot.send_message(chat_id, "CLICK BELOW TO JOIN:", reply_markup=markup)

    elif message.text == "DEV":
        bot.send_message(chat_id, f"DEVELOPER: `{DEVELOPER_ID}`", parse_mode="Markdown")

    elif message.text == "CHANNEL":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("JOIN NOW", url=CHANNEL_LINK))
        bot.send_message(chat_id, "STAY UPDATED:", reply_markup=markup)

def process_search(message):
    uid = message.text.strip()
    chat_id = message.chat.id
    
    if not uid.isdigit():
        bot.send_message(chat_id, "ONLY TG ID NEED TO ENTER FOR INFO")
        return

    search_msg = bot.send_message(chat_id, f"🔍 SEARCHING: {uid}")
    
    try:
        # Search API Call with id=
        r = requests.get(f"{BASE_URL}/search?id={uid}", timeout=60)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                res_data = data.get("results") or data.get("result")
                resp = format_result(res_data)
                bot.send_message(chat_id, resp, parse_mode="Markdown")
                bot.delete_message(chat_id, search_msg.message_id)
            else:
                bot.edit_message_text(f"'{uid}' IS NOT IN DATABASE", chat_id, search_msg.message_id)
        else:
            bot.edit_message_text(f"API ERROR ({r.status_code})", chat_id, search_msg.message_id)
    except:
        bot.edit_message_text("CONNECTION FAILED / TIMEOUT", chat_id, search_msg.message_id)

# --- 6. STARTUP ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    # 409 Conflict Fix
    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(1)
    except:
        pass

    print("Bot is active!")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
