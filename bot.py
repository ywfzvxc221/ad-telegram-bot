import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_USERNAME = '@qqwweerrttqqyyyy'
FORCE_SUB_CHANNELS = ['@qq122311w', '@qqwweerrttqqyyyy']

bot = telebot.TeleBot(TOKEN)

referrals = {}
balances = {}
custom_prices = "💵 قائمة الأسعار:\n\n- تمويل 100 عضو: 5$\n- تمويل 200 عضو: 10$\n- تمويل 500 عضو: 20$"
contact_link = "https://t.me/your_username"  # يمكن للإدمن تغييره لاحقًا

def check_subscription(user_id):
    for ch in FORCE_SUB_CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ['member', 'creator', 'administrator']:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        for ch in FORCE_SUB_CHANNELS:
            markup.add(InlineKeyboardButton(f"اشترك في {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_sub"))
        bot.send_message(user_id, "⚠️ يجب الاشتراك في القنوات التالية أولاً لمتابعة استخدام البوت:", reply_markup=markup)
        return

    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        if ref_id != str(user_id):
            referrals.setdefault(ref_id, set()).add(user_id)
            balances[ref_id] = balances.get(ref_id, 0) + 5

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("📝 طلب تمويل إعلان", callback_data='order'),
        InlineKeyboardButton("💵 الأسعار", callback_data='prices'),
        InlineKeyboardButton("📊 إحصائيات القناة", callback_data='stats'),
        InlineKeyboardButton("👥 دعوة الأصدقاء", callback_data='invite'),
        InlineKeyboardButton("💰 سحب الأرباح", callback_data='withdraw'),
        InlineKeyboardButton("📩 تواصل معنا", url=contact_link)
    )

    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("🛠️ لوحة تحكم الأدمن", callback_data='admin_panel'))

    bot.send_message(
        user_id,
        f"أهلًا {message.from_user.first_name}،\n"
        "مرحباً بك في بوت تمويل القنوات الاحترافي!\n"
        "✅ اجمع الأرباح من دعوة الأصدقاء\n"
        "💰 واطلب السحب عند وصولك إلى 100 دولار\n"
        "✨ خدمات إعلانية سريعة وفعالة\n\n"
        "اختر من الأزرار التالية:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if call.data == "check_sub":
        if check_subscription(user_id):
            bot.send_message(user_id, "✅ تم التحقق من الاشتراك بنجاح، ارسل /start للمتابعة.")
        else:
            bot.answer_callback_query(call.id, "❌ لم تكمل الاشتراك في القنوات.")
    elif call.data == "order":
        msg = bot.send_message(user_id, "📝 اكتب تفاصيل إعلانك (رابط القناة + النص)...")
        bot.register_next_step_handler(msg, receive_ad)
    elif call.data == "prices":
        bot.send_message(user_id, custom_prices)
    elif call.data == "stats":
        try:
            members = bot.get_chat_member_count(CHANNEL_USERNAME)
            bot.send_message(user_id, f"📊 عدد أعضاء القناة: {members}")
        except Exception as e:
            bot.send_message(user_id, f"⚠️ لم أتمكن من جلب الإحصائيات: {e}")
    elif call.data == "invite":
        ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        count = len(referrals.get(str(user_id), []))
        earnings = balances.get(str(user_id), 0)
        bot.send_message(user_id,
            f"👥 رابط دعوتك:\n{ref_link}\n\n"
            f"عدد الإحالات: {count}\n"
            f"الأرباح: {earnings}$\n"
            "✅ ستحصل على 5$ مقابل كل إحالة ناجحة!"
        )
    elif call.data == "withdraw":
        earnings = balances.get(str(user_id), 0)
        if earnings >= 100:
            msg = bot.send_message(user_id, "💼 أرسل عنوان محفظتك (FaucetPay أو Binance) + الوسيلة:")
            bot.register_next_step_handler(msg, process_withdrawal)
        else:
            bot.send_message(user_id, f"❌ لا يمكنك السحب الآن. الحد الأدنى هو 100 دولار.\nرصيدك الحالي: {earnings}$")
    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✏️ تغيير الأسعار", callback_data="edit_prices"),
            InlineKeyboardButton("✉️ تغيير رابط التواصل", callback_data="edit_contact"),
            InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="broadcast")
        )
        bot.send_message(user_id, "🛠️ لوحة تحكم الأدمن:", reply_markup=markup)
    elif call.data == "edit_prices" and user_id == ADMIN_ID:
        msg = bot.send_message(user_id, "✏️ أرسل النص الجديد لقائمة الأسعار:")
        bot.register_next_step_handler(msg, update_prices)
    elif call.data == "edit_contact" and user_id == ADMIN_ID:
        msg = bot.send_message(user_id, "✏️ أرسل الرابط الجديد للتواصل:")
        bot.register_next_step_handler(msg, update_contact)
    elif call.data == "broadcast" and user_id == ADMIN_ID:
        msg = bot.send_message(user_id, "📢 أرسل الرسالة التي تريد إرسالها للجميع:")
        bot.register_next_step_handler(msg, broadcast_message)

def update_prices(message):
    global custom_prices
    custom_prices = message.text
    bot.send_message(message.chat.id, "✅ تم تحديث قائمة الأسعار.")

def update_contact(message):
    global contact_link
    contact_link = message.text
    bot.send_message(message.chat.id, "✅ تم تحديث رابط التواصل.")

def broadcast_message(message):
    for user_id in balances.keys():
        try:
            bot.send_message(user_id, message.text)
        except:
            continue
    bot.send_message(message.chat.id, "✅ تم إرسال الرسالة لجميع المستخدمين.")

def process_withdrawal(message):
    user_id = message.from_user.id
    details = message.text
    bot.send_message(ADMIN_ID, f"💸 طلب سحب من المستخدم {user_id}:\n\n{details}")
    bot.send_message(user_id, "✅ تم استلام طلب السحب، سيتم مراجعته خلال 24 ساعة.")

def receive_ad(message):
    ad_info = f"📢 إعلان جديد من {message.from_user.first_name} (@{message.from_user.username}):\n\n"
    if message.text:
        ad_info += message.text
    elif message.caption:
        ad_info += message.caption

    bot.send_message(ADMIN_ID, ad_info)
    if message.content_type != 'text':
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    bot.send_message(message.chat.id, "✅ تم استلام طلبك، سيتم التواصل معك قريبًا لإتمام العملية.")

print("🚀 البوت يعمل الآن...")
bot.infinity_polling()
