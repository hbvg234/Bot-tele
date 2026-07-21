from flask import Flask, request
import telebot
import os
import json
import random
import requests
from datetime import datetime

# ==================== CONFIG ====================
BOT_TOKEN = "8740382909:AAEA_Yl7tS9uVb4Gh2d9Eu7uufJ0hj0JMoA"
ADMIN_ID = 5735224923
WEATHER_API_KEY = "a74e4a0603ecc4e5e82fee5561b05633"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ==================== DATA ====================
ALLOWED_GROUPS = set()
BANNED_USERS = set()

# ==================== HELPERS ====================
def is_admin(user_id):
    return user_id == ADMIN_ID

def is_banned(user_id):
    return user_id in BANNED_USERS

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=vi"
        r = requests.get(url, timeout=5)
        data = r.json()
        if r.status_code != 200:
            return None, "Không tìm thấy thành phố"
        return {
            'city': data['name'],
            'temp': data['main']['temp'],
            'desc': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind': data['wind']['speed']
        }, None
    except:
        return None, "Lỗi kết nối API"

# ==================== COMMANDS ====================

@bot.message_handler(commands=['start', 'ping'])
def ping(message):
    if is_banned(message.from_user.id):
        return bot.reply_to(message, "🚫 Bạn đã bị cấm")
    bot.reply_to(message, "🏓 Pong! Bot đang hoạt động!")

@bot.message_handler(commands=['help'])
def help_command(message):
    if is_banned(message.from_user.id):
        return
    text = """🤖 **BOT CỦA BẠN**

📌 **LỆNH:**
/ping - Kiểm tra bot
/help - Menu này
/time - Thời gian hiện tại
/weather <tp> - Thời tiết
/fact - Sự thật vui
/joke - Đùa một câu
/quote - Danh ngôn
/groupid - Lấy ID nhóm

👑 **ADMIN:**
/addgroup - Thêm nhóm
/stats - Thống kê
"""
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['time'])
def get_time(message):
    if is_banned(message.from_user.id):
        return
    now = datetime.now()
    bot.reply_to(message, f"🕐 **{now.strftime('%H:%M:%S %d/%m/%Y')}**", parse_mode="Markdown")

@bot.message_handler(commands=['weather'])
def weather_cmd(message):
    if is_banned(message.from_user.id):
        return
    
    args = message.text.split()
    city = ' '.join(args[1:]) if len(args) > 1 else 'Hanoi'
    
    weather, err = get_weather(city)
    if err:
        return bot.reply_to(message, f"❌ {err}")
    
    text = f"""🌤️ **{weather['city']}**
🌡️ {weather['temp']:.1f}°C
☁️ {weather['desc'].title()}
💧 Độ ẩm: {weather['humidity']}%
💨 Gió: {weather['wind']} m/s"""
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['fact'])
def fact(message):
    facts = [
        "🐱 Mèo có hơn 100 âm thanh khác nhau",
        "🌊 Đại dương chiếm 71% Trái Đất",
        "🦒 Hươu cao cổ tim nặng 11kg",
        "🐧 Chim cánh cụt bơi giỏi hơn bay",
        "🌙 Mặt Trăng cách Trái Đất 384.400km",
        "🍕 Pizza sinh ra ở Naples, Ý",
        "🐘 Voi là động vật lớn nhất trên cạn"
    ]
    bot.reply_to(message, f"💡 {random.choice(facts)}")

@bot.message_handler(commands=['joke'])
def joke(message):
    jokes = [
        "🐔 Gà chạy qua đường vì sợ bị làm thịt! 😂",
        "📚 Học mãi không giỏi vì không động não! 🤣",
        "💻 Máy tính bị cảm vì nhiều virus! 😷",
        "🐶 Chó hỏi: 'Mày sống ở đâu?' - 'Ổ chó ơi là ổ chó!'"
    ]
    bot.reply_to(message, f"😂 {random.choice(jokes)}")

@bot.message_handler(commands=['quote'])
def quote(message):
    quotes = [
        "💪 Thành công là hành trình, không phải đích đến",
        "🌟 Hãy là phiên bản tốt nhất của chính mình",
        "🔥 Đừng so sánh mình với người khác",
        "🌈 Mọi thứ đều có thể nếu bạn tin tưởng"
    ]
    bot.reply_to(message, f"📜 {random.choice(quotes)}")

@bot.message_handler(commands=['groupid'])
def group_id(message):
    if is_banned(message.from_user.id):
        return
    if message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, f"🆔 **Group ID:** `{message.chat.id}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Lệnh này chỉ trong nhóm!")

# ==================== ADMIN COMMANDS ====================

@bot.message_handler(commands=['addgroup'])
def add_group(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "❌ Chỉ Admin!")
    
    chat_id = str(message.chat.id)
    ALLOWED_GROUPS.add(chat_id)
    bot.reply_to(message, f"✅ Đã thêm nhóm `{chat_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "❌ Chỉ Admin!")
    
    text = f"""📊 **THỐNG KÊ**
📌 Nhóm: {len(ALLOWED_GROUPS)}
🚫 Bị cấm: {len(BANNED_USERS)}
📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ==================== MESSAGE HANDLER ====================

@bot.message_handler(func=lambda m: True)
def echo(message):
    if is_banned(message.from_user.id):
        return
    
    if message.chat.type in ['group', 'supergroup']:
        if str(message.chat.id) not in ALLOWED_GROUPS:
            return
    
    if message.text and message.text.lower() in ['hello', 'hi', 'chào']:
        bot.reply_to(message, f"👋 Xin chào {message.from_user.first_name}!")

# ==================== WEBHOOK ====================

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
            bot.process_new_updates([update])
            return 'ok', 200
        except Exception as e:
            print(f"Lỗi: {e}")
            return 'error', 500
    return "🤖 Bot đang chạy!"

# ==================== RUN ====================
if __name__ == '__main__':
    app.run()
