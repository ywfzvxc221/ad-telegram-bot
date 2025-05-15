import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# الإعدادات الافتراضية
config = {
    "daily_reward": float(os.getenv("DAILY_REWARD", 0.01)),
    "welcome_message": os.getenv("WELCOME_MESSAGE", "🎉 أهلاً وسهلاً بك في بوت الربح!"),
    "support_contact": os.getenv("SUPPORT_CONTACT", "@YourSupportUsername"),
    "ads_text": "📢 لا توجد إعلانات حالياً.",
    "video_text": "▶️ لا يوجد فيديو حالياً.",
    "visit_text": "🌐 لا يوجد موقع حالياً."
}

users = {}

# التحقق من التسجيل
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
    return True  # مبدأياً نعيد دائماً true (يمكن تعديلها لاحقًا)

def subscription_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 قناة 1", url="https://t.me/qq122311w"))
    markup.add(InlineKeyboardButton("📢 قناة 2", url="https://t.me/qqwweerrttqqyyyy"))
    markup.add(InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
    return markup

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎁 مكافأتي اليومية", callback_data="daily"),
        InlineKeyboardButton("🔗 رابط الإحالة", callback_data="referral")
    )
    markup.row(
        InlineKeyboardButton("📢 عرض الإعلانات", callback_data="ads"),
        InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")
    )
    markup.row(InlineKeyboardButton("💸 سحب الأرباح", callback_data="withdraw"))
    markup.row(InlineKeyboardButton("🛠 الدعم الفني", callback_data="support"))
    markup.row(InlineKeyboardButton("/start - الرجوع للقائمة الرئيسية", callback_data="back_to_home"))
    if user_is_admin(ADMIN_ID):
        markup.row(InlineKeyboardButton("🛠 لوحة تحكم الأدمن", callback_data="admin_panel"))
    return markup

def user_is_admin(user_id):
    return user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        register_user(user_id, message.from_user.username)

    if not check_subscription(user_id):
        bot.send_message(user_id, "❗ يرجى الاشتراك في القنوات التالية:", reply_markup=subscription_buttons())
        return

    user = get_user(user_id)
    welcome_text = f"{config['welcome_message']}\n\n💰 رصيدك الحالي: {user['balance']}$"
    bot.send_message(user_id, welcome_text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    if not is_user_registered(user_id):
        register_user(user_id, call.from_user.username)

    if call.data == "check_sub":
        if check_subscription(user_id):
            bot.send_message(user_id, "✅ تم التحقق من الاشتراك، يمكنك الآن استخدام البوت.", reply_markup=main_menu())
        else:
            bot.send_message(user_id, "❗ يرجى الاشتراك أولاً.", reply_markup=subscription_buttons())

    elif call.data == "daily":
        user = users[user_id]
        today = datetime.now().date()
        if user["last_bonus"] == str(today):
            bot.send_message(user_id, "⛔ لقد حصلت على مكافأتك اليومية اليوم بالفعل.")
        else:
            user["balance"] += config["daily_reward"]
            user["last_bonus"] = str(today)
            bot.send_message(user_id, f"✅ تم إضافة {config['daily_reward']}$ إلى رصيدك!")

    elif call.data == "referral":
        ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(user_id, f"🔗 رابط الإحالة الخاص بك:\n{ref_link}")

    elif call.data == "ads":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 إعلان قناة", url="https://t.me/qq122311w"))
        markup.add(InlineKeyboardButton("▶️ فيديو", url="https://t.me/your_channel/video"))
        markup.add(InlineKeyboardButton("🌐 موقع", url="https://example.com"))
        bot.send_message(user_id, f"{config['ads_text']}\n\n{config['video_text']}\n\n{config['visit_text']}", reply_markup=markup)

    elif call.data == "stats":
        user = get_user(user_id)
        msg = f"""📊 إحصائيات حسابك:

💰 رصيدك الحالي: {user['balance']}$
👥 عدد الإحالات: {user['referrals']}
🎁 آخر مكافأة: {user['last_bonus']}"""
        bot.send_message(user_id, msg)

    elif call.data == "withdraw":
        bot.send_message(user_id, "💸 للسحب، الحد الأدنى هو 1$. تواصل مع الدعم.")

    elif call.data == "support":
        bot.send_message(user_id, f"🛠 للتواصل مع الدعم الفني:\n{config['support_contact']}")

    elif call.data == "admin_panel" and user_is_admin(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎯 تغيير المكافأة", callback_data="set_reward"))
        markup.add(InlineKeyboardButton("📝 تعديل الترحيب", callback_data="set_welcome"))
        markup.add(InlineKeyboardButton("📢 نص الإعلان", callback_data="set_ads"))
        markup.add(InlineKeyboardButton("🎥 نص الفيديو", callback_data="set_video"))
        markup.add(InlineKeyboardButton("🌐 نص الموقع", callback_data="set_visit"))
        markup.add(InlineKeyboardButton("☎️ جهة الدعم", callback_data="set_support"))
        bot.send_message(user_id, "🛠 لوحة تحكم الأدمن:", reply_markup=markup)

    elif call.data.startswith("set_") and user_is_admin(user_id):
        setting = call.data.replace("set_", "")
        bot.send_message(user_id, f"✏️ أرسل القيمة الجديدة لـ {setting}:")
        bot.register_next_step_handler(call.message, update_setting, setting)

    elif call.data == "back_to_home":
        user = get_user(user_id)
        welcome_text = f"{config['welcome_message']}\n\n💰 رصيدك الحالي: {user['balance']}$"
        bot.send_message(user_id, welcome_text, reply_markup=main_menu())

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

bot.infinity_polling()
