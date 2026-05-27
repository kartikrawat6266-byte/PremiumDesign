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
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ==================== CONFIGURATION ====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found")

UPI_ID = os.environ.get("UPI_ID", "example@okhdfcbank")

IST = timezone(timedelta(hours=5, minutes=30))

DB_FILE = "user_data.json"

# ==================== PRODUCTS ====================

PRODUCTS = {
    "1 Day Premium Key": 80.00,
    "1 Month Premium Key": 99.00,
    "1 Year Premium Key": 499.00,
    "Lifetime Premium Key": 999.00,
}

# ==================== TIME ====================

def get_current_ist():
    return datetime.now(IST).strftime("%d/%m/%Y, %I:%M:%S %p")


def get_joined_date():
    return datetime.now(IST).strftime("%d/%m/%Y")

# ==================== DATABASE ====================

def load_user_data():

    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return {}


def save_user_data(data):

    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except:
        pass


def get_user(user_id):

    data = load_user_data()

    if user_id not in data:

        data[user_id] = {

            "name": "",
            "username": "",
            "total_orders": 0,
            "referral_earnings": 0.0,
            "total_refers": 0,
            "orders": [],
            "joined": get_joined_date()
        }

        save_user_data(data)

    return data[user_id]


def update_user(user_id, update_data):

    data = load_user_data()

    if user_id not in data:
        data[user_id] = get_user(user_id)

    data[user_id].update(update_data)

    save_user_data(data)

# ==================== BOTTOM BUTTON MENU ====================

def bottom_menu_keyboard():

    keyboard = [

        ["🛒 Shop Now"],

        ["📦 My Orders", "👤 Profile"],

        ["📖 How to Use", "💬 Support"],

        ["💰 Refer & Earn"]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

# ==================== INLINE BUTTONS ====================

def product_list_keyboard():

    keyboard = []

    for name, price in PRODUCTS.items():

        keyboard.append([
            InlineKeyboardButton(
                f"🛍️ {name} - ₹{price:.2f}",
                callback_data=f"product_{name}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Back To Menu",
            callback_data="main_menu"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def payment_keyboard(product_name, amount):

    upi_link = (
        f"upi://pay?"
        f"pa={UPI_ID}"
        f"&pn=Satyam%20X%20Store"
        f"&am={amount}"
        f"&cu=INR"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "✅ I Have Paid",
                callback_data=f"paid_{product_name}"
            )
        ],

        [
            InlineKeyboardButton(
                "💳 Copy UPI ID",
                callback_data="copy_upi"
            ),

            InlineKeyboardButton(
                "📱 Open UPI App",
                url=upi_link
            )
        ],

        [
            InlineKeyboardButton(
                "🔙 Cancel",
                callback_data="main_menu"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def admin_contact_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "📞 Contact Admin",
                url="https://t.me/SATYAM_X_OFC"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# ==================== START ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    user_id = str(user.id)

    user_data = get_user(user_id)

    if not user_data["name"]:

        update_user(
            user_id,
            {
                "name": user.full_name or "User",
                "username": user.username or ""
            }
        )

    welcome_text = (
        f"👋 Welcome to *Satyam X Ofc Store*!\n\n"
        f"Trusted selling bot – anyone can purchase from this bot.\n"
        f"⭐ *SUPER FAST DELIVERY*\n\n"
        f"📌 Use the buttons below to start shopping."
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=bottom_menu_keyboard()
    )

# ==================== TEXT BUTTONS ====================

async def text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # SHOP NOW
    if text == "🛒 Shop Now":

        await update.message.reply_text(
            "🛍️ *Our Products*\n\nSelect product below:",
            parse_mode="Markdown",
            reply_markup=product_list_keyboard()
        )

    # MY ORDERS
    elif text == "📦 My Orders":

        user_id = str(update.effective_user.id)

        user_data = get_user(user_id)

        orders = user_data.get("orders", [])

        if not orders:

            await update.message.reply_text(
                "📭 *No orders yet!*",
                parse_mode="Markdown"
            )

            return

        msg = "*📦 Your Orders*\n\n"

        for i, o in enumerate(reversed(orders[-10:]), 1):

            msg += (
                f"{i}. *{o['product']}*\n"
                f"🔑 `{o['key']}`\n\n"
            )

        await update.message.reply_text(
            msg,
            parse_mode="Markdown"
        )

    # PROFILE
    elif text == "👤 Profile":

        user_id = str(update.effective_user.id)

        u = get_user(user_id)

        username = u.get("username", "")

        if username:
            username_display = f"@{username}"
        else:
            username_display = "Not set"

        profile_msg = (
            f"👤 *User Account Information*\n\n"
            f"• Name: {u.get('name')}\n"
            f"• Username: {username_display}\n"
            f"• User ID: `{user_id}`\n\n"
            f"• Orders: {u.get('total_orders', 0)}\n"
            f"• Earnings: ₹{u.get('referral_earnings', 0):.2f}"
        )

        await update.message.reply_text(
            profile_msg,
            parse_mode="Markdown"
        )

    # HOW TO USE
    elif text == "📖 How to Use":

        help_msg = (
            "*📖 How To Buy*\n\n"
            "1️⃣ Tap Shop Now\n"
            "2️⃣ Select Product\n"
            "3️⃣ Pay Exact Amount\n"
            "4️⃣ Click I Have Paid\n"
            "5️⃣ Enter UPI Name\n"
            "6️⃣ Receive Key Instantly"
        )

        await update.message.reply_text(
            help_msg,
            parse_mode="Markdown"
        )

    # SUPPORT
    elif text == "💬 Support":

        support_msg = (
            "*🆘 OFFICIAL SUPPORT CENTER*\n\n"
            "📅 Active Time: 9 AM - 11 PM\n"
            "⏱️ Response: 5-10 Minutes"
        )

        await update.message.reply_text(
            support_msg,
            parse_mode="Markdown",
            reply_markup=admin_contact_keyboard()
        )

    # REFER
    elif text == "💰 Refer & Earn":

        user_id = str(update.effective_user.id)

        bot_username = (
            await context.bot.get_me()
        ).username

        referral_link = (
            f"https://t.me/{bot_username}?start={user_id}"
        )

        await update.message.reply_text(
            f"💰 *Referral Link*\n\n`{referral_link}`",
            parse_mode="Markdown"
        )

# ==================== PRODUCT SELECT ====================

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    product_name = query.data.replace("product_", "")

    price = PRODUCTS.get(product_name)

    if not price:

        await query.edit_message_text(
            "❌ Product not found."
        )

        return

    context.user_data["pending_product"] = product_name

    payment_text = (
        f"💸 *Payment Required*\n\n"
        f"📦 Product: {product_name}\n"
        f"💰 Amount: ₹{price:.2f}\n\n"
        f"💳 UPI ID:\n"
        f"`{UPI_ID}`"
    )

    await query.edit_message_text(
        payment_text,
        parse_mode="Markdown",
        reply_markup=payment_keyboard(
            product_name,
            price
        )
    )

# ==================== PAYMENT ====================

async def paid_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        "✅ Send your UPI registered name:"
    )


async def handle_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    product_name = context.user_data.get("pending_product")

    if not product_name:
        return

    user_name = update.message.text.strip()

    user_id = str(update.effective_user.id)

    price = PRODUCTS.get(product_name, 0)

    license_key = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=16
        )
    )

    user_data = get_user(user_id)

    orders = user_data.get("orders", [])

    orders.append({

        "product": product_name,
        "amount": price,
        "date": get_current_ist(),
        "key": license_key,
        "upi_name": user_name
    })

    update_user(
        user_id,
        {
            "orders": orders,
            "total_orders": user_data.get("total_orders", 0) + 1
        }
    )

    context.user_data["pending_product"] = None

    await update.message.reply_text(
        f"🎉 *Payment Confirmed!*\n\n"
        f"📦 {product_name}\n"
        f"🔑 `{license_key}`",
        parse_mode="Markdown",
        reply_markup=bottom_menu_keyboard()
    )

# ==================== CALLBACKS ====================

async def copy_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer(
        text=f"UPI ID:\n{UPI_ID}",
        show_alert=True
    )


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        "🏠 Back To Main Menu"
    )

# ==================== BOT COMMANDS ====================

async def set_bot_commands(application: Application):

    commands = [

        BotCommand("start", "Start Bot")

    ]

    await application.bot.set_my_commands(
        commands,
        scope=BotCommandScopeDefault()
    )

# ==================== MAIN ====================

def main():

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # COMMAND
    application.add_handler(
        CommandHandler("start", start)
    )

    # TEXT BUTTONS
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_buttons
        )
    )

    # CALLBACKS
    application.add_handler(
        CallbackQueryHandler(
            product_selected,
            pattern="^product_"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            paid_confirmation,
            pattern="^paid_"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            copy_upi,
            pattern="^copy_upi$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            main_menu_callback,
            pattern="^main_menu$"
        )
    )

    # UPI NAME
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_upi_name
        )
    )

    import asyncio

    asyncio.get_event_loop().run_until_complete(
        set_bot_commands(application)
    )

    logger.info("Bot Started Successfully")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )

# ==================== RUN ====================

if __name__ == "__main__":
    main()
