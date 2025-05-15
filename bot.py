import telebot
from telebot import types
import os

# قراءة البيانات من متغيرات البيئة
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

bot = telebot.TeleBot(TOKEN)

# رسالة الترحيب الافتراضية
welcome_message = "مرحبًا بك في البوت الربحي!"

# لوحة الأزرار الرئيسية
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('💰 Balance', '📈 Ref Stats')
    markup.row('💵 Withdraw', '💸 Earn More')
    markup.row('🎁 Bonus', '📰 الإعلانات')
    return markup

# لوحة تحكم الأدمن
def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📤 إرسال رسالة للجميع', '📝 تعديل الترحيب')
    markup.row('➕ إضافة إعلان', '📊 إحصائيات')
    markup.row('⬅️ رجوع')
    return markup

ads = []

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, welcome_message, reply_markup=main_menu())

# التعامل مع الأزرار العامة
@bot.message_handler(func=lambda message: True)
def handle_user(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id == ADMIN_ID and text == "/admin":
        bot.send_message(chat_id, "لوحة تحكم الأدمن:", reply_markup=admin_menu())
        return

    if chat_id == ADMIN_ID:
        handle_admin(message)
        return

    # أزرار المستخدم العادي
    if text == '💰 Balance':
        bot.send_message(chat_id, "رصيدك الحالي: 0$", reply_markup=main_menu())
    elif text == '📈 Ref Stats':
        bot.send_message(chat_id, "عدد الإحالات: 0", reply_markup=main_menu())
    elif text == '💵 Withdraw':
        bot.send_message(chat_id, "الحد الأدنى للسحب: 100$", reply_markup=main_menu())
    elif text == '💸 Earn More':
        bot.send_message(chat_id, "اربح المزيد من خلال رابط الإحالة.", reply_markup=main_menu())
    elif text == '🎁 Bonus':
        bot.send_message(chat_id, "مكافأتك اليومية: 0.003$", reply_markup=main_menu())
    elif text == '📰 الإعلانات':
        if not ads:
            bot.send_message(chat_id, "لا توجد إعلانات حالياً.", reply_markup=main_menu())
        else:
            for ad in ads:
                bot.send_message(chat_id, ad, disable_web_page_preview=True)
    else:
        bot.send_message(chat_id, "يرجى اختيار زر من القائمة.", reply_markup=main_menu())

# التعامل مع الأدمن
def handle_admin(message):
    global welcome_message
    text = message.text
    chat_id = message.chat.id

    if text == '📤 إرسال رسالة للجميع':
        msg = bot.send_message(chat_id, "أرسل الرسالة التي تريد نشرها:")
        bot.register_next_step_handler(msg, broadcast_message)
    elif text == '📝 تعديل الترحيب':
        msg = bot.send_message(chat_id, "أرسل رسالة الترحيب الجديدة:")
        bot.register_next_step_handler(msg, set_welcome_message)
    elif text == '➕ إضافة إعلان':
        msg = bot.send_message(chat_id, "أرسل نص الإعلان:")
        bot.register_next_step_handler(msg, add_ad)
    elif text == '📊 إحصائيات':
        bot.send_message(chat_id, f"عدد المستخدمين: {len(bot.get_chat_administrators(chat_id))}", reply_markup=admin_menu())
    elif text == '⬅️ رجوع':
        bot.send_message(chat_id, "تم الرجوع إلى القائمة الرئيسية.", reply_markup=main_menu())

def broadcast_message(message):
    # إرسال الرسالة لكل المستخدمين (هنا نرسل فقط للأدمن كتمثيل)
    bot.send_message(ADMIN_ID, f"تم إرسال الرسالة:\n\n{message.text}", reply_markup=admin_menu())

def set_welcome_message(message):
    global welcome_message
    welcome_message = message.text
    bot.send_message(ADMIN_ID, "تم تحديث رسالة الترحيب.", reply_markup=admin_menu())

def add_ad(message):
    ads.append(message.text)
    bot.send_message(ADMIN_ID, "تمت إضافة الإعلان بنجاح.", reply_markup=admin_menu())

bot.infinity_polling()
