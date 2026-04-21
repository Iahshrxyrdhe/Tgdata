import telebot
import requests
import os
import random
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIG ---
BOT_TOKEN = "8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI"
API_URL = "https://tfqdeadlo-tgdatabase.hf.space/search"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!", 200

# --- KEYBOARD SETUP ---
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔍 Search User", callback_data="search_info"))
    markup.row(
        InlineKeyboardButton("👨‍💻 Developer", callback_data="dev_info"),
        InlineKeyboardButton("📢 Channel", callback_data="chan_info")
    )
    markup.row(InlineKeyboardButton("🎲 Random Search", callback_data="random_search"))
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "<b>🤖 Welcome to Premium Search Bot</b>\n\n"
        "Niche diye gaye buttons ka use karein:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_menu())

# --- CALLBACK HANDLER (Buttons click karne par kya ho) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "search_info":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🔍 <b>ID Bhejo:</b>\nBas User ID type karke send karo, main search kar dunga.", parse_mode="HTML")
    
    elif call.data == "dev_info":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "👨‍💻 <b>Developer:</b> @TFQdeadlox636", parse_mode="HTML")
        
    elif call.data == "chan_info":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📢 <b>Official Channel:</b> @termuxwalee", parse_mode="HTML")
        
    elif call.data == "random_search":
        bot.answer_callback_query(call.id, "🎲 Fetching Random User...")
        # Random ID generate karna (Apne database ke hisab se range badal sakte ho)
        random_id = str(random.randint(1, 10000)) 
        perform_search(call.message, random_id)

# --- SEARCH LOGIC FUNCTION ---
def perform_search(message, user_id):
    status_msg = bot.send_message(message.chat.id, "⏳ <i>Searching Database...</i>", parse_mode="HTML")
    try:
        r = requests.get(f"{API_URL}?user_id={user_id}", timeout=15)
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

# --- TEXT MESSAGE HANDLER ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text.isdigit():
        perform_search(message, message.text.strip())
    else:
        bot.reply_to(message, "⚠️ Please send a valid **User ID** (Numbers only).", parse_mode="Markdown")

# --- SERVER RUN ---
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot is alive on Render!")
    bot.infinity_polling()
