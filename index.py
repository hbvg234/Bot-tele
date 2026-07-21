from flask import Flask, request
import telebot
import os
import json
import random
import requests
from datetime import datetime
import hashlib
import base64
import urllib.parse

BOT_TOKEN = "8740382909:AAEA_Yl7tS9uVb4Gh2d9Eu7uufJ0hj0JMoA"
ADMIN_ID = 5735224923
WEATHER_API_KEY = "a74e4a0603ecc4e5e82fee5561b05633"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

ALLOWED_GROUPS = set()
BANNED_USERS = set()

# Game data
guess_games = {}
quiz_data = [
    {"q": "Thủ đô của Việt Nam?", "a": "Hà Nội", "opts": ["Hà Nội", "TP.HCM", "Đà Nẵng", "Hải Phòng"]},
    {"q": "2 + 2 = ?", "a": "4", "opts": ["3", "4", "5", "6"]},
    {"q": "Mặt trời mọc ở hướng nào?", "a": "Đông", "opts": ["Đông", "Tây", "Nam", "Bắc"]},
]

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

def get_exchange_rate(from_currency, to_currency, amount):
    """Lấy tỷ giá từ API miễn phí"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if r.status_code != 200:
            return None, "Lỗi API tỷ giá"
        rate = data['rates'].get(to_currency.upper())
        if not rate:
            return None, f"Không hỗ trợ {to_currency.upper()}"
        result = amount * rate
        return result, None
    except:
        return None, "Lỗi kết nối"

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
    text = """🤖 **BOT CỦA BẠN - PHIÊN BẢN MỚI**

📌 **LỆNH CƠ BẢN:**
/ping - Kiểm tra bot
/help - Menu này
/time - Thời gian hiện tại
/weather <tp> - Thời tiết
/fact - Sự thật vui
/joke - Đùa một câu
/quote - Danh ngôn

🆕 **TÍNH NĂNG MỚI:**
/qr <nội dung> - Tạo mã QR
/guess - Chơi đoán số (1-100)
/translate <text> - Dịch sang tiếng Việt
/money <số> <từ> <đến> - Đổi tiền tệ
/banana - Đùa vui 🍌

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

# ==================== TÍNH NĂNG MỚI ====================

# ----- 1. QR CODE -----
@bot.message_handler(commands=['qr'])
def qr_code(message):
    if is_banned(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "⚠️ /qr <nội dung cần tạo mã>")
    content = ' '.join(args[1:])
    try:
        # Sử dụng API tạo QR code
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(content)}"
        bot.reply_to(message, f"🔲 **Mã QR của bạn:**\n{url}", parse_mode="Markdown")
        # Gửi ảnh QR
        bot.send_photo(message.chat.id, url, caption=f"📌 Nội dung: {content}")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi tạo QR: {e}")

# ----- 2. GAME ĐOÁN SỐ -----
@bot.message_handler(commands=['guess'])
def guess_game(message):
    if is_banned(message.from_user.id):
        return
    user_id = message.from_user.id
    if user_id in guess_games:
        return bot.reply_to(message, "⏳ Bạn đang chơi! Hãy đoán số từ 1-100")
    number = random.randint(1, 100)
    guess_games[user_id] = {
        'number': number,
        'attempts': 0,
        'max_attempts': 7
    }
    bot.reply_to(message, f"🎯 **ĐOÁN SỐ 1-100**\nBạn có 7 lần đoán. Bắt đầu!")

@bot.message_handler(func=lambda message: message.from_user.id in guess_games and message.text and message.text.isdigit())
def guess_handler(message):
    user_id = message.from_user.id
    game = guess_games[user_id]
    guess = int(message.text)
    game['attempts'] += 1
    if guess == game['number']:
        del guess_games[user_id]
        bot.reply_to(message, f"🎉 **ĐÚNG RỒI!** Số là {game['number']}\nSố lần đoán: {game['attempts']}")
    elif game['attempts'] >= game['max_attempts']:
        del guess_games[user_id]
        bot.reply_to(message, f"😢 Hết lượt! Số đúng là {game['number']}")
    elif guess < game['number']:
        bot.reply_to(message, f"📈 Lớn hơn! Còn {game['max_attempts'] - game['attempts']} lượt")
    else:
        bot.reply_to(message, f"📉 Nhỏ hơn! Còn {game['max_attempts'] - game['attempts']} lượt")

# ----- 3. DỊCH VĂN BẢN -----
@bot.message_handler(commands=['translate'])
def translate_text(message):
    if is_banned(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "⚠️ /translate <văn bản cần dịch>")
    text = ' '.join(args[1:])
    try:
        # Dịch sang tiếng Việt
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=en|vi"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get('responseStatus') == 200:
            translated = data['responseData']['translatedText']
            bot.reply_to(message, f"📝 **Dịch sang tiếng Việt:**\n{translated}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Lỗi dịch")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")

# ----- 4. ĐỔI TIỀN TỆ -----
@bot.message_handler(commands=['money'])
def exchange_money(message):
    if is_banned(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 4:
        return bot.reply_to(message, "⚠️ /money <số> <từ> <đến>\nVí dụ: /money 100 usd vnd")
    try:
        amount = float(args[1])
        from_cur = args[2].upper()
        to_cur = args[3].upper()
        result, err = get_exchange_rate(from_cur, to_cur, amount)
        if err:
            return bot.reply_to(message, f"❌ {err}")
        bot.reply_to(message, f"💱 **{amount:.2f} {from_cur} = {result:.2f} {to_cur}**\n📅 {datetime.now().strftime('%d/%m/%Y')}", parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "⚠️ Số tiền không hợp lệ")
    except:
        bot.reply_to(message, "❌ Lỗi")

# ----- 5. TRÁI CÂY VUI (BANANA) -----
@bot.message_handler(commands=['banana'])
def banana(message):
    bananas = [
        "🍌 Đây là chuối! 🍌",
        "🍌Ăn chuối tốt cho sức khỏe! 💪",
        "🐒 Khỉ thích chuối! 🍌",
        "🍌 Chuối vàng ơi! 🌟",
        "🍌 Ai muốn ăn chuối nào? 😋"
    ]
    bot.reply_to(message, random.choice(bananas))

# ==================== GROUP ID ====================

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
🎮 Đang chơi đoán số: {len(guess_games)}
📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ==================== INLINE BUTTONS ====================

@bot.message_handler(commands=['menu'])
def menu_inline(message):
    if is_banned(message.from_user.id):
        return
    from telebot import types
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🌤️ Thời tiết", callback_data="weather")
    btn2 = types.InlineKeyboardButton("😂 Đùa vui", callback_data="joke")
    btn3 = types.InlineKeyboardButton("💡 Sự thật", callback_data="fact")
    btn4 = types.InlineKeyboardButton("🎯 Đoán số", callback_data="guess")
    btn5 = types.InlineKeyboardButton("🍌 Chuối", callback_data="banana")
    btn6 = types.InlineKeyboardButton("📝 Dịch", callback_data="translate")
    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.reply_to(message, "🎯 **CHỌN TÍNH NĂNG:**", reply_markup=keyboard, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    chat_id = call.message.chat.id
    if data == "weather":
        bot.send_message(chat_id, "🌤️ **Hà Nội**: 32°C, Nhiều mây", parse_mode="Markdown")
    elif data == "joke":
        jokes = ["🐔 Gà chạy qua đường!", "💻 Máy tính bị cảm!", "🐶 Ổ chó ơi là ổ chó!"]
        bot.send_message(chat_id, f"😂 {random.choice(jokes)}")
    elif data == "fact":
        facts = ["🐱 Mèo có hơn 100 âm thanh", "🌊 Đại dương chiếm 71%"]
        bot.send_message(chat_id, f"💡 {random.choice(facts)}")
    elif data == "guess":
        bot.send_message(chat_id, "🎯 /guess - Chơi đoán số!")
    elif data == "banana":
        bot.send_message(chat_id, "🍌 Chuối vàng! 🍌")
    elif data == "translate":
        bot.send_message(chat_id, "📝 /translate <nội dung>")
    bot.answer_callback_query(call.id)

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
    elif message.text and '?' in message.text:
        bot.reply_to(message, "🤔 Bạn cần giúp gì? Dùng /help nhé!")

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

if __name__ == '__main__':
    app.run()
