# =========================================
# PREMIUM TELEGRAM STORE BOT
# FULL FIXED VERSION
# =========================================

import os
import json
import logging
import random
import string
import asyncio
import qrcode

from io import BytesIO
from datetime import datetime, timezone, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
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

UPI_ID = "kartikrawat6266@okhdfcbank"

OWNER_USERNAME = "SATYAM_X_OFC"

OWNER_ID = 1987818347

IST = timezone(timedelta(hours=5, minutes=30))

DB_FILE = "user_data.json"

# =========================================
# GAMES & PLANS
# =========================================

GAMES = {

    "Drip ClieNt": {
        "💸 1 Day": 75,
        "🍫 3 Day": 179,
        "🍓 7 Day": 319,
        "🧚🏻 15 Day": 549,
        "🍇 30 Day": 899
    },

    "Prime HooK": {
        "💸 1 Day": 69,
        "🍫 3 Day": 149,
        "🍓 7 Day": 269,
        "🍫 10 Day": 349
    },

    "PaTo TeaM": {
        "🍫 3 Day": 219,
        "🍓 7 Day": 499,
        "💸 30 Day": 1049
    },

    "Hg ChEaTs": {
        "💸 1 Day": 99,
        "🧚🏻 7 Day": 400,
        "🍇 30 Day": 1150
    },

    "Fʟᴜᴏʀɪᴛᴇ Ff Ios [Iphone]": {
        "💸 1 Day": 400,
        "🍓 7 Day": 1100,
        "🧚🏻 30 Day": 1800
    },

    "SpotifY EnJecT RooT": {
        "💸 7 Day": 299,
        "🧚🏻 15 Day": 579
    }
}

# =========================================
# TIME
# =========================================

def current_time():
    return datetime.now(IST).strftime("%d/%m/%Y %I:%M:%S %p")

def expiry_time():
    return (
        datetime.now(IST) + timedelta(minutes=10)
    ).strftime("%d/%m/%Y %I:%M:%S %p")

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

    user_id = str(user_id)

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
        }

        save_data(data)

    return data[user_id]

def update_user(user_id, updates=None):

    user_id = str(user_id)

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
                "🗳️ PREMIUM SHOP 🛒",
                callback_data="shop_now"
            )
        ],

        [
            InlineKeyboardButton(
                "🪩 MY ORDERS 📦",
                callback_data="my_orders"
            )
        ],

        [
            InlineKeyboardButton(
                "🎨 MY PROFILE 🙆🏻‍♂️",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "🌌 HOW TO USE 🈲",
                callback_data="how_to_use"
            )
        ],

        [
            InlineKeyboardButton(
                "📩 SUPPORT CENTER 📬",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 REFER & EARN 🔑",
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

        "🪩 *Welcome To BeSt ChEat SHOP* 🔮\n\n"

        "❄️ *Here you can purchase all tg premium*\n"
        "*hacks for Android & IOS..*💥\n\n"

        "🔻 *Continue Shopping Premium*\n"
        "*Option Below..* 🛍️"
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

    text = (
        "╔══════════════════╗\n"
        " 🅵🆁🅴🅴 🅵🅸🆁🅴 🆂🅷🅾🅿\n"
        "╚══════════════════╝\n\n"

        "🌈 *Welcome To BeSt ChEat SHOP* 🎨\n\n"

        "❄️ _Here you can purchase all tg premium_\n"
        "_hacks for Android & IOS...💥_\n\n"

        "🔻 *Continue Shopping Premium*\n"
        "*Option Below...* 🛍️"
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

    keyboard = []

    for game in GAMES.keys():

        keyboard.append([
            InlineKeyboardButton(
                f"🎮 {game}",
                callback_data=f"game_{game}"
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
            "╔══════════════════╗\n"
            " 🪩 🆂🅴🅻🅴🅲🆃 🅶🅰🅼🅴 \n"
            "╚══════════════════╝\n\n"

            "🎨 *Choose Your Favorite Premium Game*\n\n"

            "⚡ Android & IOS Supported\n"
            "🚀 Instant Delivery Available\n\n"

            "🔻 *Select Your Game Below* 🎯"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# GAME PLANS
# =========================================

async def game_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    game = query.data.replace("game_", "")

    keyboard = []

    for plan, price in GAMES[game].items():

        keyboard.append([
            InlineKeyboardButton(
                f"{plan} • ₹{price}",
                callback_data=f"plan|{game}|{plan}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ BACK",
            callback_data="shop_now"
        )
    ])

    await query.message.edit_text(
        text=(
            f"🎮 *{game}*\n\n"
            "💎 Select Your Premium Plan Below."
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# CREATE PAYMENT
# =========================================

async def create_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:

        data = query.data.split("|")

        game = data[1]
        plan = data[2]

        amount = GAMES[game][plan]

        user_id = str(query.from_user.id)

        order_id = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=10
        ))

        upi_link = (
            f"upi://pay?pa={UPI_ID}"
            f"&pn=BeStCheat"
            f"&am={amount}"
            f"&cu=INR"
        )

        qr = qrcode.make(upi_link)

        bio = BytesIO()
        bio.name = "payment_qr.png"

        qr.save(bio, "PNG")

        bio.seek(0)

        text = (
            "🛒 *Order Created Successfully!*\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            f"🎮 Product : {game}\n"
            f"📦 Plan : {plan}\n"
            f"💰 Amount To Pay : ₹{amount}\n\n"

            f"🏦 UPI ID : `{UPI_ID}`\n"
            f"🆔 Order ID : `{order_id}`\n\n"

            f"📩 Telegram ID : `{user_id}`\n\n"

            f"⌛ Payment Expiry :\n{expiry_time()}\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "📲 Scan The QR Code Above\n"
            "And Complete Your Payment Successfully.\n\n"

            "⚠️ QR Will Expire Automatically After 10 Minutes.\n\n"

            "🚫 After 10 Minutes Don't Send Payment.\n"
            "Create A New QR For Successful Payment.\n\n"

            "✅ After Payment Click Verify Payment\n\n"

            "💖 Thank You For Choosing Us"
        )

        keyboard = [

            [
                InlineKeyboardButton(
                    "✅ VERIFY PAYMENT",
                    callback_data=f"verify|{game}|{plan}|{amount}|{order_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    "❌ CANCEL",
                    callback_data="cancel_order"
                )
            ]
        ]

        await query.message.delete()

        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=InputFile(bio),
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:

        print("PAYMENT ERROR :", e)

        await query.message.reply_text(
            f"❌ QR GENERATE ERROR\n\n{e}"
        )

# =========================================
# VERIFY PAYMENT
# =========================================

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data.split("|")

    game = data[1]
    plan = data[2]
    amount = data[3]
    order_id = data[4]

    checking = await query.message.reply_text(
        "🔍 Checking Your Payment Please Wait..."
    )

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            "🚨 *NEW PAYMENT REQUEST*\n\n"

            f"🎮 Product : {game}\n"
            f"📦 Plan : {plan}\n"
            f"💰 Amount : ₹{amount}\n"
            f"🆔 Order ID : `{order_id}`\n\n"

            f"👤 User ID : `{query.from_user.id}`"
        ),
        parse_mode="Markdown"
    )

    await asyncio.sleep(5)

    try:
        await checking.delete()
    except:
        pass

# =========================================
# CANCEL ORDER
# =========================================

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    text = (
        "╔══════════════════╗\n"
        " 🆆🅴🅻🅲🅾🅼🅴 🅱🆄🅳🅳🆈\n"
        "╚══════════════════╝\n\n"

        "🪩 *Welcome To BeSt ChEat SHOP* 🔮\n\n"

        "❄️ *Here you can purchase all tg premium*\n"
        "*hacks for Android & IOS..*💥\n\n"

        "🔻 *Continue Shopping Premium*\n"
        "*Option Below..* 🛍️"
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# =========================================
# MY ORDERS
# =========================================

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        text="📭 *NO ORDERS FOUND*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ BACK TO MENU",
                    callback_data="main_menu"
                )
            ]
        ])
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

    text = (
        "╔══════════════════╗\n"
        "  🆈🅾🆄🆁 🅿🆁🅾🅵🅸🅻🅴 \n"
        "╚══════════════════╝\n\n"

       f"🍇 ***Name :*** _{user_data['name']}_\n"
       f"💌 ***Username :*** _{username}_\n"
       f"🫅🏻 ***User ID :*** _`{user_id}`_\n\n"

       f"❄️ ***Total Orders :*** _{user_data['total_orders']}_"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ BACK TO MENU",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================
# HOW TO USE
# =========================================

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        text=(
            "📖 *HOW TO BUY PREMIUM*\n\n"

            "1️⃣ Click Premium Shop\n"
            "2️⃣ Select Your Product\n"
            "3️⃣ Select Plan\n"
            "4️⃣ Scan QR & Pay\n"
            "5️⃣ Click Verify Payment\n"
            "6️⃣ Receive Key 🚀"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ BACK TO MENU",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================
# SUPPORT
# =========================================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

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
        text=(
            "💬 *PREMIUM SUPPORT CENTER*\n\n"

            "⚡ Fast Support Available\n"
            "⏰ Active : 9AM To 11PM\n\n"

            "Click Below Button To Contact Owner."
        ),
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

    bot_username = (await context.bot.get_me()).username

    referral_link = (
        f"https://t.me/{bot_username}?start=ref_{user_id}"
    )

    text = (
        "😉 *REFERRAL PROGRAM*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🗣 Your Invite Link :\n`{referral_link}`"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ BACK TO MENU",
                    callback_data="main_menu"
                )
            ]
        ])
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
            game_plans,
            pattern="^game_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            create_payment,
            pattern=r"^plan\|"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            verify_payment,
            pattern=r"^verify\|"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            cancel_order,
            pattern="^cancel_order$"
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

    print("BOT STARTED SUCCESSFULLY")

    app.run_polling()

if __name__ == "__main__":
    main()
