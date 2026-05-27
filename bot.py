import os
import json
import logging
import random
import string
from datetime import datetime, timezone, timedelta

from telegram import (
    Update,
    BotCommand,
    BotCommandScopeDefault,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found!")

UPI_ID = os.environ.get("UPI_ID", "example@upi")

OWNER_USERNAME = "SATYAM_X_OFC"

DB_FILE = "user_data.json"

IST = timezone(timedelta(hours=5, minutes=30))

# =========================================================
# PRODUCTS
# =========================================================

PRODUCTS = {
    "1 Day Premium Key": 80.00,
    "1 Month Premium Key": 99.00,
    "1 Year Premium Key": 499.00,
    "Lifetime Premium Key": 999.00,
}

FREE_KEY_REFERRALS_NEEDED = 80
FREE_KEY_PRODUCT = "1 Day Premium Key"

# =========================================================
# TIME FUNCTIONS
# =========================================================

def current_time():
    return datetime.now(IST).strftime("%d/%m/%Y %I:%M:%S %p")

# =========================================================
# DATABASE
# =========================================================

def load_user_data():
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_user(user_id):
    data = load_user_data()

    if user_id not in data:
        data[user_id] = {
            "name": "",
            "username": "",
            "joined_date": current_time(),
            "activity_time": current_time(),
            "total_orders": 0,
            "orders": [],
            "referral_earnings": 0.0,
            "total_refers": 0,
            "referred_users": [],
            "referral_history": [],
            "referred_by": None,
            "free_key_claimed": False,
            "pending_payment": None
        }

        save_user_data(data)

    return data[user_id]

def update_user(user_id, new_data):
    data = load_user_data()

    if user_id not in data:
        data[user_id] = get_user(user_id)

    data[user_id].update(new_data)
    data[user_id]["activity_time"] = current_time()

    save_user_data(data)

def update_activity(user_id):
    data = load_user_data()

    if user_id in data:
        data[user_id]["activity_time"] = current_time()
        save_user_data(data)

# =========================================================
# REFERRAL SYSTEM
# =========================================================

def add_referral(referrer_id, new_user_id, username):
    referrer = get_user(referrer_id)

    if new_user_id in referrer["referred_users"]:
        return False

    referrer["referred_users"].append(new_user_id)
    referrer["total_refers"] += 1
    referrer["referral_earnings"] += 1

    referrer["referral_history"].append({
        "user": username,
        "date": current_time()
    })

    update_user(referrer_id, referrer)

    return True

# =========================================================
# PERSISTENT MENU
# =========================================================

def persistent_menu():
    keyboard = [
        ["☰ Menu"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

# =========================================================
# MAIN MENU BUTTONS
# =========================================================

def main_menu_keyboard():
    keyboard = [

        [
            InlineKeyboardButton(
                "🛒 Shop Now",
                callback_data="shop_now"
            )
        ],

        [
            InlineKeyboardButton(
                "📦 My Orders",
                callback_data="my_orders"
            ),

            InlineKeyboardButton(
                "👤 Profile",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "📖 How To Use",
                callback_data="how_to_use"
            ),

            InlineKeyboardButton(
                "💬 Support",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 Refer & Earn",
                callback_data="refer_earn"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# =========================================================
# BACK BUTTON
# =========================================================

def back_button():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔙 Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])

# =========================================================
# SHOP BUTTON
# =========================================================

def shop_now_button():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🛒 Shop Now",
                callback_data="shop_now"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])

# =========================================================
# PRODUCTS
# =========================================================

def products_keyboard():
    keyboard = []

    for product, price in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"🛍️ {product} - ₹{price}",
                callback_data=f"product_{product}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Back to Menu",
            callback_data="main_menu"
        )
    ])

    return InlineKeyboardMarkup(keyboard)

# =========================================================
# PAYMENT BUTTONS
# =========================================================

def payment_keyboard(product, amount):

    upi_link = (
        f"upi://pay?pa={UPI_ID}&pn=SatyamXStore&am={amount}&cu=INR"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "✅ I Have Paid",
                callback_data=f"paid_{product}"
            )
        ],

        [
            InlineKeyboardButton(
                "📱 Open UPI App",
                url=upi_link
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Cancel",
                callback_data="shop_now"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# =========================================================
# SUPPORT BUTTON
# =========================================================

def support_keyboard():
    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✨ Contact Owner",
                url=f"https://t.me/{OWNER_USERNAME}"
            )
        ],

        [
            InlineKeyboardButton(
                "🕒 Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])

# =========================================================
# REFER BUTTON
# =========================================================

def refer_keyboard(referral_link):
    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🗣️ Share with Friend",
                url=(
                    f"https://t.me/share/url?"
                    f"url={referral_link}"
                    f"&text=🔥 Join This Premium Store Bot!"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "🔢 Back to Menu",
                callback_data="main_menu"
            )
        ]
    ])

# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = str(user.id)

    # REFERRAL
    if context.args and context.args[0].startswith("ref_"):

        referrer_id = context.args[0].replace("ref_", "")

        if referrer_id != user_id:

            user_data = get_user(user_id)

            if not user_data["referred_by"]:

                username = (
                    f"@{user.username}"
                    if user.username
                    else user.full_name
                )

                added = add_referral(
                    referrer_id,
                    user_id,
                    username
                )

                if added:

                    update_user(user_id, {
                        "referred_by": referrer_id
                    })

    # CREATE USER
    user_data = get_user(user_id)

    if not user_data["name"]:

        update_user(user_id, {
            "name": user.full_name,
            "username": user.username or ""
        })

    update_activity(user_id)

    text = (
        "🏠 *Main Menu*\n\n"
        "Choose an option:"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    await update.message.reply_text(
        "Menu Opened ✅",
        reply_markup=persistent_menu()
    )

# =========================================================
# MAIN MENU
# =========================================================

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    try:
        await query.message.delete()
    except:
        pass

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="🏠 *Main Menu*\n\nChoose an option:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================================
# SHOP NOW
# =========================================================

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="🛍️ *Our Products*\n\nSelect product:",
        parse_mode="Markdown",
        reply_markup=products_keyboard()
    )

# =========================================================
# PRODUCT SELECT
# =========================================================

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    product_name = query.data.replace("product_", "")

    amount = PRODUCTS.get(product_name)

    update_user(user_id, {
        "pending_payment": product_name
    })

    text = (
        "💸 *Payment Required*\n\n"
        f"📦 Product: {product_name}\n"
        f"💰 Amount: ₹{amount}\n\n"
        f"💳 UPI ID:\n`{UPI_ID}`\n\n"
        "⚠️ Pay exact amount!"
    )

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=payment_keyboard(product_name, amount)
    )

# =========================================================
# PAID
# =========================================================

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    product_name = query.data.replace("paid_", "")

    context.user_data["pending_product"] = product_name

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="✅ Enter your UPI registered name:"
    )

# =========================================================
# HANDLE UPI NAME
# =========================================================

async def handle_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "pending_product" not in context.user_data:
        return

    user_id = str(update.effective_user.id)

    update_activity(user_id)

    upi_name = update.message.text

    product = context.user_data["pending_product"]

    amount = PRODUCTS.get(product)

    license_key = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=16
        )
    )

    user_data = get_user(user_id)

    user_data["orders"].append({
        "product": product,
        "amount": amount,
        "key": license_key,
        "upi_name": upi_name,
        "date": current_time()
    })

    user_data["total_orders"] += 1

    update_user(user_id, user_data)

    context.user_data.pop("pending_product")

    text = (
        "🎉 *Payment Confirmed!*\n\n"
        f"📦 {product}\n"
        f"🔑 `{license_key}`\n\n"
        "🚀 SUPER FAST DELIVERY"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================================
# MY ORDERS
# =========================================================

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    user_data = get_user(user_id)

    orders = user_data["orders"]

    await query.message.delete()

    if not orders:

        text = (
            "*No orders yet!*\n\n"
            "Start shopping to see your orders here."
        )

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=shop_now_button()
        )

        return

    text = "📦 *Your Orders*\n\n"

    for order in reversed(orders):

        text += (
            f"📦 {order['product']}\n"
            f"💰 ₹{order['amount']}\n"
            f"🔑 `{order['key']}`\n"
            f"📅 {order['date']}\n\n"
        )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=back_button()
    )

# =========================================================
# PROFILE
# =========================================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    u = get_user(user_id)

    username = (
        f"@{u['username']}"
        if u["username"]
        else "Not Set"
    )

    text = (
        "👤 *User Account Information*\n\n"

        f"👤 Name: {u['name']}\n"
        f"🆔 Username: {username}\n"
        f"🆔 User ID: `{user_id}`\n\n"

        f"📦 Total Orders: {u['total_orders']}\n"
        f"💰 Referral Earnings: ₹{u['referral_earnings']:.2f}\n\n"

        f"⏰ Joined Date:\n{u['joined_date']}\n\n"

        f"⚡ Activity Time:\n{u['activity_time']}"
    )

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=back_button()
    )

# =========================================================
# HOW TO USE
# =========================================================

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    text = (
        "📖 *How to Buy — SATYAM X MOD STORE*\n\n"

        "1️⃣ Tap 🛒 Shop Now\n"
        "2️⃣ Pick your product & plan\n"
        "3️⃣ Scan the UPI QR or copy UPI ID\n"
        "4️⃣ Pay exact amount shown\n"
        "5️⃣ Tap ✅ I Have Paid\n"
        "6️⃣ Enter UPI registered name\n"
        "7️⃣ Your key arrives instantly 🚀\n\n"

        "⚠️ Always pay exact amount!"
    )

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================================
# SUPPORT
# =========================================================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    text = (
        "❓ *OFFICIAL SUPPORT CENTER*\n\n"

        "If you face any issues or have questions\n"
        "regarding our services, feel free to contact\n"
        "our expert team.\n\n"

        "⏰ Active Time: 9 AM - 11 PM\n"
        "✅ Response: Waiting 5-10 Minutes\n\n"

        "Click the button below to start a chat:"
    )

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=support_keyboard()
    )

# =========================================================
# REFER & EARN
# =========================================================

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = str(query.from_user.id)

    update_activity(user_id)

    bot_username = (await context.bot.get_me()).username

    referral_link = (
        f"https://t.me/{bot_username}"
        f"?start=ref_{user_id}"
    )

    user_data = get_user(user_id)

    text = (
        "😉 *Referral Program*\n\n"

        "Invite your friends and earn real balance\n"
        "for every successful joining.\n\n"

        f"😉 Total Refers: {user_data['total_refers']} User(s)\n"
        f"💰 Invite Reward: INR {user_data['referral_earnings']:.2f}\n\n"

        f"🗣️ Your Invite Link:\n"
        f"`{referral_link}`\n\n"

        "Share your link to grow your earnings!"
    )

    await query.message.delete()

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=refer_keyboard(referral_link)
    )

# =========================================================
# UNKNOWN
# =========================================================

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message:

        await update.message.reply_text(
            "❌ Please use menu buttons.",
            reply_markup=persistent_menu()
        )

# =========================================================
# BOT COMMANDS
# =========================================================

async def set_commands(app):

    commands = [

        BotCommand("start", "Start Bot"),

        BotCommand("shop", "Open Shop"),

        BotCommand("profile", "Your Profile"),

        BotCommand("orders", "My Orders"),

        BotCommand("support", "Support"),

        BotCommand("refer", "Refer & Earn"),
    ]

    await app.bot.set_my_commands(
        commands,
        scope=BotCommandScopeDefault()
    )

# =========================================================
# MAIN
# =========================================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    # COMMANDS
    app.add_handler(CommandHandler("start", start))

    # CALLBACKS
    app.add_handler(
        CallbackQueryHandler(main_menu, pattern="^main_menu$")
    )

    app.add_handler(
        CallbackQueryHandler(shop_now, pattern="^shop_now$")
    )

    app.add_handler(
        CallbackQueryHandler(product_selected, pattern="^product_")
    )

    app.add_handler(
        CallbackQueryHandler(paid, pattern="^paid_")
    )

    app.add_handler(
        CallbackQueryHandler(my_orders, pattern="^my_orders$")
    )

    app.add_handler(
        CallbackQueryHandler(profile, pattern="^profile$")
    )

    app.add_handler(
        CallbackQueryHandler(how_to_use, pattern="^how_to_use$")
    )

    app.add_handler(
        CallbackQueryHandler(support, pattern="^support$")
    )

    app.add_handler(
        CallbackQueryHandler(refer_earn, pattern="^refer_earn$")
    )

    # MESSAGE
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_upi
        )
    )

    app.add_handler(
        MessageHandler(filters.ALL, unknown)
    )

    # COMMAND SETUP
    import asyncio

    asyncio.get_event_loop().run_until_complete(
        set_commands(app)
    )

    logger.info("Bot Started!")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )

# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":
    main()
