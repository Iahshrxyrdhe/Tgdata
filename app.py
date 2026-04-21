import telebot
import requests
import os
import random
from flask import Flask
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# --- CONFIG ---
BOT_TOKEN = "8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI" # Apna sahi token dalo
API_URL = "https://tfqdeadlo-tgdatabase.hf.space/search"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!", 200

# --- REPLY KEYBOARD SETUP ---
def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Buttons ko keyboard layout mein set karna
    btn1 = KeyboardButton("🔍 Search Info")
    btn2 = KeyboardButton("🎲 Random Search")
    btn3 = KeyboardButton("👨‍💻 Developer")
    btn4 = KeyboardButton("📢 Channel")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "<b>🤖 Premium Search Bot Active!</b>\n\n"
        "Niche diye gaye keyboard buttons ka use karein ya direct ID bhejein."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_keyboard())

# --- SMART RANDOM SEARCH LOGIC ---
def get_random_user(message):
    status_msg = bot.send_message(message.chat.id, "🎲 <i>Searching valid random user...</i>", parse_mode="HTML")
    found = False
    max_attempts = 15 # Zyada koshish karega data dhoondne ki

    for _ in range(max_attempts):
        # Range ko apne database ke size ke mutabiq set karein
        random_id = str(random.randint(1, 2000)) 
        try:
            r = requests.get(f"{API_URL}?user_id={random_id}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if results:
                    res = results[0]
                    response_text = (
                        "<b>🎲 Random Result Found!</b>\n"
                        "──────────────────\n"
                        f"👤 <b>Name:</b> <code>{res.get('First_Name', 'N/A')}</code>\n"
                        f"📞 <b>Phone:</b> <code>{res.get('Phone_Number', 'N/A')}</code>\n"
                        f"🆔 <b>User ID:</b> <code>{res.get('User_ID', 'N/A')}</code>\n"
                        "──────────────────\n"
                        "<b>Powered By:</b> @TFQdeadlox636"
                    )
                    bot.edit_message_text(response_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
                    found = True
                    break
        except:
            continue

    if not found:
        bot.edit_message_text("❌ <b>Random Search Failed!</b>\nDatabase se koi valid random row nahi mili. Dobara click karein.", message.chat.id, status_msg.message_id, parse_mode="HTML")

# --- ACTUAL SEARCH FUNCTION ---
def perform_search(message, user_id):
    status_msg = bot.send_message(message.chat.id, "⏳ <i>Searching Database...</i>", parse_mode="HTML")
    try:
        r = requests.get(f"{API_URL}?user_id={user_id}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                res = results[0]
                response_text = (
                    "<b>✅ Result Found!</b>\n"
                    "──────────────────\n"
                    f"👤 <b>Name:</b> <code>{res.get('First_Name', 'N/A')}</code>\n"
                    f"📞 <b>Phone:</b> <code>{res.get('Phone_Number', 'N/A')}</code>\n"
                    f"🆔 <b>User ID:</b> <code>{res.get('User_ID', 'N/A')}</code>\n"
                    "──────────────────\n"
                    "<b>Powered By:</b> @TFQdeadlox636"
                )
                bot.edit_message_text(response_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            else:
                bot.edit_message_text("❌ <b>Not found in database!</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("❌ <b>Not found in database!</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
    except:
        bot.edit_message_text("❌ <b>Not found in database!</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# --- KEYBOARD TEXT HANDLER ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text

    if text == "🔍 Search Info":
        bot.send_message(message.chat.id, "🔍 <b>ID Bhejo:</b>\nSirf User ID type karke send karo.", parse_mode="HTML")
    
    elif text == "🎲 Random Search":
        Thread(target=get_random_user, args=(message,)).start()
        
    elif text == "👨‍💻 Developer":
        bot.send_message(message.chat.id, "👨‍💻 <b>Developer:</b> @TFQdeadlox636", parse_mode="HTML")
        
    elif text == "📢 Channel":
        bot.send_message(message.chat.id, "📢 <b>Official Channel:</b> @termuxwalee", parse_mode="HTML")
        
    elif text.isdigit():
        perform_search(message, text.strip())
    else:
        bot.reply_to(message, "⚠️ <b>Error:</b> Please use buttons or send a valid ID.", parse_mode="HTML")

# --- SERVER RUN ---
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
