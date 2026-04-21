import telebot
import requests
import os
from flask import Flask
from threading import Thread

# --- CONFIG ---
BOT_TOKEN = "8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI"
API_URL = "https://tfqdeadlo-tgdatabase.hf.space/search"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!", 200

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "<b>🤖 Welcome to Search Bot</b>\n\n"
        "<b>👨‍💻 Developer:</b> @TFQdeadlox636\n"
        "──────────────────\n"
        "🔍 <i>Search karne ke liye 'User ID' bheje.</i>"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

# --- SEARCH LOGIC ---
@bot.message_handler(func=lambda message: True)
def search_user(message):
    user_id = message.text.strip()
    
    if not user_id.isdigit():
        bot.reply_to(message, "❌ <b>Galt format!</b> Sirf numbers (ID) bheje.", parse_mode="HTML")
        return

    # Loading message (Optional, for better feel)
    status_msg = bot.reply_to(message, "⏳ <i>Searching in Database...</i>", parse_mode="HTML")

    try:
        r = requests.get(f"{API_URL}?user_id={user_id}", timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])

            if results:
                res = results[0]
                # Result ko clean aur premium look dena
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
            bot.edit_message_text("⚠️ <b>API Error:</b> Database respond nahi kar raha.", message.chat.id, status_msg.message_id, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text("⚠️ <b>Connection Error!</b> API tak request nahi pahonchi.", message.chat.id, status_msg.message_id, parse_mode="HTML")

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print("Bot is starting on Render...")
    bot.infinity_polling()
