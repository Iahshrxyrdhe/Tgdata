import telebot
import requests
from telebot import types

# --- CONFIG ---
API_TOKEN = '8435434656:AAEzE0AK1TvNRsDzXxycUyWdMKzuES-TfAI' 
BASE_URL = "https://tfqdeadlo-tgdatabase.hf.space"

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

@bot.message_handler(commands=['start'])
def start(message):
    welcome_msg = "🔥 **Welcome!**\n\nDatabase search ke liye niche diye gaye buttons use karein."
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🔍 Search ID":
        msg = bot.send_message(chat_id, "🆔 **Please enter the User ID to search:**")
        bot.register_next_step_handler(msg, process_search)

    elif text == "🎲 Random Search":
        bot.send_message(chat_id, "⏳ Fetching a random record (2.8Cr rows)...")
        try:
            # Timeout add kiya hai taaki bot hang na ho
            r = requests.get(f"{BASE_URL}/random", timeout=15)
            data = r.json()
            if data.get("status") == "success":
                res = data["result"]
                response = (f"🎲 **Random Result:**\n\n"
                            f"👤 Name: {res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}\n"
                            f"📞 Phone: {res.get('Phone', 'N/A')}\n"
                            f"🆔 ID: {res.get('User_ID', 'N/A')}\n"
                            f"🌐 User: @{res.get('Username', 'N/A')}")
                bot.send_message(chat_id, response, parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "❌ Database abhi ready nahi hai. 1 minute baad try karein.")
        except Exception as e:
            bot.send_message(chat_id, "⚠️ Server So raha hai (Sleep Mode). Main use jaga raha hoon, 10 second baad dobara click karein.")
            # Browser ki tarah ek hit maarna taaki server jag jaye
            try: requests.get(BASE_URL)
            except: pass

    elif text == "👨‍💻 Developer":
        bot.send_message(chat_id, f"👨‍💻 **Bot Developer:** {DEVELOPER_ID}\n\nSupport ke liye message karein.")

    elif text == "📢 Channel":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Join Channel 🚀", url=CHANNEL_LINK)
        markup.add(btn)
        bot.send_message(chat_id, "📢 **Join @termuxwalee for updates:**", reply_markup=markup, parse_mode="Markdown")

def process_search(message):
    uid = message.text.strip()
    if not uid.isdigit():
        bot.send_message(message.chat.id, "❌ Invalid ID! Sirf numbers daalein.")
        return

    bot.send_message(message.chat.id, f"🔎 Searching for `{uid}`...")
    
    try:
        r = requests.get(f"{BASE_URL}/search?uid={uid}", timeout=15)
        data = r.json()
        
        if data.get("status") == "success":
            res = data["result"]
            response = (f"✅ **Record Found!**\n\n"
                        f"👤 Name: {res.get('First_Name', 'N/A')} {res.get('Last_Name', '')}\n"
                        f"📞 Phone: {res.get('Phone', 'N/A')}\n"
                        f"🆔 ID: {res.get('User_ID', 'N/A')}\n"
                        f"🌐 User: @{res.get('Username', 'N/A')}")
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ No record found.")
    except Exception as e:
        bot.send_message(chat_id, "⚠️ API connect nahi ho pa rahi. Browser mein link check karein.")

print("🤖 Bot is running...")
bot.infinity_polling()
