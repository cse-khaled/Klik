import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# ==========================================
# 1. الإعدادات والتوكن
# ==========================================
TOKEN = '8272942530:AAE4_6wzdsUCLhleC9OSfsR4yQac3TIupWE' 
bot = telebot.TeleBot(TOKEN)

# إعدادات القناة والدعم
CHANNEL_USERNAME = "@klik_gaza"
SUPPORT_USER = "@klikgaza"

DB_FILE = "users_db.json"

# تحميل البيانات في الذاكرة
if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db_cache = json.load(f)
else:
    db_cache = {}

def save_db():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db_cache, f, indent=4, ensure_ascii=False)

# ==========================================
# 2. الدوال المساعدة
# ==========================================
def check_subscription(user_id):
    """فحص اشتراك المستخدم في القناة"""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

def get_main_menu_markup():
    """القائمة الرئيسية (تم حذف السلة منها)"""
    markup = InlineKeyboardMarkup(row_width=1) # جعلت الأزرار تحت بعضها لترتيب أفضل
    
    # رابط الدعم المباشر
    support_url = f"https://t.me/{SUPPORT_USER.replace('@','')}"
    
    markup.add(InlineKeyboardButton("🛍️ عرض خدماتنا", callback_data="services"))
    markup.add(InlineKeyboardButton("📱 تابعنا (Social Media)", callback_data="socials"))
    markup.add(InlineKeyboardButton("📞 تواصل معنا", url=support_url))
    
    return markup

# ==========================================
# 3. معالجة البداية (Start)
# ==========================================
@bot.message_handler(commands=['start', 'restart'])
def store_welcome(message):
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
    
    # 1. التحقق من الاشتراك الإجباري
    if not check_subscription(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 انضم للقناة الآن", url="https://t.me/klik_gaza"))
        markup.add(InlineKeyboardButton("✅ تم الانضمام (تحقق)", callback_data="verify_sub"))
        
        bot.send_message(chat_id, 
                         "⛔ *عذراً، لا يمكنك استخدام البوت!*\n\n"
                         "⚠️ يجب عليك الانضمام لقناة المتجر الرسمية أولاً للاستفادة من خدماتنا.\n"
                         "👇 اضغط على الرابط أدناه ثم زر التحقق:", 
                         reply_markup=markup, parse_mode="Markdown")
        return

    # 2. الدخول المباشر (تثبيت العربية)
    if chat_id not in db_cache: db_cache[chat_id] = {}
    db_cache[chat_id]['lang'] = 'ar'
    save_db()

    bot.send_message(chat_id, 
                     f"👋 أهلاً بك {message.from_user.first_name} في *متجر كليك*،\n"
                     "الرجاء الاختيار من القائمة أدناه 👇", 
                     reply_markup=get_main_menu_markup(), 
                     parse_mode="Markdown")

# ==========================================
# 4. معالج الأزرار (Callbacks)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = str(call.message.chat.id)
    user_id = call.from_user.id
    support_url = f"https://t.me/{SUPPORT_USER.replace('@','')}"

    # --- التحقق من الانضمام ---
    if call.data == "verify_sub":
        if check_subscription(user_id):
            bot.delete_message(chat_id, call.message.message_id)
            store_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ لم تنضم للقناة بعد!", show_alert=True)
        return

    # --- قسم عرض الخدمات (مع زر الطلب الخاص) ---
    elif call.data == "services":
        services_text = """
🛍️ *قائمة خدمات متجر كليك:*

🤖 *الذكاء الاصطناعي (AI):*
▫️ ChatGPT Plus | Go
▫️ Midjourney
▫️ Perplexity
▫️ Manus AI
▫️ Google Pro

📺 *الترفيه والمشاهدة:*
▫️ Netflix
▫️ YouTube Premium
▫️ Spotify
▫️ Crunchyroll

🎨 *التصميم والعمل:*
▫️ Canva Pro
▫️ LinkedIn Premium
▫️ Autodesk
▫️ Filmora

🎮 *الألعاب:*
▫️ شحن في جميع الألعاب
▫️ خدمات الألعاب الإلكترونية
▫️ جميع برامج الألعاب والحاسوب

📚 *التعليم:*
▫️ Duolingo

👇 *اختر ما يناسبك:*
"""
        markup = InlineKeyboardMarkup(row_width=1)
        # زر طلب خدمة من القائمة
        markup.add(InlineKeyboardButton("🛒 طلب خدمة من القائمة أعلاه", url=support_url))
        # زر طلب خدمة غير موجودة (الجديد)
        markup.add(InlineKeyboardButton("💡 خدمتك مش موجودة؟ اطلبها الآن!", url=support_url))
        # زر الرجوع
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        
        bot.edit_message_text(services_text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # --- السوشيال ميديا ---
    elif call.data == "socials":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("📘 Facebook", url="https://facebook.com/YOUR_FB"),
                   InlineKeyboardButton("📸 Instagram", url="https://instagram.com/klik.gaza"),
                   InlineKeyboardButton("💚 WhatsApp", url="https://wa.me/972592273086"),
                   InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text("📱 *تابعنا على منصاتنا الرسمية:*", 
                              chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # --- الرجوع للقائمة الرئيسية ---
    elif call.data == "back_main":
        bot.edit_message_text(f"👋 أهلاً بك {call.from_user.first_name} في *متجر كليك*،\nالرجاء الاختيار من القائمة أدناه 👇", 
                              chat_id, call.message.message_id, 
                              reply_markup=get_main_menu_markup(), parse_mode="Markdown")

    bot.answer_callback_query(call.id)

# ==========================================
# 5. التشغيل
# ==========================================
bot.set_my_commands([BotCommand("start", "تشغيل المتجر")])
print("🚀 متجر كليك يعمل الآن (تم حذف السلة + إضافة زر الطلب الخاص)...")
bot.infinity_polling()