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

        # SAVE ORDER DATA
        if "orders" not in context.bot_data:
            context.bot_data["orders"] = {}

        context.bot_data["orders"][order_id] = {
            "game": game,
            "plan": plan,
            "amount": amount,
            "user_id": user_id
        }

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
                    "🧚🏻 Verify Payment",
                    callback_data=f"verify|{order_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    "🪩 Cancel OrDeR",
                    callback_data="cancel_order"
                )
            ]
        ]

        try:
            await query.message.delete()
        except:
            pass

        await context.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=InputFile(bio),
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:

        print("PAYMENT ERROR :", e)

# =========================================
# VERIFY PAYMENT
# =========================================

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    try:

        data = query.data.split("|")

        order_id = data[1]

        if "orders" not in context.bot_data:
            return

        if order_id not in context.bot_data["orders"]:
            return

        order_data = context.bot_data["orders"][order_id]

        game = order_data["game"]
        plan = order_data["plan"]
        amount = order_data["amount"]

        user_id = query.from_user.id

        username = query.from_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "No Username"

        # SAVE QR MESSAGE ID
        if "qr_messages" not in context.bot_data:
            context.bot_data["qr_messages"] = {}

        context.bot_data["qr_messages"][str(user_id)] = query.message.message_id

        # SAVE VERIFY DATA
        if "verify_orders" not in context.bot_data:
            context.bot_data["verify_orders"] = {}

        context.bot_data["verify_orders"][str(user_id)] = {
            "game": game,
            "plan": plan,
            "amount": amount,
            "order_id": order_id
        }

        # USER CHECKING MESSAGE
        checking_msg = await context.bot.send_message(
            chat_id=user_id,
            text="🔍 Checking Your Payment Please Wait..."
        )

        # AUTO DELETE AFTER 15 SEC
        asyncio.create_task(
            auto_delete_message(
                context.bot,
                user_id,
                checking_msg.message_id
            )
        )

        verify_time = current_time()

        # OWNER REQUEST
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                f"🧚🏻 New Payment Request 🪩\n\n"

                f"🎮 Game : {game}\n"
                f"📦 Plan : {plan}\n"
                f"💵 Price : ₹{amount}\n"
                f"🆔 Order ID : {order_id}\n\n"

                f"👤 User ID : {user_id}\n"
                f"🌐 Username : {username_text}\n\n"

                f"🕒 Verify Time : {verify_time}"
            ),
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "🧚🏻 APPROVE PAYMENT",
                        callback_data=f"approve|{user_id}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "🪩 CANCEL PAYMENT",
                        callback_data=f"cancelpayment|{user_id}"
                    )
                ]
            ])
        )

    except Exception as e:
        print(f"VERIFY ERROR : {e}")

# =========================================
# AUTO DELETE MESSAGE
# =========================================

async def auto_delete_message(bot, chat_id, message_id):

    await asyncio.sleep(15)

    try:

        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )

    except:
        pass

# =========================================
# CANCEL ORDER
# =========================================

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    # DELETE QR MESSAGE
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

    # SEND MAIN MENU
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    
# =========================================
# CANCEL PAYMENT
# =========================================

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = int(query.data.split("|")[1])

    # REMOVE OWNER BUTTONS FAST
    try:

        await query.edit_message_reply_markup(
            reply_markup=None
        )

    except:
        pass

    # OWNER SUCCESS MESSAGE
    try:

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🍫 User Payment Cancelled Successfully"
        )

    except:
        pass

    # DELETE USER QR
    try:

        if "qr_messages" in context.bot_data:

            qr_message_id = context.bot_data["qr_messages"].get(str(user_id))

            if qr_message_id:

                await context.bot.delete_message(
                    chat_id=user_id,
                    message_id=qr_message_id
                )

    except:
        pass

    # USER MESSAGE
    sent_msg = await context.bot.send_message(
        chat_id=user_id,
        text=(
            "⚠️ Payment not received yet.\n"
            "Please try again in a few seconds."
        ),
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🧚🏻 Go To BaCk MeNu 🪩",
                    callback_data="main_menu"
                )
            ]
        ])
    )

    # AUTO DELETE
    asyncio.create_task(
        auto_delete_cancel_msg(
            context.bot,
            user_id,
            sent_msg.message_id
        )
    )
    
# =========================================
# APPROVE PAYMENT
# =========================================

async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    # FAST RESPONSE
    await query.answer()

    try:

        data = query.data.split("|")

        user_id = int(data[1])

        # VERIFY ORDER CHECK
        if "verify_orders" not in context.bot_data:
            return

        if str(user_id) not in context.bot_data["verify_orders"]:
            return

        order_data = context.bot_data["verify_orders"][str(user_id)]

        game = order_data["game"]
        plan = order_data["plan"]
        amount = order_data["amount"]
        order_id = order_data["order_id"]

        # PAYMENT TIME
        payment_time = datetime.now(IST)

        # EXPIRY TIME
        if "1 Day" in plan:
            expiry_datetime = payment_time + timedelta(days=1, hours=2)

        elif "3 Day" in plan:
            expiry_datetime = payment_time + timedelta(days=3, hours=2)

        elif "7 Day" in plan:
            expiry_datetime = payment_time + timedelta(days=7, hours=2)

        elif "10 Day" in plan:
            expiry_datetime = payment_time + timedelta(days=10, hours=2)

        elif "15 Day" in plan:
            expiry_datetime = payment_time + timedelta(days=15, hours=2)

        elif "30 Day" in plan:
            expiry_datetime = payment_time + timedelta(days=31, hours=2)

        else:
            expiry_datetime = payment_time + timedelta(days=30, hours=2)

        payment_time_text = payment_time.strftime("%d-%m-%Y %I:%M:%S %p")
        expiry_time_text = expiry_datetime.strftime("%d-%m-%Y %I:%M:%S %p")

        # USER QR DELETE
        try:

            qr_message_id = context.bot_data["qr_messages"].get(str(user_id))

            if qr_message_id:

                await context.bot.delete_message(
                    chat_id=user_id,
                    message_id=qr_message_id
                )

        except:
            pass

        # USER MESSAGE
        verify_msg = await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🧚🏻 Payment Verified Successfully\n\n"
                "Your key will be delivered shortly."
            )
        )

        # AUTO DELETE MESSAGE WITHOUT DELAY
        asyncio.create_task(
            auto_delete_message(
                context.bot,
                user_id,
                verify_msg.message_id
            )
        )

        # OWNER DELIVERY PANEL
        keyboard = [

            [
                InlineKeyboardButton(
                    "🔑 Delivery Key",
                    callback_data=(
                        f"delivery|{user_id}|{game}|{plan}|"
                        f"{amount}|{order_id}|"
                        f"{payment_time_text}|{expiry_time_text}"
                    )
                )
            ],

            [
                InlineKeyboardButton(
                    "🧚🏻 Cancel",
                    callback_data=f"cancelpayment|{user_id}"
                )
            ]
        ]

        await query.message.edit_text(
            text=(
                "🎁 PAYMENT APPROVED\n\n"
                "Now Send Delivery Key."
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:

        print("APPROVE PAYMENT ERROR :", e)
    
# =========================================
# DELIVERY KEY
# =========================================

async def delivery_key(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data.split("|")

    user_id = int(data[1])
    game = data[2]
    plan = data[3]
    amount = data[4]
    order_id = data[5]
    payment_time = data[6]
    expiry_time = data[7]

    days = (
        plan.replace("💸", "")
        .replace("🍫", "")
        .replace("🍓", "")
        .replace("🧚🏻", "")
        .replace("🍇", "")
        .replace(" ", "")
    )

    game_key = (
        game.upper()
        .replace(" ", "-")
        .replace("[", "")
        .replace("]", "")
    )

    final_key = f"{days}x-{game_key}"

    text = (
        "🎉 *Payment Successful!*\n\n"

        f"🎮 Game : {game}\n"
        f"⏳ Duration : {plan}\n"
        f"💰 Price : ₹{amount}\n\n"

        "📋 *Order Details :*\n\n"

        f"🆔 Order ID : `{order_id}`\n"
        f"🕒 Order Time : {current_time()}\n"
        f"⏰ Payment Time : {payment_time}\n"
        f"⚠️ Expiry Time : {expiry_time}\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🔑 Your Key :\n`{final_key}`\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "❄️ Thanks For Purchasing 💥"
    )

    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode="Markdown"
    )

    await query.message.edit_text(
        "🍓 KeY Delevery Successfully"
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
            cancel_payment,
            pattern=r"^cancelpayment\|"
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
        CallbackQueryHandler(
            approve_payment,
            pattern=r"^approve\|"
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
            delivery_key,
            pattern=r"^delivery\|"
        )
    )

    print("BOT STARTED SUCCESSFULLY")

    app.run_polling()

if __name__ == "__main__":
    main()
