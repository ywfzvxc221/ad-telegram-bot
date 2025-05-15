import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# إعدادات افتراضية
config = {
    "daily_reward": float(os.getenv("DAILY_REWARD", 0.01)),
    "welcome_message": os.getenv("WELCOME_MESSAGE", "🎉 أهلاً وسهلاً بك في بوت الربح!"),
    "support_contact": os.getenv("SUPPORT_CONTACT", "@YourSupportUsername"),
    "ads_text": "📢 لا توجد إعلانات حالياً.",
    "video_text": "▶️ لا يوجد فيديو حالياً.",
    "visit_text": "🌐 لا يوجد موقع حالياً."
}

users = {}

def is_user_registered(user_id):
    return user_id in users

def register_user(user_id, username):
    users[user_id] = {
        "username": username,
        "balance": 0.0,
        "referrals": 0,
        "last_bonus": "لا يوجد"
    }

def get_user(user_id):
    return users.get(user_id, {
        "balance": 0.0,
        "referrals": 0,
        "last_bonus": "لا يوجد"
    })

def check_subscription(user_id):
    return True

def user_is_admin(user_id):
    return user_id == ADMIN_ID

# الأزرار الأساسية
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 مكافأتي اليومية", "🔗 رابط الإحالة")
    markup.add("📢 عرض الإعلانات", "📊 إحصائياتي")
    markup.add("💸 سحب الأرباح", "🛠 الدعم الفني")
    if user_is_admin(ADMIN_ID):
        markup.add("🛠 لوحة تحكم الأدمن")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        register_user(user_id, message.from_user.username)

    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 قناة 1", url="https://t.me/qq122311w"))
        markup.add(InlineKeyboardButton("📢 قناة 2", url="https://t.me/qqwweerrttqqyyyy"))
        markup.add(InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
        bot.send_message(user_id, "❗ يرجى الاشتراك في القنوات التالية:", reply_markup=markup)
        return

    user = get_user(user_id)
    welcome_text = f"{config['welcome_message']}\n\n💰 رصيدك الحالي: {user['balance']}$"
    if os.path.exists("welcome_image.png"):
        with open("welcome_image.png", "rb") as img:
            bot.send_photo(user_id, img, caption=welcome_text, reply_markup=main_menu())
    else:
        bot.send_message(user_id, welcome_text, reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🎁 مكافأتي اليومية")
def daily_bonus(message):
    user = users[message.from_user.id]
    today = datetime.now().date()
    if user["last_bonus"] == str(today):
        bot.reply_to(message, "⛔ لقد حصلت على مكافأتك اليومية اليوم بالفعل.")
    else:
        user["balance"] += config["daily_reward"]
        user["last_bonus"] = str(today)
        bot.reply_to(message, f"✅ تم إضافة {config['daily_reward']}$ إلى رصيدك!")

@bot.message_handler(func=lambda m: m.text == "🔗 رابط الإحالة")
def referral_link(message):
    user_id = message.from_user.id
    ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    bot.reply_to(message, f"🔗 رابط الإحالة الخاص بك:\n{ref_link}")

@bot.message_handler(func=lambda m: m.text == "📢 عرض الإعلانات")
def show_ads(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 إعلان قناة", url="https://t.me/qq122311w"))
    markup.add(InlineKeyboardButton("▶️ فيديو", url="https://t.me/your_channel/video"))
    markup.add(InlineKeyboardButton("🌐 موقع", url="https://example.com"))
    bot.send_message(message.chat.id, f"{config['ads_text']}\n\n{config['video_text']}\n\n{config['visit_text']}", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 إحصائياتي")
def stats(message):
    user = get_user(message.from_user.id)
    msg = f"""📊 إحصائيات حسابك:

💰 رصيدك الحالي: {user['balance']}$
👥 عدد الإحالات: {user['referrals']}
🎁 آخر مكافأة: {user['last_bonus']}"""
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "💸 سحب الأرباح")
def withdraw(message):
    bot.reply_to(message, "💸 للسحب، الحد الأدنى هو 1$. تواصل مع الدعم.")

@bot.message_handler(func=lambda m: m.text == "🛠 الدعم الفني")
def support(message):
    bot.reply_to(message, f"🛠 للتواصل مع الدعم الفني:\n{config['support_contact']}")

@bot.message_handler(func=lambda m: m.text == "🛠 لوحة تحكم الأدمن")
def admin_panel(message):
    if not user_is_admin(message.from_user.id): return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎯 تغيير المكافأة", callback_data="set_reward"))
    markup.add(InlineKeyboardButton("📝 تعديل الترحيب", callback_data="set_welcome"))
    markup.add(InlineKeyboardButton("📢 نص الإعلان", callback_data="set_ads"))
    markup.add(InlineKeyboardButton("🎥 نص الفيديو", callback_data="set_video"))
    markup.add(InlineKeyboardButton("🌐 نص الموقع", callback_data="set_visit"))
    markup.add(InlineKeyboardButton("☎️ جهة الدعم", callback_data="set_support"))
    markup.add(InlineKeyboardButton("🗑 حذف صورة الترحيب", callback_data="delete_welcome_image"))
    bot.send_message(message.chat.id, "🛠 لوحة تحكم الأدمن:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if call.data == "check_sub":
        if check_subscription(user_id):
            bot.send_message(user_id, "✅ تم التحقق من الاشتراك، يمكنك الآن استخدام البوت.", reply_markup=main_menu())
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📢 قناة 1", url="https://t.me/qq122311w"))
            markup.add(InlineKeyboardButton("📢 قناة 2", url="https://t.me/qqwweerrttqqyyyy"))
            markup.add(InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
            bot.send_message(user_id, "❗ يرجى الاشتراك أولاً.", reply_markup=markup)

    elif call.data == "delete_welcome_image" and user_is_admin(user_id):
        try:
            os.remove("welcome_image.png")
            bot.send_message(user_id, "✅ تم حذف صورة الترحيب بنجاح.")
        except FileNotFoundError:
            bot.send_message(user_id, "⚠️ لا توجد صورة ترحيب حالياً.")

    elif call.data.startswith("set_") and user_is_admin(user_id):
        setting = call.data.replace("set_", "")
        bot.send_message(user_id, f"✏️ أرسل القيمة الجديدة لـ {setting}:")
        bot.register_next_step_handler(call.message, update_setting, setting)

def update_setting(message, key):
    value = message.text
    if key == "reward":
        try:
            config["daily_reward"] = float(value)
            bot.reply_to(message, f"✅ تم تحديث المكافأة اليومية إلى {value}$")
        except:
            bot.reply_to(message, "❗ يرجى إرسال رقم صحيح.")
    else:
        config_key = f"{key}_text" if key in ["ads", "video", "visit"] else f"{key}_message" if key == "welcome" else "support_contact"
        config[config_key] = value
        bot.reply_to(message, f"✅ تم تحديث {key} بنجاح.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if user_is_admin(message.from_user.id):
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("welcome_image.png", "wb") as f:
            f.write(downloaded_file)
        bot.reply_to(message, "✅ تم تعيين صورة الترحيب بنجاح.")

bot.infinity_polling()
