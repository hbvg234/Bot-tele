from flask import Flask, request, render_template_string
import telebot
import os
import json
import random
import requests
from datetime import datetime
import urllib.parse

BOT_TOKEN = "8740382909:AAEA_Yl7tS9uVb4Gh2d9Eu7uufJ0hj0JMoA"
ADMIN_ID = 5735224923
WEATHER_API_KEY = "a74e4a0603ecc4e5e82fee5561b05633"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

ALLOWED_GROUPS = set()
BANNED_USERS = set()
guess_games = {}

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Bot Telegram</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 50px 40px;
            max-width: 600px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            text-align: center;
            animation: fadeIn 0.8s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .avatar {
            width: 100px;
            height: 100px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 50px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        h1 {
            color: #fff;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #a8b5d1;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .status {
            display: inline-block;
            background: rgba(0, 255, 136, 0.15);
            color: #00ff88;
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 25px;
            border: 1px solid rgba(0, 255, 136, 0.2);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 25px 0;
        }
        .stat-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px 10px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .stat-number {
            color: #fff;
            font-size: 28px;
            font-weight: 700;
        }
        .stat-label {
            color: #8899bb;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }
        .commands {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 25px 0;
            text-align: left;
        }
        .cmd {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px 14px;
            border-radius: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #a8b5d1;
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: all 0.3s;
        }
        .cmd:hover {
            background: rgba(102, 126, 234, 0.15);
            border-color: #667eea;
            color: #fff;
        }
        .cmd span {
            color: #667eea;
            font-weight: 600;
        }
        .footer {
            color: #556688;
            font-size: 12px;
            margin-top: 25px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 20px;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .time-badge {
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 16px;
            border-radius: 12px;
            color: #8899bb;
            font-size: 13px;
            display: inline-block;
        }
        @media (max-width: 480px) {
            .card { padding: 30px 20px; }
            .stats-grid { grid-template-columns: repeat(3, 1fr); }
            .commands { grid-template-columns: 1fr; }
            h1 { font-size: 22px; }
            .avatar { width: 70px; height: 70px; font-size: 35px; }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="avatar">🤖</div>
        <h1>✨ Bot Telegram</h1>
        <p class="subtitle">🟢 Đang hoạt động 24/7 trên Vercel</p>
        <div class="status">● ONLINE</div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number">{{ groups }}</div>
                <div class="stat-label">Nhóm</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ commands_count }}</div>
                <div class="stat-label">Lệnh</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ uptime }}</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>

        <div class="commands">
            <div class="cmd"><span>/ping</span> 🏓 Kiểm tra</div>
            <div class="cmd"><span>/help</span> 📋 Menu</div>
            <div class="cmd"><span>/weather</span> 🌤️ Thời tiết</div>
            <div class="cmd"><span>/time</span> 🕐 Giờ</div>
            <div class="cmd"><span>/qr</span> 🔲 Mã QR</div>
            <div class="cmd"><span>/guess</span> 🎯 Đoán số</div>
            <div class="cmd"><span>/translate</span> 📝 Dịch</div>
            <div class="cmd"><span>/money</span> 💱 Tỷ giá</div>
            <div class="cmd"><span>/fact</span> 💡 Sự thật</div>
            <div class="cmd"><span>/joke</span> 😂 Đùa</div>
            <div class="cmd"><span>/quote</span> 📜 Danh ngôn</div>
            <div class="cmd"><span>/menu</span> 🎛️ Buttons</div>
        </div>

        <div class="time-badge">📅 {{ current_time }}</div>
        
        <div class="footer">
            Made with ❤️ • Telegram Bot • <a href="https://vercel.com" target="_blank">Vercel</a>
        </div>
    </div>
</body>
</html>
"""

# ==================== HELPERS ====================

def is_admin(user_id):
    return user_id == ADMIN_ID

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
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if r.status_code != 200:
            return None, "Lỗi API tỷ giá"
        rate = data['rates'].get(to_currency.upper())
        if not rate:
            return None, f"Không hỗ trợ {to_currency.upper()}"
        return amount * rate, None
    except:
        return None, "Lỗi kết nối"

# ==================== WEB ROUTE ====================

@app.route('/', methods=['GET'])
def home():
    now = datetime.now().strftime('%H:%M:%S %d/%m/%Y')
    return render_template_string(
        HTML_TEMPLATE,
        groups=len(ALLOWED_GROUPS),
        commands_count=14,
        uptime="24/7",
        current_time=now
    )

# ==================== WEBHOOK ====================

@app.route('/', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200
    except Exception as e:
        print(f"Lỗi: {e}")
        return 'error', 500

# ==================== BOT COMMANDS ====================

@bot.message_handler(commands=['start', 'ping'])
def ping(message):
    bot.reply_to(message, "🏓 **Pong! Bot đang hoạt động!**", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_command(message):
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
/menu - Menu nút bấm
/banana - Đùa vui 🍌

👑 **ADMIN:**
/addgroup - Thêm nhóm
/stats - Thống kê
"""
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['time'])
def get_time(message):
    now = datetime.now()
    bot.reply_to(message, f"🕐 **{now.strftime('%H:%M:%S %d/%m/%Y')}**", parse_mode="Markdown")

@bot.message_handler(commands=['weather'])
def weather_cmd(message):
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

# ----- QR CODE -----
@bot.message_handler(commands=['qr'])
def qr_code(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "⚠️ /qr <nội dung cần tạo mã>")
    content = ' '.join(args[1:])
    try:
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(content)}"
        bot.send_photo(message.chat.id, url, caption=f"🔲 **Mã QR:**\n{content}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")

# ----- GUESS GAME -----
@bot.message_handler(commands=['guess'])
def guess_game(message):
    user_id = message.from_user.id
    if user_id in guess_games:
        return bot.reply_to(message, "⏳ Bạn đang chơi! Hãy đoán số từ 1-100")
    number = random.randint(1, 100)
    guess_games[user_id] = {'number': number, 'attempts': 0, 'max_attempts': 7}
    bot.reply_to(message, "🎯 **ĐOÁN SỐ 1-100**\nBạn có 7 lần đoán. Bắt đầu!")

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

# ----- TRANSLATE -----
@bot.message_handler(commands=['translate'])
def translate_text(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "⚠️ /translate <văn bản cần dịch>")
    text = ' '.join(args[1:])
    try:
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

# ----- MONEY -----
@bot.message_handler(commands=['money'])
def exchange_money(message):
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

# ----- BANANA -----
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

# ----- MENU INLINE -----
@bot.message_handler(commands=['menu'])
def menu_inline(message):
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

# ----- GROUP ID -----
@bot.message_handler(commands=['groupid'])
def group_id(message):
    if message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, f"🆔 **Group ID:** `{message.chat.id}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Lệnh này chỉ trong nhóm!")

# ----- ADMIN -----
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

# ==================== MESSAGE HANDLER ====================

@bot.message_handler(func=lambda m: True)
def echo(message):
    if message.chat.type in ['group', 'supergroup']:
        if str(message.chat.id) not in ALLOWED_GROUPS:
            return
    if message.text and message.text.lower() in ['hello', 'hi', 'chào']:
        bot.reply_to(message, f"👋 Xin chào {message.from_user.first_name}!")
    elif message.text and '?' in message.text:
        bot.reply_to(message, "🤔 Bạn cần giúp gì? Dùng /help nhé!")

# ==================== RUN ====================

if __name__ == '__main__':
    app.run()
