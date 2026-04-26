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

# --- 2. FORMATTING LOGIC (Minimal & Clean) ---
def format_result(res, title="RESULT FOUND"):
    # Phone number (+ prefix only)
    raw_phone = str(res.get('Phone', 'N/A')).strip()
    if raw_phone != 'N/A' and not raw_phone.startswith('+'):
        phone = f"+{raw_phone}"
    else:
        phone = raw_phone

    # Username (@ prefix only)
    raw_user = str(res.get('Username', 'N/A')).strip()
    if raw_user != 'N/A' and not raw_user.startswith('@'):
        username = f"@{raw_user}"
    else:
        username = raw_user

    # Name & ID (Clickable)
    name = f"{res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}"
    user_id = str(res.get('User_ID', 'N/A'))

    # Result Only (No extra text/powered by)
    response = (
        f"*{title}*\n\n"
        f"NAME: `{name}`\n"
        f"PHONE: {phone}\n"
        f"USER ID: `{user_id}`\n"
        f"USERNAME: {username}"
    )
    return response

# --- 3. WEB SERVER FOR RENDER ---
@app.route('/')
def health_check():
    return "ONLINE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 4. KEYBOARD (CAPITAL LETTERS & NO SYMBOLS) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("SEARCH ID")
    btn2 = types.KeyboardButton("RANDOM")
    btn3 = types.KeyboardButton("BOT DATABASE")
    btn4 = types.KeyboardButton("DEV")
    btn5 = types.KeyboardButton("CHANNEL")
    btn6 = types.KeyboardButton("RESTART")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
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
        temp_msg = bot.send_message(chat_id, "FETCHING DATA...")
        try:
            r = requests.get(f"{BASE_URL}/random", timeout=30)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    resp = format_result(data["result"], title="RANDOM DATA")
                    bot.send_message(chat_id, resp, parse_mode="Markdown")
                    bot.delete_message(chat_id, temp_msg.message_id)
                else:
                    bot.edit_message_text("DATABASE BUSY", chat_id, temp_msg.message_id)
        except:
            bot.edit_message_text("TIMEOUT", chat_id, temp_msg.message_id)

    elif message.text == "RESTART":
        start(message)

    elif message.text == "BOT DATABASE":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ACCESS DATABASE", url=DB_LINK))
        bot.send_message(chat_id, "CLICK BELOW TO JOIN:", reply_markup=markup)

    elif message.text == "DEV":
        bot.send_message(chat_id, f"DEVELOPER: `{DEVELOPER_ID}`", parse_mode="Markdown")

    elif message.text == "CHANNEL":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("JOIN NOW", url=CHANNEL_LINK))
        bot.send_message(chat_id, "STAY UPDATED:", reply_markup=markup)

def process_search(message):
    uid = message.text.strip()
    chat_id = message.chat.id
    
    if not uid.isdigit():
        bot.send_message(chat_id, "ONLY TG ID NEED TO ENTER FOR INFO")
        return

    search_msg = bot.send_message(chat_id, f"SEARCHING: {uid}")
    
    try:
        r = requests.get(f"{BASE_URL}/search?uid={uid}", timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                resp = format_result(data["result"])
                bot.send_message(chat_id, resp, parse_mode="Markdown")
                bot.delete_message(chat_id, search_msg.message_id)
            else:
                # Custom Not Found message as requested
                bot.edit_message_text(f"'{uid}' IS NOT IN DATABASE", chat_id, search_msg.message_id)
        else:
            bot.edit_message_text("API ERROR", chat_id, search_msg.message_id)
    except:
        bot.edit_message_text("CONNECTION FAILED", chat_id, search_msg.message_id)

# --- 6. STARTUP LOGIC (CLEAN 409 FIX) ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    print("Flushing old sessions...")
    try:
        # 409 Conflict Fix: Delete webhook and drop all pending messages
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except:
        pass

    print("Bot is active!")
    bot.infinity_polling()
