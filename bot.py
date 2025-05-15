import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

config = {
    "daily_reward": 0.01,
    "welcome_message": "أهلاً وسهلاً بك في بوت الربح!",
    "support_contact": "@YourSupportUsername"
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

def subscription_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("قناة 1", url="https://t.me/qq122311w"))
    markup.add(InlineKeyboardButton("قناة 2", url="https://t.me/qqwweerrttqqyyyy"))
    markup.add(InlineKeyboardButton("تحقق من الاشتراك", callback_data="check_sub"))
    return markup

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("مكافأتي اليومية", callback_data="daily"),
        InlineKeyboardButton("رابط الإحالة", callback_data="referral")
    )
    markup.row(
        InlineKeyboardButton("عرض الإعلانات", callback_data="ads"),
        InlineKeyboardButton("إحصائياتي", callback_data="stats")
    )
    markup.row(InlineKeyboardButton("سحب الأرباح", callback_data="withdraw"))
    markup.row(InlineKeyboardButton("الدعم الفني", callback_data="support"))
    if user_is_admin(ADMIN_ID):
        markup.row(InlineKeyboardButton("لوحة تحكم الأدمن", callback_data="admin_panel"))
    return markup

def user_is_admin(user_id):
    return user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        register_user(user_id, message.from_user.username)

    if not check_subscription(user_id):
        bot.send_message(user_id, "يرجى الاشتراك في القنوات التالية:", reply_markup=subscription_buttons())
        return

    user = get_user(user_id)
    welcome_text = f"{config['welcome_message']}\n\nرصيدك الحالي: {user['balance']}$"
    bot.send_message(user_id, welcome_text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    if not is_user_registered(user_id):
        register_user(user_id, call.from_user.username)

    if call.data == "check_sub":
        if check_subscription(user_id):
            bot.send_message(user_id, "تم التحقق من الاشتراك، يمكنك الآن استخدام البوت.", reply_markup=main_menu())
        else:
            bot.send_message(user_id, "يرجى الاشتراك أولاً.", reply_markup=subscription_buttons())

    elif call.data == "daily":
        user = users[user_id]
        today = datetime.now().date()
        if user["last_bonus"] == str(today):
            bot.send_message(user_id, "لقد حصلت على مكافأتك اليومية اليوم بالفعل.")
        else:
            user["balance"] += config["daily_reward"]
            user["last_bonus"] = str(today)
            bot.send_message(user_id, f"تم إضافة {config['daily_reward']}$ إلى رصيدك!")

    elif call.data == "referral":
        ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(user_id, f"رابط الإحالة الخاص بك:\n{ref_link}")

    elif call.data == "ads":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("اشتراك في القنوات", url="https://t.me/qq122311w"))
        markup.add(InlineKeyboardButton("مشاهدة فيديو", url="https://t.me/your_channel/video"))
        markup.add(InlineKeyboardButton("زيارة موقع", url="https://example.com"))
        bot.send_message(user_id, "اختر نوع الإعلان:", reply_markup=markup)

    elif call.data == "stats":
        user = get_user(user_id)
        msg = f"""إحصائيات حسابك:
رصيدك الحالي: {user['balance']}$
عدد الإحالات: {user['referrals']}
آخر مكافأة: {user['last_bonus']}"""
        bot.send_message(user_id, msg)

    elif call.data == "withdraw":
        bot.send_message(user_id, "للسحب، الحد الأدنى هو 1$. تواصل مع الدعم.")

    elif call.data == "support":
        bot.send_message(user_id, f"للتواصل مع الدعم الفني:\n{config['support_contact']}")

    elif call.data == "admin_panel" and user_is_admin(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("تغيير المكافأة اليومية", callback_data="set_reward"))
        markup.add(InlineKeyboardButton("تعديل رسالة الترحيب", callback_data="set_welcome"))
        markup.add(InlineKeyboardButton("تعديل جهة الدعم", callback_data="set_support"))
        bot.send_message(user_id, "لوحة تحكم الأدمن:", reply_markup=markup)

    elif call.data == "set_reward" and user_is_admin(user_id):
        bot.send_message(user_id, "أرسل القيمة الجديدة للمكافأة اليومية بصيغة: `/setreward 0.02`", parse_mode="Markdown")

    elif call.data == "set_welcome" and user_is_admin(user_id):
        bot.send_message(user_id, "أرسل رسالة الترحيب الجديدة بصيغة: `/setwelcome أهلاً بك في البوت!`", parse_mode="Markdown")

    elif call.data == "set_support" and user_is_admin(user_id):
        bot.send_message(user_id, "أرسل جهة الدعم الجديدة بصيغة: `/setsupport @support`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: user_is_admin(m.from_user.id))
def handle_admin_input(message):
    if message.text.startswith("/setreward "):
        try:
            value = float(message.text.split()[1])
            config["daily_reward"] = value
            bot.reply_to(message, f"تم تعيين المكافأة إلى {value}$")
        except:
            bot.reply_to(message, "يرجى إرسال رقم صحيح. مثال: `/setreward 0.02`", parse_mode="Markdown")

    elif message.text.startswith("/setwelcome "):
        config["welcome_message"] = message.text.replace("/setwelcome ", "")
        bot.reply_to(message, "تم تحديث رسالة الترحيب.")

    elif message.text.startswith("/setsupport "):
        config["support_contact"] = message.text.replace("/setsupport ", "")
        bot.reply_to(message, "تم تحديث جهة الدعم.")

bot.infinity_polling()
