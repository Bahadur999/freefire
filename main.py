import os
import threading
import time
from flask import Flask
import requests
import telebot

# Web-сервер (Render/Koyeb өшіп қалмауы үшін)
app = Flask(__name__)

@app.route('/')
def home():
    return "FF Checker Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ЖАҢА БОТ ТОКЕНІН ОСЫНДА ҚОЙЫҢЫЗ:
API_TOKEN = '8869812841:AAHm8uPi6ghO_LLt3eZWYAMyLrvAalzhWks'
bot = telebot.TeleBot(API_TOKEN)

# Өзіңіздің Telegram ID-іңіз
ADMIN_ID = 5732227994

def notify_admin(user, action_text):
    if ADMIN_ID:
        try:
            user_info = f"👤 **Пайдаланушы:** {user.first_name} (@{user.username if user.username else 'жоқ'})\n🆔 **ID:** `{user.id}`\n📝 **Әрекет:** {action_text}"
            bot.send_message(ADMIN_ID, user_info, parse_mode="Markdown")
        except Exception as e:
            print(f"Админ хабарламасы қатесі: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    notify_admin(message.from_user, "Старт басты")
    bot.reply_to(
        message, 
        "Салам алейкум! 🎮 Free Fire Check Bot-қа кош келдіңіз!\n\n"
        "Маған Free Fire аккаунтының **ID-ін (UID)** жіберіңіз, мен ол туралы толық ақпаратты тауып беремін!"
    )

# Free Fire ID өңдеу (Тек цифрлардан тұратын ID-лер)
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) >= 8)
def handle_ff_id(message):
    ff_id = message.text.strip()
    notify_admin(message.from_user, f"FF ID іздеді: {ff_id}")
    status_msg = bot.reply_to(message, "🔎 Free Fire аккаунты тексерілуде...")

    # Free Fire API
    api_url = f"https://free-fire-api-five.vercel.app/api/ff_info?uid={ff_id}"

    try:
        res = requests.get(api_url, timeout=10).json()
        
        if "basicInfo" in res:
            info = res["basicInfo"]
            nickname = info.get("nickname", "Белгісіз")
            level = info.get("level", "Белгісіз")
            region = info.get("region", "Белгісіз")
            likes = info.get("likes", "0")
            created_at = info.get("createAt", "Белгісіз")

            text = (
                f"🔥 **Free Fire Аккаунт Инфо:**\n\n"
                f"👤 **Никнейм:** `{nickname}`\n"
                f"🆔 **UID:** `{ff_id}`\n"
                f"📊 **Деңгей (Level):** {level}\n"
                f"❤️ **Лайк саны:** {likes}\n"
                f"🌍 **Регион:** {region}\n"
                f"📅 **Ашылған күні:** `{created_at}`"
            )
            bot.edit_message_text(text, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("❌ Аккаунт табылмады. ID-ді тексеріп кайта жіберіңіз!", message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"FF API Қатесі: {e}")
        bot.edit_message_text("⚠️ Серверде қателік болды немесе бұл ID табылмады.", message.chat.id, status_msg.message_id)

# Басқа мәтіндерге жауап
@bot.message_handler(func=lambda message: True)
def handle_other(message):
    notify_admin(message.from_user, f"Жазды: {message.text}")
    bot.reply_to(message, "Тек Free Fire ID-ін (цифрлармен) жіберіңіз! 🎮")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Polling қатесі: {e}")
            time.sleep(3)
