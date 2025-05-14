import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

# ====== بيانات البوت من متغيرات البيئة ======
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_USERNAME = os.getenv("FORCE_CHANNELS").split(",")[0]
FORCE_SUB_CHANNELS = os.getenv("FORCE_CHANNELS").split(",")
PROOF_CHANNEL = os.getenv("PROOF_CHANNEL")
FAUCETPAY_EMAIL = os.getenv("FAUCETPAY_EMAIL")

bot = telebot.TeleBot(TOKEN)

# ====== قواعد بيانات مؤقتة ======
referrals = {}
balances = {}
last_daily_reward = {}
ad_list = []
user_seen_ads = {}

custom_prices = "💵 قائمة الأسعار:\n\n- تمويل 100 عضو: 5$\n- تمويل 200 عضو: 10$\n- تمويل 500 عضو: 20$"
contact_link = "https://t.me/your_username"

# ====== التحقق من الاشتراك ======
def check_subscription(user_id):
    for ch in FORCE_SUB_CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ['member', 'creator', 'administrator']:
                return False
        except:
            return False
    return True

# ====== قائمة الأزرار الرئيسية ======
def main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💰 السحب", callback_data="withdraw"))
    markup.add(InlineKeyboardButton("🎁 المكافأة اليومية", callback_data="daily"))
    markup.add(InlineKeyboardButton("👥 دعوة الأصدقاء", callback_data="invite"))
    markup.add(InlineKeyboardButton("📢 عرض الإعلانات", callback_data="view_ads"))
    markup.add(InlineKeyboardButton("💼 اطلب تمويل", callback_data="order"))
    markup.add(InlineKeyboardButton("💵 الأسعار", callback_data="prices"))
    markup.add(InlineKeyboardButton("⚙️ الإحصائيات", callback_data="stats"))
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("🛠️ لوحة تحكم الأدمن", callback_data="admin_panel"))
    return markup

# ====== /start ======
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

    markup = main_menu(user_id)
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

# ====== ردود الأزرار ======
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
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 مشاركة الرابط", switch_inline_query=ref_link))
        bot.send_message(user_id,
            f"👥 رابط دعوتك:\n{ref_link}\n\n"
            f"عدد الإحالات: {count}\n"
            f"الأرباح: {earnings}$\n"
            "✅ ستحصل على 5$ مقابل كل إحالة ناجحة!",
            reply_markup=markup
        )

    elif call.data == "withdraw":
        earnings = balances.get(str(user_id), 0)
        if earnings >= 100:
            msg = bot.send_message(user_id, "💼 أرسل عنوان محفظتك (FaucetPay أو Binance) + الوسيلة:")
            bot.register_next_step_handler(msg, process_withdrawal)
        else:
            bot.send_message(user_id, f"❌ لا يمكنك السحب الآن. الحد الأدنى هو 100 دولار.\nرصيدك الحالي: {earnings}$")

    elif call.data == "daily":
        now = datetime.now()
        last = last_daily_reward.get(str(user_id), now - timedelta(days=1, minutes=1))
        if now - last >= timedelta(days=1):
            balances[str(user_id)] = balances.get(str(user_id), 0) + 5
            last_daily_reward[str(user_id)] = now
            bot.send_message(user_id, "✅ تم منحك 5$ كمكافأة يومية!")
        else:
            bot.send_message(user_id, "⏳ لقد حصلت على مكافأتك اليوم، عد غدًا!")

    elif call.data == "view_ads":
        ads = [ad for ad in ad_list if str(user_id) not in user_seen_ads.get(ad['url'], set())]
        if not ads:
            bot.send_message(user_id, "📢 لا توجد إعلانات حالياً.")
            return
        for ad in ads:
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("✅ اشترك في القناة", url=ad['url']),
                InlineKeyboardButton("تحقّق من الاشتراك", callback_data=f"verify_ad|{ad['url']}")
            )
            bot.send_message(user_id, ad['text'], reply_markup=markup)

    elif call.data.startswith("verify_ad"):
        _, url = call.data.split("|", 1)
        channel_username = url.split("https://t.me/")[-1]
        try:
            status = bot.get_chat_member(f"@{channel_username}", user_id).status
            if status in ['member', 'administrator', 'creator']:
                balances[str(user_id)] = balances.get(str(user_id), 0) + 1
                user_seen_ads.setdefault(url, set()).add(str(user_id))
                bot.send_message(user_id, "✅ تم التحقق من اشتراكك وحصلت على 1$")
            else:
                bot.send_message(user_id, "❌ تأكد من الاشتراك أولاً.")
        except:
            bot.send_message(user_id, "⚠️ حدث خطأ أثناء التحقق. تأكد أن القناة متاحة.")

    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✏️ تغيير الأسعار", callback_data="edit_prices"),
            InlineKeyboardButton("✉️ تغيير رابط التواصل", callback_data="edit_contact"),
            InlineKeyboardButton("📢 إرسال إعلان", callback_data="add_ad"),
            InlineKeyboardButton("🛠️ إدارة المكافآت والمهام", callback_data="manage_rewards")
        )
        bot.send_message(user_id, "🛠️ لوحة تحكم الأدمن:", reply_markup=markup)

    elif call.data == "manage_rewards" and user_id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✏️ تغيير المكافأة اليومية", callback_data="edit_daily_reward"),
            InlineKeyboardButton("✏️ إضافة مهمة جديدة", callback_data="add_task")
        )
        bot.send_message(user_id, "📋 إدارة المكافآت والمهام:", reply_markup=markup)

    # إضافة تفاصيل مع المهام
    elif call.data == "edit_daily_reward" and user_id == ADMIN_ID:
        msg = bot.send_message(user_id, "✏️ أرسل المكافأة اليومية الجديدة:")
        bot.register_next_step_handler(msg, update_daily_reward)

    elif call.data == "add_task" and user_id == ADMIN_ID:
        msg = bot.send_message(user_id, "📋 اكتب تفاصيل المهمة الجديدة (مثل: الاشتراك في قناة):")
        bot.register_next_step_handler(msg, add_new_task)

# ====== دوال ثانوية ======
def update_daily_reward(message):
    # تحديث المكافأة اليومية
    pass

def add_new_task(message):
    # إضافة مهمة جديدة
    pass
