import os
import telebot
import requests
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. CONFIGURATION ---
API_TOKEN = '8435434656:AAH4FzsCtgUw4V9PXnj5GN_HJbdA659Df2s'  # BotFather wala token
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"
DEVELOPER_ID = "@TFQdeadlox636"
CHANNEL_LINK = "https://t.me/termuxwalee"

# --- 2. FLASK SERVER (For Render Port Binding) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Active!", 200

def run_flask():
    # Render automatically sets the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    print(f"📡 Flask is binding to port {port}")
    app.run(host='0.0.0.0', port=port)

# --- 3. BOT LOGIC ---
bot = telebot.TeleBot(API_TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Search ID")
    btn2 = types.KeyboardButton("🎲 Random Search")
    btn3 = types.KeyboardButton("👨‍💻 Developer")
    btn4 = types.KeyboardButton("📢 Channel")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "🔥 **System Online!**\n\nNiche diye gaye buttons se database search karein.",
        parse_mode="Markdown", 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🔍 Search ID":
        msg = bot.send_message(chat_id, "🆔 **Enter User ID to search:**")
        bot.register_next_step_handler(msg, process_search)

    elif text == "🎲 Random Search":
        bot.send_message(chat_id, "⏳ Picking a random record...")
        try:
            r = requests.get(f"{BASE_URL}/random", timeout=20)
            data = r.json()
            if data.get("status") == "success":
                res = data["result"]
                resp = (f"🎲 **Random Result:**\n\n"
                        f"👤 Name: {res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}\n"
                        f"📞 Phone: {res.get('Phone', 'N/A')}\n"
                        f"🆔 ID: {res.get('User_ID', 'N/A')}\n"
                        f"🌐 User: @{res.get('Username', 'N/A')}")
                bot.send_message(chat_id, resp, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "⚠️ API Server is waking up. Try again in 10 seconds.")

    elif text == "👨‍💻 Developer":
        bot.send_message(chat_id, f"👨‍💻 **Developer:** {DEVELOPER_ID}")

    elif text == "📢 Channel":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Now 🚀", url=CHANNEL_LINK))
        bot.send_message(chat_id, "📢 **Join @termuxwalee:**", reply_markup=markup, parse_mode="Markdown")

def process_search(message):
    uid = message.text.strip()
    if not uid.isdigit():
        bot.send_message(message.chat.id, "❌ Valid Number bhejein.")
        return

    bot.send_message(message.chat.id, f"🔎 Searching `{uid}`...")
    try:
        r = requests.get(f"{BASE_URL}/search?uid={uid}", timeout=20)
        data = r.json()
        if data.get("status") == "success":
            res = data["result"]
            resp = (f"✅ **Found!**\n\n"
                    f"👤 Name: {res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}\n"
                    f"📞 Phone: {res.get('Phone', 'N/A')}\n"
                    f"🆔 ID: {res.get('User_ID', 'N/A')}\n"
                    f"🌐 User: @{res.get('Username', 'N/A')}")
            bot.send_message(message.chat.id, resp, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Not Found.")
    except:
        bot.send_message(message.chat.id, "⚠️ Connection Error.")

# --- 4. STARTUP ---
if __name__ == '__main__':
    # Start Flask in background
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("🤖 Bot is starting...")
    # Use infinity_polling to keep it alive
    bot.infinity_polling()
