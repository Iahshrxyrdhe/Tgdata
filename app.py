import telebot
import requests
from telebot import types

# --- CONFIG ---
API_TOKEN = '8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI'  # BotFather wala token yahan daalo
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"

# Updated Details
DEVELOPER_ID = "@TFQdeadlox636" 
CHANNEL_LINK = "https://t.me/termuxwalee" 

bot = telebot.TeleBot(API_TOKEN)

# --- KEYBOARD SETUP ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Search ID")
    btn2 = types.KeyboardButton("🎲 Random Search")
    btn3 = types.KeyboardButton("👨‍💻 Developer")
    btn4 = types.KeyboardButton("📢 Channel")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    welcome_msg = "🔥 **Welcome!**\n\nDatabase search karne ke liye niche diye gaye buttons ka use karein."
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🔍 Search ID":
        msg = bot.send_message(chat_id, "🆔 **Please enter the User ID to search:**")
        bot.register_next_step_handler(msg, process_search)

    elif text == "🎲 Random Search":
        bot.send_message(chat_id, "⏳ Fetching a random record...")
        try:
            r = requests.get(f"{BASE_URL}/random")
            data = r.json()
            if data.get("status") == "success":
                res = data["result"]
                response = (f"🎲 **Random Result:**\n\n"
                            f"👤 Name: {res['First_Name']} {res['Last_Name']}\n"
                            f"📞 Phone: {res['Phone']}\n"
                            f"🆔 ID: {res['User_ID']}\n"
                            f"🌐 User: @{res['Username']}")
                bot.send_message(chat_id, response, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "⚠️ API Server Error.")

    elif text == "👨‍💻 Developer":
        dev_msg = f"👨‍💻 **Bot Developer:**\n\nContact: {DEVELOPER_ID}\n\nSupport ya queries ke liye message karein."
        bot.send_message(chat_id, dev_msg, parse_mode="Markdown")

    elif text == "📢 Channel":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Join Channel 🚀", url=CHANNEL_LINK)
        markup.add(btn)
        bot.send_message(chat_id, f"📢 **Join @termuxwalee for latest updates:**", reply_markup=markup, parse_mode="Markdown")

# --- SEARCH LOGIC ---
def process_search(message):
    uid = message.text.strip()
    if not uid.isdigit():
        bot.send_message(message.chat.id, "❌ Invalid ID! Sirf numbers daalein.")
        return

    bot.send_message(message.chat.id, f"🔎 Searching for `{uid}`...", parse_mode="Markdown")
    
    try:
        r = requests.get(f"{BASE_URL}/search?uid={uid}")
        data = r.json()
        
        if data.get("status") == "success":
            res = data["result"]
            response = (f"✅ **Record Found!**\n\n"
                        f"👤 Name: {res['First_Name']} {res['Last_Name']}\n"
                        f"📞 Phone: {res['Phone']}\n"
                        f"🆔 ID: {res['User_ID']}\n"
                        f"🌐 User: @{res['Username']}")
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ No record found.")
    except:
        bot.send_message(message.chat.id, "⚠️ API connection error.")

# --- RUN BOT ---
print("🤖 Bot is running with final settings...")
bot.infinity_polling()
