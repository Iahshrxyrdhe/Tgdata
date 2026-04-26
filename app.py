import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. CONFIGURATION ---
# Token ko secure rakhne ke liye Environment Variable use karein (Best Practice)
API_TOKEN = os.environ.get('BOT_TOKEN', '8435434656:AAGxTX5s9EuGI-qWV0Iy8OwyJ97SEa6b8Kw') 
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"
DEVELOPER_ID = "@TFQdeadlox636"
CHANNEL_LINK = "https://t.me/termuxwalee"
DB_LINK = "https://t.me/+MN_TO1H8nmMzNzM1"

bot = telebot.TeleBot(API_TOKEN, threaded=False) # Threaded=False for stability on free servers
app = Flask(__name__)

# --- 2. FORMATTING LOGIC ---
def format_result(res, title="RESULT FOUND"):
    # Pattern Recognition for different keys (user_id vs User_ID etc)
    raw_res = {str(k).lower(): v for k, v in res.items()}
    
    phone = str(raw_res.get('phone', 'N/A')).strip()
    if phone != 'N/A' and not phone.startswith('+'):
        phone = f"+{phone}"

    username = str(raw_res.get('username', 'N/A')).strip()
    if username != 'N/A' and not username.startswith('@'):
        username = f"@{username}"

    name = f"{raw_res.get('first_name', 'N/A')} {raw_res.get('last_name', '')}".strip()
    user_id = str(raw_res.get('user_id', 'N/A'))

    return (
        f"*{title}*\n\n"
        f"NAME: `{name}`\n"
        f"PHONE: {phone}\n"
        f"USER ID: `{user_id}`\n"
        f"USERNAME: {username}"
    )

# --- 3. WEB SERVER ---
@app.route('/')
def health_check():
    return "BOT IS RUNNING", 200

def run_flask():
    # Render PORT handling
    port = int(os.environ.get("PORT", 8080))
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
        "Welcome to OisntBot Made By @TFQdeadlox636",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == "SEARCH ID":
        msg = bot.send_message(chat_id, "ENTER THE ID TO LOOK UP:")
        bot.register_next_step_handler(msg, process_search)

    elif text == "RANDOM":
        temp_msg = bot.send_message(chat_id, "FETCHING DATA...")
        try:
            r = requests.get(f"{BASE_URL}/random", timeout=20)
            data = r.json()
            if data.get("status") == "success":
                # Check if it's 'result' or 'results'
                res_data = data.get("result") or data.get("results")
                resp = format_result(res_data, title="RANDOM DATA")
                bot.send_message(chat_id, resp, parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "DATABASE BUSY")
        except:
            bot.send_message(chat_id, "TIMEOUT")
        bot.delete_message(chat_id, temp_msg.message_id)

    elif text == "RESTART":
        start(message)

    elif text in ["BOT DATABASE", "DEV", "CHANNEL"]:
        if text == "BOT DATABASE":
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("ACCESS", url=DB_LINK))
            bot.send_message(chat_id, "CLICK BELOW TO JOIN:", reply_markup=markup)
        elif text == "DEV":
            bot.send_message(chat_id, f"DEVELOPER: `{DEVELOPER_ID}`", parse_mode="Markdown")
        else:
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("JOIN", url=CHANNEL_LINK))
            bot.send_message(chat_id, "STAY UPDATED:", reply_markup=markup)

def process_search(message):
    uid = message.text.strip()
    chat_id = message.chat.id
    
    if not uid.isdigit():
        bot.send_message(chat_id, "ONLY TG ID IS ALLOWED")
        return

    search_msg = bot.send_message(chat_id, f"SEARCHING: {uid}...")
    
    try:
        # Note: API use 'id' or 'uid'? Check your Flask API. Defaulting to 'id'
        r = requests.get(f"{BASE_URL}/search?id={uid}", timeout=25)
        data = r.json()
        if data.get("status") == "success":
            res_data = data.get("result") or data.get("results")
            resp = format_result(res_data)
            bot.send_message(chat_id, resp, parse_mode="Markdown")
            bot.delete_message(chat_id, search_msg.message_id)
        else:
            bot.edit_message_text(f"'{uid}' IS NOT IN DATABASE", chat_id, search_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"CONNECTION ERROR", chat_id, search_msg.message_id)

# --- 6. STARTUP ---
if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Fix 409 and start bot
    try:
        bot.delete_webhook(drop_pending_updates=True)
        print("Bot is active!")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Error: {e}")
