# =========================================
# PREMIUM TELEGRAM STORE BOT
# FULL PREMIUM UI FIXED VERSION
# BIG BUTTONS + PREMIUM TEXT
# COMMAND LIST REMOVED
# MENU BUTTON REMOVED
# =========================================

import os
import json
import logging
import random
import string

from datetime import datetime, timezone, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# =========================================
# CONFIG
# =========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
UPI_ID = os.environ.get("UPI_ID", "example@upi")

OWNER_USERNAME = "SATYAM_X_OFC"

IST = timezone(timedelta(hours=5, minutes=30))

DB_FILE = "user_data.json"

PRODUCTS = {
    "🔥 1 Day Premium Key": 80,
    "⚡ 1 Month Premium Key": 99,
    "💎 1 Year Premium Key": 499,
    "👑 Lifetime Premium Key": 999,
}

# =========================================
# TIME
# =========================================

def current_time():
    return datetime.now(IST).strftime("%d/%m/%Y %I:%M:%S %p")

# =========================================
# DATABASE
# =========================================

def load_data():

    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)

    except:
        return {}

def save_data(data):

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(user_id):

    data = load_data()

    if user_id not in data:

        data[user_id] = {
            "name": "",
            "username": "",
            "joined": current_time(),
            "last_activity": current_time(),
            "total_orders": 0,
            "orders": [],
            "referral_earnings": 0,
            "total_refers": 0,
            "referred_users": []
        }

        save_data(data)

    return data[user_id]

def update_user(user_id, updates):

    data = load_data()

    if user_id not in data:
        get_user(user_id)

    data = load_data()

    data[user_id].update(updates)

    data[user_id]["last_activity"] = current_time()

    save_data(data)

# =========================================
# MAIN MENU BUTTONS
# =========================================

def main_menu_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "━━━━━━━━━━━━━━━",
                callback_data="none"
            )
        ],

        [
            InlineKeyboardButton(
                "🛒 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐇𝐎𝐏 🛒",
                callback_data="shop_now"
            )
        ],

        [
            InlineKeyboardButton(
                "📦 𝐌𝐘 𝐎𝐑𝐃𝐄𝐑𝐒 📦",
                callback_data="my_orders"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 𝐌𝐘 𝐏𝐑𝐎𝐅𝐈𝐋𝐄 👤",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "📖 𝐇𝐎𝐖 𝐓𝐎 𝐔𝐒𝐄 📖",
                callback_data="how_to_use"
            )
        ],

        [
            InlineKeyboardButton(
                "💬 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐔𝐏𝐏𝐎𝐑𝐓 💬",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 𝐑𝐄𝐅𝐄𝐑 & 𝐄𝐀𝐑𝐍 💰",
                callback_data="refer_earn"
            )
        ],

        [
            InlineKeyboardButton(
                "━━━━━━━━━━━━━━━",
                callback_data="none"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = str(user.id)

    user_data = get_user(user_id)

    if not user_data["name"]:

        update_user(user_id, {
            "name": user.full_name,
            "username": user.username or ""
        })

    text = (
        "╔══════════════════╗\n"
        " 👋 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 👋\n"
        " 💎 𝐁𝐄𝐒𝐓 𝐂𝐇𝐄𝐀𝐓 𝐒𝐇𝐎𝐏 💎\n"
        "╚══════════════════╝\n\n"

        "❄️ Here you can purchase all\n"
        "premium telegram hacks for\n"
        "Android & IOS devices 💥\n\n"

        "⚡ Instant Delivery\n"
        "💎 Premium Quality\n"
        "🔥 24/7 Support\n"
        "🚀 Fast Service\n\n"

        "👇 Select any premium option below 👇"
    )

    await update.message.reply_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
        reply_markup_remove=True if False else None
    )

# =========================================
# MAIN MENU
# =========================================

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "╔══════════════════╗\n"
        " 🏠 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐌𝐄𝐍𝐔 🏠\n"
        "╚══════════════════╝\n\n"

        "💎 Choose any premium option\n"
        "from below buttons 👇"
    )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

# =========================================
# SHOP
# =========================================

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    keyboard = []

    for name, price in PRODUCTS.items():

        keyboard.append([
            InlineKeyboardButton(
                f"{name} ➜ ₹{price}",
                callback_data=f"buy_{name}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐄𝐍𝐔",
            callback_data="main_menu"
        )
    ])

    text = (
        "🛒 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐇𝐎𝐏 🛒\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "💎 Select your premium plan\n"
        "from below 👇"
    )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# BUY PRODUCT
# =========================================

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_name = query.data.replace("buy_", "")

    price = PRODUCTS.get(product_name)

    try:
        await query.message.delete()
    except:
        pass

    keyboard = [

        [
            InlineKeyboardButton(
                "✅ 𝐈 𝐇𝐀𝐕𝐄 𝐏𝐀𝐈𝐃",
                callback_data=f"paid_{product_name}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ 𝐁𝐀𝐂𝐊",
                callback_data="shop_now"
            )
        ]
    ]

    text = (
        "💸 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐒𝐄𝐂𝐓𝐈𝐎𝐍 💸\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"📦 Product : {product_name}\n"
        f"💰 Amount : ₹{price}\n\n"

        f"💳 UPI ID :\n"
        f"`{UPI_ID}`\n\n"

        "⚠️ Pay exact amount only."
    )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# =========================================
# PAYMENT
# =========================================

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product = query.data.replace("paid_", "")

    context.user_data["pending_product"] = product

    try:
        await query.message.delete()
    except:
        pass

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "✅ 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃\n\n"
            "💬 Send your UPI registered name"
        )
    )

# =========================================
# HANDLE MESSAGE
# =========================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "pending_product" not in context.user_data:
        return

    user_id = str(update.effective_user.id)

    product = context.user_data["pending_product"]

    price = PRODUCTS.get(product)

    key = ''.join(random.choices(
        string.ascii_uppercase + string.digits,
        k=16
    ))

    user_data = get_user(user_id)

    orders = user_data.get("orders", [])

    orders.append({
        "product": product,
        "amount": price,
        "date": current_time(),
        "key": key
    })

    update_user(user_id, {
        "orders": orders,
        "total_orders": user_data["total_orders"] + 1
    })

    context.user_data.pop("pending_product")

    await update.message.reply_text(
        text=(
            "🎉 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐂𝐎𝐍𝐅𝐈𝐑𝐌𝐄𝐃 🎉\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            f"📦 Product : {product}\n"
            f"💰 Amount : ₹{price}\n"
            f"🔑 Key : `{key}`\n\n"

            "✅ Enjoy your premium purchase 🚀"
        ),
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================
# PROFILE
# =========================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    user_data = get_user(user_id)

    username = user_data.get("username")

    if username:
        username = f"@{username}"
    else:
        username = "Not Set"

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "👤 𝐔𝐒𝐄𝐑 𝐏𝐑𝐎𝐅𝐈𝐋𝐄 👤\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 Name : {user_data['name']}\n"
        f"🆔 Username : {username}\n"
        f"🆔 User ID : `{user_id}`\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"📦 Total Orders : {user_data['total_orders']}\n"
        f"💰 Referral Earnings : ₹{user_data['referral_earnings']:.2f}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"⏰ Joined Date : {user_data['joined']}\n"
        f"⚡ Activity Time : {user_data['last_activity']}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐄𝐍𝐔",
                callback_data="main_menu"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# =========================================
# HOW TO USE
# =========================================

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "📖 𝐇𝐎𝐖 𝐓𝐎 𝐁𝐔𝐘 📖\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "1️⃣ Click Premium Shop\n"
        "2️⃣ Select your premium plan\n"
        "3️⃣ Pay using UPI ID\n"
        "4️⃣ Click I Have Paid\n"
        "5️⃣ Send your UPI name\n"
        "6️⃣ Receive your premium key\n\n"

        "⚠️ Always pay exact amount."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ 𝐁𝐀𝐂𝐊",
                callback_data="main_menu"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=keyboard
    )

# =========================================
# SUPPORT
# =========================================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "💬 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐔𝐏𝐏𝐎𝐑𝐓 💬\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "❓ Facing any issue?\n"
        "Contact our support team.\n\n"

        "⏰ Active : 9 AM - 11 PM\n"
        "⚡ Fast Reply Available"
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✨ 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑",
                url=f"https://t.me/{OWNER_USERNAME}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐄𝐍𝐔",
                callback_data="main_menu"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=keyboard
    )

# =========================================
# REFER
# =========================================

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    user_data = get_user(user_id)

    bot_username = (await context.bot.get_me()).username

    referral_link = (
        f"https://t.me/{bot_username}?start=ref_{user_id}"
    )

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "💰 𝐑𝐄𝐅𝐄𝐑 & 𝐄𝐀𝐑𝐍 💰\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "Invite friends and earn rewards.\n\n"

        f"👥 Total Refers : {user_data['total_refers']}\n"
        f"💸 Earnings : ₹{user_data['referral_earnings']:.2f}\n\n"

        "🔗 Your Invite Link :\n"
        f"`{referral_link}`"
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📤 𝐒𝐇𝐀𝐑𝐄 𝐖𝐈𝐓𝐇 𝐅𝐑𝐈𝐄𝐍𝐃",
                url=f"https://t.me/share/url?url={referral_link}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐄𝐍𝐔",
                callback_data="main_menu"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# =========================================
# EMPTY BUTTON
# =========================================

async def none_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

# =========================================
# MAIN
# =========================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    # REMOVE COMMAND LIST BUTTON
    app.bot_data["command"] = []

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            main_menu_callback,
            pattern="^main_menu$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            shop_now,
            pattern="^shop_now$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            buy_product,
            pattern="^buy_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            paid,
            pattern="^paid_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            profile,
            pattern="^profile$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            how_to_use,
            pattern="^how_to_use$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            support,
            pattern="^support$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            refer_earn,
            pattern="^refer_earn$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            none_callback,
            pattern="^none$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("BOT STARTED SUCCESSFULLY")

    app.run_polling()

if __name__ == "__main__":
    main()
