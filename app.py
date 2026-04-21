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
    return "Bot is Alive!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bhai Render par Swagat hai! ✅\nUser_ID bhejo search ke liye.")

@bot.message_handler(func=lambda message: True)
def search_user(message):
    user_id = message.text.strip()
    if user_id.isdigit():
        try:
            r = requests.get(f"{API_URL}?user_id={user_id}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if results:
                    res = results[0]
                    text = f"👤 Name: {res.get('First_Name')}\n📞 Phone: {res.get('Phone_Number')}"
                    bot.reply_to(message, text)
                else:
                    bot.reply_to(message, "❌ Nahi mila.")
        except:
            bot.reply_to(message, "⚠️ API Error!")

def run_flask():
    # Render hamesha PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask ko alag thread mein chalayenge taaki Render 'Port' detect kar sake
    t = Thread(target=run_flask)
    t.start()
    
    print("Bot is starting...")
    bot.infinity_polling()
