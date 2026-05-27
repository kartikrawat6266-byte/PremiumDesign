# =========================================
# PREMIUM TELEGRAM STORE BOT
# FULL FIXED VERSION
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
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
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

def update_user(user_id, updates=None):

    data = load_data()

    if user_id not in data:
        get_user(user_id)

    data = load_data()

    if updates:
        data[user_id].update(updates)

    data[user_id]["last_activity"] = current_time()

    save_data(data)

# =========================================
# KEYBOARD
# =========================================

def main_menu_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "🛒 PREMIUM SHOP 🛒",
                callback_data="shop_now"
            )
        ],

        [
            InlineKeyboardButton(
                "📦 MY ORDERS 📦",
                callback_data="my_orders"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 MY PROFILE 👤",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "📖 HOW TO USE 📖",
                callback_data="how_to_use"
            )
        ],

        [
            InlineKeyboardButton(
                "💬 SUPPORT CENTER 💬",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 REFER & EARN 💰",
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

    text = (
        "╔══════════════════╗\n"
        " 🆆🅴🅻🅲🅾🅼🅴 🅱🆄🅳🅳🆈\n"
        "╚══════════════════╝\n\n"

        "👋 *Welcome To BeSt ChEat SHOP* 👋\n\n"

        "❄️ *Here you can purchase all tg premium*\n"
        "*hacks for Android & IOS..* 💥\n\n"

        "🔻 ***Continue Shopping Premium***\n"
        "***Option Below..*** 🛍️"
    )
 
    await update.message.reply_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================
# MAIN MENU
# =========================================

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    text = (
        "╔══════════════════╗\n"
        " 🅵🆁🅴🅴 🅵🅸🆁🅴 🆂🅷🅾🅿\n"
        "╚══════════════════╝\n\n"

        "👋 *Welcome To BeSt ChEat SHOP* 👋\n\n"

        "❄️ _Here you can purchase all tg premium_\n"
        "_hacks for Android & IOS.._ 💥\n\n"

        "🔻 *Continue Shopping Premium*\n"
        "*Option Below..* 🛍️"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================
# SHOP
# =========================================

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    keyboard = []

    for name, price in PRODUCTS.items():

        keyboard.append([
            InlineKeyboardButton(
                f"🛍️ {name} • ₹{price}",
                callback_data=f"buy_{name}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ BACK TO MENU",
            callback_data="main_menu"
        )
    ])

    await query.message.edit_text(
        text=(
            "🛒 *PREMIUM PRODUCT STORE*\n\n"
            "✨ Select Your Premium Plan Below ✨"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# BUY PRODUCT
# =========================================

async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    product_name = query.data.replace("buy_", "")

    price = PRODUCTS.get(product_name)

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
        "💸 *PAYMENT REQUIRED*\n\n"

        f"📦 Product : {product_name}\n"
        f"💰 Amount : ₹{price}\n\n"

        f"💳 UPI ID :\n`{UPI_ID}`\n\n"

        "⚠️ Pay Exact Amount Then Click\n"
        "✅ I HAVE PAID"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# PAID
# =========================================

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    product = query.data.replace("paid_", "")

    context.user_data["pending_product"] = product

    await query.message.edit_text(
        text=(
            "✅ *PAYMENT DETECTED*\n\n"
            "Send Your UPI Registered Name Now."
        ),
        parse_mode="Markdown"
    )

# =========================================
# HANDLE MESSAGE
# =========================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "pending_product" not in context.user_data:
        return

    user_id = str(update.effective_user.id)

    update_user(user_id)

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
            "🎉 *PAYMENT CONFIRMED*\n\n"

            f"📦 Product : {product}\n"
            f"💰 Amount : ₹{price}\n"
            f"🔑 Key : `{key}`\n\n"

            "✅ Thanks For Purchasing."
        ),
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

    update_user(user_id)

    user_data = get_user(user_id)

    orders = user_data.get("orders", [])

    if not orders:

        keyboard = [
            [
                InlineKeyboardButton(
                    "🛒 OPEN SHOP",
                    callback_data="shop_now"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ BACK TO MENU",
                    callback_data="main_menu"
                )
            ]
        ]

        await query.message.edit_text(
            text=(
                "📭 *NO ORDERS FOUND*\n\n"
                "Purchase Any Premium Product First."
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    text = "📦 *YOUR PREMIUM ORDERS*\n\n"

    for order in orders:

        text += (
            f"📦 {order['product']}\n"
            f"💰 ₹{order['amount']}\n"
            f"📅 {order['date']}\n"
            f"🔑 `{order['key']}`\n\n"
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
                callback_data="main_menu"
            )
        ]
    ]

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# PROFILE
# =========================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    user_data = get_user(user_id)

    username = user_data.get("username")

    if username:
        username = f"@{username}"
    else:
        username = "Not Set"

    text = (
        "╔══════════════════╗\n"
        "🅿🆁🅴🅼🅸🆄🅼 🅿🆁🅾🅵🅸🅻🅴\n"
        "╚══════════════════╝\n\n"

       f"👤 ***Name :*** _{user_data['name']}_\n"
       f"🆔 ***Username :*** _{username}_\n"
       f"💎 ***User ID :*** _`{user_id}`_\n\n"

        "╔══════════════════╗\n"
        " 📦 🆄🆂🅴🆁 🆂🆃🅰🆃🆂 📦\n"
        "╚══════════════════╝\n\n"

       f"📦 ***Total Orders :*** _{user_data['total_orders']}_\n"
       f"💰 ***Referral Earnings :*** _₹{user_data['referral_earnings']:.2f}_\n"
       f"👥 ***Total Refers :*** _{user_data['total_refers']}_\n\n"

        "╔══════════════════╗\n"
        "⏰ 🅰🅲🅲🅾🆄🅽🆃 🆃🅸🅼🅴 ⏰\n"
        "╚══════════════════╝\n\n"

       f"📅 ***Joined :*** _{user_data['joined']}_\n"
       f"⚡ ***Last Activity :*** _{user_data['last_activity']}_"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
                callback_data="main_menu"
            )
        ]
    ]

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# HOW TO USE
# =========================================

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    text = (
        "📖 *HOW TO BUY PREMIUM*\n\n"

        "1️⃣ Click Premium Shop\n"
        "2️⃣ Select Your Product\n"
        "3️⃣ Pay Using UPI\n"
        "4️⃣ Click I HAVE PAID\n"
        "5️⃣ Send UPI Registered Name\n"
        "6️⃣ Receive Premium Key Instantly 🚀"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
                callback_data="main_menu"
            )
        ]
    ]

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# SUPPORT
# =========================================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    text = (
        "💬 *PREMIUM SUPPORT CENTER*\n\n"

        "⚡ Fast Support Available\n"
        "⏰ Active : 9AM To 11PM\n\n"

        "Click Below Button To Contact Owner."
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "✨ CONTACT OWNER ✨",
                url=f"https://t.me/{OWNER_USERNAME}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ BACK TO MENU",
                callback_data="main_menu"
            )
        ]
    ]

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# REFER & EARN
# =========================================

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    update_user(user_id)

    user_data = get_user(user_id)

    bot_username = (await context.bot.get_me()).username

    referral_link = (
        f"https://t.me/{bot_username}?start=ref_{user_id}"
    )

    text = (
        "😉 *REFERRAL PROGRAM*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "Invite Your Friends And Earn\n"
        "Real Balance For Every Joining.\n\n"

        f"😉 Total Refers : {user_data['total_refers']} User(s)\n"
        f"💰 Invite Reward : ₹{user_data['referral_earnings']:.2f}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🗣 Your Invite Link :\n`{referral_link}`\n\n"

        "Share Your Link To Grow Earnings."
    )

    keyboard = [

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
    ]

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    print("BOT STARTED SUCCESSFULLY")

    app.run_polling()

if __name__ == "__main__":
    main()
