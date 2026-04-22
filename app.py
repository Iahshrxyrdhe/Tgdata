import telebot
import requests
from telebot import types

# --- CONFIG ---
API_TOKEN = '8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI'  # BotFather se mila token yahan daalo
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"

bot = telebot.TeleBot(API_TOKEN)

# --- KEYBOARD SETUP ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Search ID")
    btn2 = types.KeyboardButton("🎲 Random Search")
    btn3 = types.KeyboardButton("👤 My Profile")
    btn4 = types.KeyboardButton("ℹ️ Info / Help")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    welcome_msg = "🔥 **Welcome to 28M Database Bot!**\n\nNiche diye gaye buttons ka use karke search karein."
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🔍 Search ID":
        msg = bot.send_message(chat_id, "🆔 **Please enter the User ID to search:**")
        bot.register_next_step_handler(msg, process_search)

    elif text == "🎲 Random Search":
        bot.send_message(chat_id, "⏳ Fetching a random record from 2.8 Crore rows...")
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
            else:
                bot.send_message(chat_id, "❌ Error fetching random data.")
        except Exception as e:
            bot.send_message(chat_id, "⚠️ API Server is busy or sleeping. Try again.")

    elif text == "👤 My Profile":
        user = message.from_user
        profile_msg = (f"👤 **Your Profile:**\n\n"
                       f"📛 Name: {user.first_name}\n"
                       f"🆔 Your ID: `{user.id}`\n"
                       f"✨ Username: @{user.username}")
        bot.send_message(chat_id, profile_msg, parse_mode="Markdown")

    elif text == "ℹ️ Info / Help":
        help_text = ("ℹ️ **Bot Information**\n\n"
                     "📍 Database: 2.8 Crore Users\n"
                     "⚡ Speed: 0.06s\n"
                     "🛠 Built by: Your Name\n\n"
                     "Search button dabao aur ID daalo result paane ke liye.")
        bot.send_message(chat_id, help_text, parse_mode="Markdown")

# --- SEARCH LOGIC ---
def process_search(message):
    uid = message.text.strip()
    if not uid.isdigit():
        bot.send_message(message.chat.id, "❌ Invalid ID! Please enter numbers only.")
        return

    bot.send_message(message.chat.id, f"🔎 Searching for ID: `{uid}`...", parse_mode="Markdown")
    
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
            bot.send_message(message.chat.id, "❌ No record found for this ID.")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ API connection error.")

# --- RUN BOT ---
print("🤖 Bot is running...")
bot.infinity_polling()
