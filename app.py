import telebot
import requests
import os
import random
import time
from flask import Flask
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# --- CONFIG ---
BOT_TOKEN = "8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI" # Apna Token Check Kar Lena
API_URL = "https://tfqdeadlo-tgdatabase.hf.space/search"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!", 200

# --- KEYBOARD ---
def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 Search Info"), KeyboardButton("🎲 Random Search"))
    markup.add(KeyboardButton("👨‍💻 Developer"), KeyboardButton("📢 Channel"))
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "<b>🤖 Premium Search Bot Active!</b>\n\n"
        "Niche diye gaye buttons ka use karein ya direct ID bhejein."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_keyboard())

# --- SMART RANDOM SEARCH (No More Fails) ---
def get_random_user(message):
    status_msg = bot.send_message(message.chat.id, "🎲 <i>Searching for any valid user...</i>", parse_mode="HTML")
    
    found = False
    attempts = 0
    # Hum 20 baar koshish karenge alag-alag random IDs par
    while not found and attempts < 20:
        attempts += 1
        # Yahan range wo rakhna jo tere database mein IDs ki hai (e.g. 1 to 5000)
        test_id = str(random.randint(1, 5000)) 
        try:
            r = requests.get(f"{API_URL}?user_id={test_id}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("results"):
                    res = data["results"][0]
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
        bot.edit_message_text("❌ <b>Random Search Failed!</b>\nDatabase mein koi valid entry nahi mili. Range check karein ya dobara click karein.", message.chat.id, status_msg.message_id, parse_mode="HTML")

# --- MAIN SEARCH ---
def perform_search(message, user_id):
    status_msg = bot.send_message(message.chat.id, "⏳ <i>Searching...</i>", parse_mode="HTML")
    try:
        r = requests.get(f"{API_URL}?user_id={user_id}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                res = results[0]
                text = (
                    "<b>✅ Result Found!</b>\n"
                    "──────────────────\n"
                    f"👤 <b>Name:</b> <code>{res.get('First_Name', 'N/A')}</code>\n"
                    f"📞 <b>Phone:</b> <code>{res.get('Phone_Number', 'N/A')}</code>\n"
                    f"🆔 <b>User ID:</b> <code>{res.get('User_ID', 'N/A')}</code>\n"
                    "──────────────────\n"
                    "<b>Powered By:</b> @TFQdeadlox636"
                )
                bot.edit_message_text(text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            else:
                bot.edit_message_text("❌ <b>Not found in database!</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text("❌ <b>Not found in database!</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")
    except:
        bot.edit_message_text("❌ <b>Not found in database!</b>", message.chat.id, status_msg.message_id, parse_mode="HTML")

# --- HANDLER ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    txt = message.text
    if txt == "🔍 Search Info":
        bot.send_message(message.chat.id, "🔍 <b>ID Bhejo:</b>\nBas number type karke send karo.", parse_mode="HTML")
    elif txt == "🎲 Random Search":
        Thread(target=get_random_user, args=(message,)).start()
    elif txt == "👨‍💻 Developer":
        bot.send_message(message.chat.id, "👨‍💻 <b>Developer:</b> @TFQdeadlox636", parse_mode="HTML")
    elif txt == "📢 Channel":
        bot.send_message(message.chat.id, "📢 <b>Channel:</b> @termuxwalee", parse_mode="HTML")
    elif txt.isdigit():
        perform_search(message, txt.strip())
    else:
        bot.reply_to(message, "⚠️ Buttons use karein ya ID bhejein.")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
