# =========================================
# PREMIUM TELEGRAM STORE BOT
# FULL FIXED VERSION
# NO COMMAND MENU
# NO REPLY KEYBOARD
# PREMIUM UI
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
    ReplyKeyboardRemove,
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
    "1 Day Premium Key": 80,
    "1 Month Premium Key": 99,
    "1 Year Premium Key": 499,
    "Lifetime Premium Key": 999,
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
                "🛒 PREMIUM SHOP",
                callback_data="shop_now"
            )
        ],

        [
            InlineKeyboardButton(
                "📦 MY ORDERS",
                callback_data="my_orders"
            ),

            InlineKeyboardButton(
                "👤 PROFILE",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "📖 HOW TO USE",
                callback_data="how_to_use"
            ),

            InlineKeyboardButton(
                "💬 SUPPORT",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 REFER & EARN",
                callback_data="refer_earn"
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

    welcome_text = (
        "👋 *Welcome To BeSt ChEat SHOP* 👋\n\n"
        "❄️ _Here you can purchase all tg premium hacks "
        "for Android & IOS.._ 💥"
    )

    await update.message.reply_text(
        text=welcome_text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    text = (
        "🏠 *PREMIUM MAIN MENU*\n\n"
        "✨ Choose an option below:"
    )

    await update.message.reply_text(
        text=text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

# =========================================
# MAIN MENU CALLBACK
# =========================================

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "🏠 *PREMIUM MAIN MENU*\n\n"
        "✨ Choose an option below:"
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
                f"🛍️ {name} - ₹{price}",
                callback_data=f"buy_{name}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ BACK TO MENU",
            callback_data="main_menu"
        )
    ])

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🛒 *PREMIUM PRODUCTS*\n\nSelect your plan:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
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
                "✅ I HAVE PAID",
                callback_data=f"paid_{product_name}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ BACK",
                callback_data="shop_now"
            )
        ]
    ]

    text = (
        f"💸 *PAYMENT REQUIRED*\n\n"
        f"📦 Product: {product_name}\n"
        f"💰 Amount: ₹{price}\n\n"
        f"💳 UPI ID:\n`{UPI_ID}`\n\n"
        f"⚠️ Pay exact amount."
    )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# =========================================
# PAID
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
        text="✅ Send your UPI registered name:"
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
        f"🎉 *PAYMENT CONFIRMED!*\n\n"
        f"📦 Product: {product}\n"
        f"🔑 Key: `{key}`",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================
# MY ORDERS
# =========================================

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    user_data = get_user(user_id)

    orders = user_data.get("orders", [])

    try:
        await query.message.delete()
    except:
        pass

    if not orders:

        text = (
            "📭 *No orders yet!*\n\n"
            "Start shopping to see your orders here."
        )

        keyboard = InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🛒 SHOP NOW",
                    callback_data="shop_now"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ BACK TO MENU",
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

        return

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
        "👤 *USER ACCOUNT INFORMATION*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 *Name:* {user_data['name']}\n"
        f"🆔 *Username:* {username}\n"
        f"🆔 *User ID:* `{user_id}`\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"📦 *Total Orders:* {user_data['total_orders']}\n"
        f"💰 *Referral Earnings:* ₹{user_data['referral_earnings']:.2f}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"⏰ *Joined Date:* {user_data['joined']}\n"
        f"⚡ *Activity Time:* {user_data['last_activity']}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
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
        "📖 *How To Buy — SATYAM X MOD STORE*\n\n"

        "1️⃣ Tap 🛒 Shop Now\n"
        "2️⃣ Pick your product & plan\n"
        "3️⃣ Scan the UPI QR or copy UPI ID\n"
        "4️⃣ Pay the exact amount shown\n"
        "5️⃣ Tap ✅ I Have Paid\n"
        "6️⃣ Enter your UPI registered name\n"
        "7️⃣ Sit back — your key arrives in seconds! 🚀"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ BACK",
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
        "❓ *OFFICIAL SUPPORT CENTER*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "If you face any issues or have questions\n"
        "regarding our services, feel free to contact\n"
        "our expert team.\n\n"

        "⏰ Active Time: 9 AM - 11 PM\n"
        "✅ Response: Waiting 5-10 Minutes"
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✨ CONTACT OWNER",
                url=f"https://t.me/{OWNER_USERNAME}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
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
# REFER & EARN
# =========================================

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    user_data = get_user(user_id)

    bot_username = (await context.bot.get_me()).username

    referral_link = (
        f"https://t.me/{bot_username}"
        f"?start=ref_{user_id}"
    )

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "😉 *REFERRAL PROGRAM*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "Invite your friends and earn real balance\n"
        "for every successful joining.\n\n"

        f"😉 *Total Refers:* {user_data['total_refers']} User(s)\n"
        f"💰 *Invite Reward:* INR {user_data['referral_earnings']:.2f} INR\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🗣 *Your Invite Link:*\n"
        f"`{referral_link}`"
    )

    keyboard = InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🗣 SHARE WITH FRIEND",
                url=(
                    "https://t.me/share/url?"
                    f"url={referral_link}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
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
# MAIN
# =========================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

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
            my_orders,
            pattern="^my_orders$"
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
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("BOT STARTED")

    app.run_polling()

if __name__ == "__main__":
    main()
