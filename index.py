from flask import Flask, request
import telebot
import os
import json
import random
import time
from datetime import datetime
import requests  # Thêm requests để gọi API thời tiết

# ==================== CONFIG ====================
BOT_TOKEN = "8740382909:AAEA_Yl7tS9uVb4Gh2d9Eu7uufJ0hj0JMoA"
ADMIN_ID = 5735224923
WEATHER_API_KEY = "a74e4a0603ecc4e5e82fee5561b05633"  # API key thời tiết

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ==================== DATA ====================
BANNED_USERS = set()
ALLOWED_GROUPS = set()

try:
    with open('data.json', 'r') as f:
        data = json.load(f)
        ALLOWED_GROUPS = set(data.get('allowed_groups', []))
        BANNED_USERS = set(data.get('banned_users', []))
except:
    pass

def save_data():
    try:
        with open('data.json', 'w') as f:
            json.dump({
                'allowed_groups': list(ALLOWED_GROUPS),
                'banned_users': list(BANNED_USERS)
            }, f)
    except:
        pass

# ==================== DATA ====================
WELCOME_MESSAGES = [
    "Chào mừng {} đến với nhóm! 🎉",
    "Ồ một thành viên mới: {}! Chào mừng! 🌟",
    "Thêm một chiến binh: {} đã gia nhập! ⚔️",
    "Đã có thêm {}! Nhiệt liệt chào mừng! 🔥",
    "Chào {}! Chúc bạn vui vẻ trong nhóm! 😊"
]

RANDOM_FACTS = [
    "🐱 Mèo có thể phát ra hơn 100 âm thanh khác nhau!",
    "🌊 Đại dương chiếm 71% diện tích Trái Đất!",
    "🦒 Hươu cao cổ có tim nặng tới 11kg!",
    "🐧 Chim cánh cụt không thể bay nhưng bơi rất giỏi!",
    "🌙 Mặt Trăng cách Trái Đất khoảng 384,400 km!",
    "🍕 Pizza được phát minh ở Naples, Ý!",
    "🐬 Cá heo có thể giao tiếp bằng âm thanh!",
    "🌳 Cây có thể sống hàng nghìn năm!",
    "🐘 Voi là động vật có vú lớn nhất trên cạn!",
    "🎵 Thế giới có hơn 7.000 ngôn ngữ khác nhau!"
]

JOKES = [
    "Tại sao con gà chạy qua đường? 🐔\n→ Vì nó sợ bị làm thịt! 😂",
    "Học sinh hỏi thầy: 'Thầy ơi, sao em học mãi không giỏi?'\n→ Thầy đáp: 'Vì em không chịu động não!' 🤣",
    "Bác sĩ bảo: 'Anh bị stress nặng!' \n→ Bệnh nhân: 'Vậy làm sao để hết?' \n→ Bác sĩ: 'Đừng đọc tin nhắn này!' 😆",
    "Có 2 con chó gặp nhau:\n- Mày sống ở đâu?\n- Ở ổ chó!\n- Ổ chó nào?\n- Ổ chó ơi là ổ chó! 🐶",
    "Tại sao máy tính hay bị cảm? 💻\n→ Vì có quá nhiều virus! 😷"
]

QUOTES = [
    "💪 Thành công không phải là đích đến, mà là hành trình.",
    "🌟 Cuộc sống là những chuyến đi, hãy tận hưởng mỗi khoảnh khắc.",
    "🔥 Đừng so sánh mình với người khác. Hãy là phiên bản tốt nhất của chính mình!",
    "🌈 Mọi thứ đều có thể nếu bạn tin tưởng.",
    "🎯 Mục tiêu không cần to lớn, chỉ cần đủ để thúc đẩy bạn tiến lên."
]

MOTIVATIONAL = [
    "Bạn có thể làm được! 💪",
    "Đừng từ bỏ! Thành công đang chờ bạn! 🌟",
    "Hôm nay là ngày mới, cơ hội mới! 🚀",
    "Sai lầm là bài học, không phải là thất bại! 📚",
    "Bạn mạnh mẽ hơn bạn nghĩ! 💥"
]

# ==================== HÀM THỜI TIẾT ====================

def get_weather(city):
    """Lấy thông tin thời tiết từ OpenWeatherMap API"""
    try:
        # URL API OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=vi"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            return None, data.get('message', 'Không tìm thấy thành phố')
        
        # Lấy thông tin thời tiết
        weather = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon']
        }
        
        return weather, None
    except requests.exceptions.Timeout:
        return None, "Kết nối tới API thời tiết bị timeout"
    except requests.exceptions.ConnectionError:
        return None, "Không thể kết nối tới API thời tiết"
    except Exception as e:
        return None, f"Lỗi: {str(e)}"

def get_weather_emoji(description):
    """Chuyển đổi mô tả thời tiết thành emoji"""
    desc = description.lower()
    if 'mưa' in desc or 'rain' in desc:
        return '🌧️'
    elif 'dông' in desc or 'storm' in desc:
        return '⛈️'
    elif 'tuyết' in desc or 'snow' in desc:
        return '❄️'
    elif 'mây' in desc or 'cloud' in desc:
        return '☁️'
    elif 'nắng' in desc or 'clear' in desc:
        return '☀️'
    elif 'sương mù' in desc or 'fog' in desc:
        return '🌫️'
    else:
        return '🌤️'

# ==================== COMMANDS ====================

# ----- ADMIN COMMANDS -----
@bot.message_handler(commands=['addgroup'])
def add_group(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Lệnh này chỉ dành cho Admin!")
    
    chat_id = str(message.chat.id)
    ALLOWED_GROUPS.add(chat_id)
    save_data()
    bot.reply_to(message, f"✅ Đã thêm nhóm `{chat_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['delgroup'])
def del_group(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Lệnh này chỉ dành cho Admin!")
    
    chat_id = str(message.chat.id)
    ALLOWED_GROUPS.discard(chat_id)
    save_data()
    bot.reply_to(message, f"🗑️ Đã xóa nhóm `{chat_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Lệnh này chỉ dành cho Admin!")
    
    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "⚠️ /ban <user_id>")
        user_id = int(args[1])
        BANNED_USERS.add(user_id)
        save_data()
        bot.reply_to(message, f"🚫 Đã cấm user `{user_id}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Lỗi: ID không hợp lệ!")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Lệnh này chỉ dành cho Admin!")
    
    try:
        args = message.text.split()
        if len(args) < 2:
            return bot.reply_to(message, "⚠️ /unban <user_id>")
        user_id = int(args[1])
        BANNED_USERS.discard(user_id)
        save_data()
        bot.reply_to(message, f"✅ Đã bỏ cấm user `{user_id}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Lỗi: ID không hợp lệ!")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Lệnh này chỉ dành cho Admin!")
    
    try:
        msg = message.text.replace('/broadcast', '').strip()
        if not msg:
            return bot.reply_to(message, "⚠️ /broadcast <tin nhắn>")
        
        count = 0
        for chat_id in ALLOWED_GROUPS:
            try:
                bot.send_message(chat_id, f"📢 **THÔNG BÁO TỪ ADMIN:**\n\n{msg}", parse_mode="Markdown")
                count += 1
            except:
                pass
        
        bot.reply_to(message, f"✅ Đã gửi thông báo đến {count} nhóm!")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Lệnh này chỉ dành cho Admin!")
    
    stats_text = f"""
📊 **THỐNG KÊ BOT**

📌 **Nhóm được phép:** {len(ALLOWED_GROUPS)}
🚫 **Người bị cấm:** {len(BANNED_USERS)}
🤖 **Trạng thái:** Đang chạy
📅 **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
    bot.reply_to(message, stats_text, parse_mode="Markdown")

# ----- USER COMMANDS -----
@bot.message_handler(commands=['start', 'ping'])
def ping(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm sử dụng bot!")
    bot.reply_to(message, "🏓 **Pong! Bot đang hoạt động!**", parse_mode="Markdown")

@bot.message_handler(commands=['help', 'menu'])
def help_command(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm sử dụng bot!")
    
    text = """
🤖 **MENU CHÍNH**

📌 **LỆNH CƠ BẢN:**
/ping - Kiểm tra bot
/help - Hiển thị menu
/groupid - Lấy ID nhóm

🌤️ **LỆNH THỜI TIẾT:**
/weather <thành_phố> - Xem thời tiết
/weather - Thời tiết mặc định (Hà Nội)

⚡ **LỆNH GIẢI TRÍ:**
/fact - Sự thật thú vị
/joke - Đùa vui
/quote - Danh ngôn
/motivate - Lời động viên
/random - Ngẫu nhiên

👑 **LỆNH ADMIN:**
/addgroup - Thêm nhóm
/delgroup - Xóa nhóm
/ban <id> - Cấm user
/unban <id> - Bỏ cấm
/broadcast - Gửi thông báo
/stats - Thống kê

📱 **LỆNH KHÁC:**
/info - Thông tin user
/time - Thời gian hiện tại
"""
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['groupid'])
def group_id(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    
    if message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, f"🆔 **Group ID:** `{message.chat.id}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Lệnh này chỉ dùng trong nhóm!")

# ----- WEATHER COMMAND -----
@bot.message_handler(commands=['weather'])
def weather_command(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    
    try:
        # Lấy tên thành phố từ lệnh
        args = message.text.split()
        if len(args) > 1:
            city = ' '.join(args[1:])
        else:
            city = "Hanoi"  # Mặc định Hà Nội
        
        # Gọi API thời tiết
        weather, error = get_weather(city)
        
        if error:
            bot.reply_to(message, f"❌ **Lỗi thời tiết:**\n{error}\n\n💡 **Gợi ý:** Dùng /weather <tên thành phố>", parse_mode="Markdown")
            return
        
        # Tạo tin nhắn thời tiết
        emoji = get_weather_emoji(weather['description'])
        
        weather_text = f"""
🌤️ **THỜI TIẾT {weather['city'].upper()}**

{emoji} **{weather['description'].capitalize()}**

🌡️ **Nhiệt độ:** {weather['temp']:.1f}°C
🤒 **Cảm giác như:** {weather['feels_like']:.1f}°C
💧 **Độ ẩm:** {weather['humidity']}%
💨 **Tốc độ gió:** {weather['wind_speed']} m/s
📊 **Áp suất:** {weather['pressure']} hPa

📅 **Cập nhật:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        bot.reply_to(message, weather_text, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Lỗi:**\n{str(e)}", parse_mode="Markdown")

# ----- ENTERTAINMENT COMMANDS -----
@bot.message_handler(commands=['fact'])
def fact(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    bot.reply_to(message, f"💡 **Sự thật thú vị:**\n{random.choice(RANDOM_FACTS)}", parse_mode="Markdown")

@bot.message_handler(commands=['joke'])
def joke(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    bot.reply_to(message, f"😂 **Đùa vui:**\n{random.choice(JOKES)}", parse_mode="Markdown")

@bot.message_handler(commands=['quote'])
def quote(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    bot.reply_to(message, f"📜 **Danh ngôn:**\n{random.choice(QUOTES)}", parse_mode="Markdown")

@bot.message_handler(commands=['motivate'])
def motivate(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    bot.reply_to(message, f"💪 **Động lực:**\n{random.choice(MOTIVATIONAL)}", parse_mode="Markdown")

@bot.message_handler(commands=['random'])
def random_command(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    
    commands = ['fact', 'joke', 'quote', 'motivate']
    cmd = random.choice(commands)
    bot.reply_to(message, f"🎲 **Ngẫu nhiên:**\nDùng lệnh `/{cmd}` để xem!", parse_mode="Markdown")

# ----- UTILITY COMMANDS -----
@bot.message_handler(commands=['info'])
def user_info(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    
    user = message.from_user
    text = f"""
👤 **THÔNG TIN USER**

📌 **ID:** `{user.id}`
📛 **Tên:** {user.first_name}
🔹 **Username:** @{user.username if user.username else 'Không có'}
⭐ **Is Bot:** {'Có' if user.is_bot else 'Không'}
🌐 **Ngôn ngữ:** {user.language_code if user.language_code else 'Không xác định'}
"""
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['time'])
def current_time(message):
    if message.from_user.id in BANNED_USERS:
        return bot.reply_to(message, "🚫 Bạn đã bị cấm!")
    
    now = datetime.now()
    text = f"""
🕐 **THỜI GIAN HIỆN TẠI**

📅 **Ngày:** {now.strftime('%d/%m/%Y')}
⏰ **Giờ:** {now.strftime('%H:%M:%S')}
📆 **Thứ:** {now.strftime('%A')}
"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ==================== MESSAGE HANDLERS ====================

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    chat_id = message.chat.id
    if str(chat_id) not in ALLOWED_GROUPS:
        return
    
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.send_message(chat_id, "🤖 Cảm ơn đã thêm tôi vào nhóm!\nDùng /help để xem các lệnh.")
            continue
        
        name = new_member.first_name
        welcome_msg = random.choice(WELCOME_MESSAGES).format(f"**{name}**")
        bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def echo(message):
    if message.from_user.id in BANNED_USERS:
        return
    
    if message.chat.type in ['group', 'supergroup']:
        if str(message.chat.id) not in ALLOWED_GROUPS:
            return
    
    if message.text and message.text.lower().startswith(('hello', 'hi', 'chào', 'xin chào')):
        replies = [
            f"Xin chào {message.from_user.first_name}! 👋",
            f"Chào bạn {message.from_user.first_name}! 😊",
            f"Hi {message.from_user.first_name}! 🌟"
        ]
        bot.reply_to(message, random.choice(replies))
    
    elif message.text and 'bot' in message.text.lower():
        bot.reply_to(message, "Tôi đây! Cần tôi giúp gì không? 🤖\nDùng /help để xem các lệnh.")
    
    elif message.text and message.text == '?':
        bot.reply_to(message, "Bạn cần giúp gì? 🤔\nDùng /help để xem các lệnh.")

# ==================== WEBHOOK ====================

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
            bot.process_new_updates([update])
            return 'ok', 200
        except Exception as e:
            print(f"Lỗi webhook: {e}")
            return 'error', 500
    else:
        return f"🤖 Bot đang chạy trên Vercel!\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

# ==================== RUN ====================
if __name__ == '__main__':
    app.run()