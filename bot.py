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

            "referral_balance": 0,
            "referred_users": [],
            "claimed_keys": []
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

    data = load_data()

    # ==============================
    # CREATE USER
    # ==============================

    if user_id not in data:

        data[user_id] = {

            "name": user.full_name,
            "username": user.username or "",
            "joined": current_time(),
            "last_activity": current_time(),

            "total_orders": 0,
            "orders": [],

            "referral_earnings": 0,
            "total_refers": 0,

            "referral_balance": 0,
            "referred_users": [],
            "claimed_keys": []
        }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    data = load_data()

    # ==============================
    # REFERRAL SYSTEM
    # ==============================

    if context.args:

        ref_arg = context.args[0]

        if ref_arg.startswith("ref_"):

            referrer_id = ref_arg.replace(
                "ref_",
                ""
            )

            # SELF REFERRAL BLOCK
            if referrer_id != user_id:

                if referrer_id in data:

                    # DUPLICATE JOIN BLOCK
                    if user_id not in data[
                        referrer_id
                    ][
                        "referred_users"
                    ]:

                        data[referrer_id][
                            "referred_users"
                        ].append(user_id)

                        data[referrer_id][
                            "total_refers"
                        ] += 1

                        data[referrer_id][
                            "referral_balance"
                        ] += 5

                        data[referrer_id][
                            "referral_earnings"
                        ] += 5

                        try:

                            old_message_id = data[
                                referrer_id
                            ].get(
                                "refer_message_id"
                            )

                            if old_message_id:

                                await context.bot.delete_message(
                                    chat_id=int(referrer_id),
                                    message_id=old_message_id
                                )

                        except:
                            pass

                        try:

                            sent_msg = await context.bot.send_message(

                                chat_id=int(referrer_id),

                                text=(

                                    "🎉 *New Referral Joined Successfully*\n\n"

                                    "💸 *₹5 Added To Your Balance*\n\n"

                                    f"🧚🏻 *Total Refers :* "
                                    f"`{data[referrer_id]['total_refers']}`\n"

                                    f"💰 *Balance :* "
                                    f"`₹{data[referrer_id]['referral_balance']}`"

                                ),

                                parse_mode="Markdown",

                                reply_markup=InlineKeyboardMarkup([

                                    [
                                        InlineKeyboardButton(
                                            "🈲 Back To Main Menu 🧚🏻",
                                            callback_data="main_menu"
                                        )
                                    ]
                                ])
                            )

                            data[referrer_id][
                                "refer_message_id"
                            ] = sent_msg.message_id

                            save_data(data)

                        except:
                            pass       

    # =====================================
    # START MESSAGE
    # =====================================    

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

    # DRIP CLIENT
    keyboard.append([
        InlineKeyboardButton(
            " 🪩 DRIP CLIENT 🥇",
            callback_data="game_Drip ClieNt"
        )
    ])

    # PRIME HOOK
    keyboard.append([
        InlineKeyboardButton(
            "🧚🏻 PRIME HOOK 🎖️",
            callback_data="game_Prime HooK"
        )
    ])

    # PATO TEAM
    keyboard.append([
        InlineKeyboardButton(
            "🐼 PATO TEAM 🍓",
            callback_data="game_PaTo TeaM"
        )
    ])

    # HG CHEATS
    keyboard.append([
        InlineKeyboardButton(
            "👑 HG CHEATS 🚀",
            callback_data="game_Hg ChEaTs"
        )
    ])

    # FLUORITE IOS
    keyboard.append([
        InlineKeyboardButton(
            "🍎 FLUORITE IOS ✨",
            callback_data="game_Fʟᴜᴏʀɪᴛᴇ Ff Ios [Iphone]"
        )
    ])

    # SPOTIFY ENJECT
    keyboard.append([
        InlineKeyboardButton(
            "🎵 SPOTIFY ENJECT 💸",
            callback_data="game_SpotifY EnJecT RooT"
        )
    ])

    # BACK BUTTON
    keyboard.append([
        InlineKeyboardButton(
            "📨 BACK TO MENU",
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
            "📨 BACK",
            callback_data="shop_now"
        )
    ])

    # =====================================
    # DRIP CLIENT
    # =====================================

    if game == "Drip ClieNt":

        text = (
            "╔══════════════════════╗\n"
            "       🪩 *𝘿𝙧𝙞𝙥 𝘾𝙡𝙞𝙚𝙉𝙩* 🥇\n"
            "╚══════════════════════╝\n\n"

            "🔥 *Premium Rage + Legit Experience*\n"
            "⚡ *Ultra Smooth Gameplay*\n"
            "🛡️ *Safe & Stable Protection*\n"
            "🎯 *Powerful Premium Features*\n"
            "🚀 *Trusted By Premium Players*\n\n"

            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    # =====================================
    # PRIME HOOK
    # =====================================

    elif game == "Prime HooK":

        text = (
            "╔══════════════════════╗\n"
            "      🧚🏻 *𝙋𝙧𝙞𝙢𝙚 𝙃𝙤𝙤𝙆* 🎖️\n"
            "╚══════════════════════╝\n\n"

            "🎯 *Deadly Premium Features*\n"
            "🔥 *Ultra Legit Gameplay*\n"
            "🛡️ *Smooth & Secure Client*\n"
            "🚀 *Fastest Performance Ever*\n"
            "💎 *Best Premium Experience*\n\n"

            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    # =====================================
    # PATO TEAM
    # =====================================

    elif game == "PaTo TeaM":

        text = (
            "╔══════════════════════╗\n"
            "       🐼 *𝙋𝙖𝙏𝙤 𝙏𝙚𝙖𝙈* 🍓\n"
            "╚══════════════════════╝\n\n"

            "⚡ *Powerful Premium Gameplay*\n"
            "🎯 *Legit + Rage Features*\n"
            "🔥 *Smooth Aim Experience*\n"
            "🛡️ *High Protection System*\n"
            "🚀 *Trusted By Real Users*\n\n"

            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    # =====================================
    # HG CHEATS
    # =====================================

    elif game == "Hg ChEaTs":

        text = (
            "╔══════════════════════╗\n"
            "      👑 *𝙃𝙜 𝘾𝙝𝙀𝙖𝙏𝙨* 🚀\n"
            "╚══════════════════════╝\n\n"

            "🔥 *High Quality Premium Client*\n"
            "⚡ *Extreme Smooth Gameplay*\n"
            "🎯 *Best Legit Features*\n"
            "🛡️ *Strong Security Protection*\n"
            "🚀 *Stable & Fast Updates*\n\n"

            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    # =====================================
    # FLUORITE IOS
    # =====================================

    elif game == "Fʟᴜᴏʀɪᴛᴇ Ff Ios [Iphone]":

        text = (
            "╔══════════════════════╗\n"
            "      🍎 *𝙁𝙡𝙪𝙤𝙧𝙞𝙩𝙚 𝙄𝙊𝙎* ✨\n"
            "╚══════════════════════╝\n\n"

            "⚡ *Premium IOS Experience*\n"
            "🎯 *Smooth Legit Features*\n"
            "🔥 *Ultra Stable Gameplay*\n"
            "🛡️ *Safe For Iphone Users*\n"
            "🚀 *Luxury Premium Feeling*\n\n"

            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    # =====================================
    # SPOTIFY ENJECT
    # =====================================

    elif game == "SpotifY EnJecT RooT":

        text = (
            "╔══════════════════════╗\n"
            "    🎵 *𝙎𝙥𝙤𝙩𝙞𝙛𝙔 𝙀𝙣𝙅𝙚𝙘𝙏* 💸\n"
            "╚══════════════════════╝\n\n"

            "🔥 *Premium Root Experience*\n"
            "⚡ *Ultra Smooth Injection*\n"
            "🎯 *Powerful Premium Features*\n"
            "🛡️ *Safe & Stable Working*\n"
            "🚀 *Best Performance Ever*\n\n"

            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    # =====================================
    # DEFAULT
    # =====================================

    else:

        text = (
            f"🎮 *{game}*\n\n"
            "🧚🏻 *Select Your Premium Plan Below.*"
        )

    await query.message.edit_text(
        text=text,
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

        # REMOVE PLAN EMOJIS
        clean_plan = (
            plan.replace("💸 ", "")
            .replace("🍫 ", "")
            .replace("🍓 ", "")
            .replace("🧚🏻 ", "")
            .replace("🍇 ", "")
        )

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
            "plan": clean_plan,
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
            f"📦 Plan : {clean_plan}\n"
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

        verify_datetime = datetime.now(IST)

        context.bot_data["verify_orders"][str(user_id)] = {
            "game": game,
            "plan": plan,
            "amount": amount,
            "order_id": order_id,
            "verify_time": verify_datetime.strftime(
                "%d/%m/%Y %I:%M:%S %p"
            )
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

        # REMOVE PLAN EMOJIS
        clean_plan = (
            plan.replace("💸 ", "")
            .replace("🍫 ", "")
            .replace("🍓 ", "")
            .replace("🧚🏻 ", "")
            .replace("🍇 ", "")
        )

        # OWNER REQUEST
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                f"🧚🏻 New Payment Request 🪩\n\n"

                f"🎮 Game : {game}\n"
                f"📦 Plan : {clean_plan}\n"
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
# AUTO DELETE CANCEL MESSAGE
# =========================================

async def auto_delete_cancel_msg(bot, chat_id, message_id):

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

    await query.answer()

    try:

        data = query.data.split("|")

        user_id = int(data[1])

        if "verify_orders" not in context.bot_data:
            return

        if str(user_id) not in context.bot_data["verify_orders"]:
            return

        order_data = context.bot_data["verify_orders"][str(user_id)]

        game = order_data["game"]
        plan = order_data["plan"]
        amount = order_data["amount"]
        order_id = order_data["order_id"]

        # VERIFY BUTTON CLICK TIME
        payment_time = datetime.strptime(
            order_data["verify_time"],
            "%d/%m/%Y %I:%M:%S %p"
        ).replace(tzinfo=IST)

        # EXPIRY TIME
        if "1 Day" in plan:

            expiry_datetime = payment_time + timedelta(
                days=1,
                minutes=13
            )

        elif "3 Day" in plan:

            expiry_datetime = payment_time + timedelta(
                days=3,
                minutes=13
            )

        elif "7 Day" in plan:

            expiry_datetime = payment_time + timedelta(
                days=7,
                minutes=13
            )

        elif "10 Day" in plan:

            expiry_datetime = payment_time + timedelta(
                days=10,
                minutes=13
            )

        elif "15 Day" in plan:

            expiry_datetime = payment_time + timedelta(
                days=15,
                minutes=13
            )

        elif "30 Day" in plan:

            expiry_datetime = payment_time + timedelta(
                days=30,
                minutes=13
            )

        else:

            expiry_datetime = payment_time + timedelta(
                days=30,
                minutes=13
            )

        payment_time_text = payment_time.strftime(
            "%d/%m/%Y %I:%M:%S %p"
        )

        expiry_time_text = expiry_datetime.strftime(
            "%d/%m/%Y %I:%M:%S %p"
        )

        # REMOVE PLAN EMOJIS
        clean_plan = (
            plan.replace("💸 ", "")
            .replace("🍫 ", "")
            .replace("🍓 ", "")
            .replace("🧚🏻 ", "")
            .replace("🍇 ", "")
        )

        # DELETE USER QR
        try:

            qr_message_id = context.bot_data[
                "qr_messages"
            ].get(str(user_id))

            if qr_message_id:

                await context.bot.delete_message(
                    chat_id=user_id,
                    message_id=qr_message_id
                )

        except:
            pass

        # USER VERIFY MESSAGE
        verify_msg = await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🧚🏻 Payment Verified Successfully\n\n"
                "Your key will be delivered shortly."
            )
        )

        # AUTO DELETE AFTER 15 SEC
        asyncio.create_task(
            auto_delete_message(
                context.bot,
                user_id,
                verify_msg.message_id
            )
        )

        # =====================================
        # SAVE DELIVERY DATA
        # =====================================

        data = load_data()

        user_id_str = str(user_id)

        if user_id_str not in data:

            get_user(user_id_str)

            data = load_data()

        if "delivery_data" not in context.bot_data:

            context.bot_data["delivery_data"] = {}

        context.bot_data["delivery_data"][order_id] = {

            "user_id": user_id,
            "game": game,
            "plan": clean_plan,
            "amount": amount,
            "payment_time": payment_time_text,
            "expiry_time": expiry_time_text
        }

        data[user_id_str]["pending_delivery"] = {

            "order_id": order_id,
            "game": game,
            "plan": clean_plan,
            "amount": amount,
            "payment_time": payment_time_text,
            "expiry_time": expiry_time_text
        }

        save_data(data)

        # =====================================
        # SAVE USER ORDER HISTORY
        # =====================================

        data = load_data()

        user_id_str = str(user_id)

        if user_id_str not in data:

            get_user(user_id_str)

            data = load_data()

        try:

            user_info = await context.bot.get_chat(
                user_id
            )

            if user_info.username and user_info.username.lower() != "none":

                username = user_info.username

            else:

                username = "No Username"

        except:

            username = "No Username"

        data[user_id_str]["total_orders"] += 1

        data[user_id_str]["orders"].append({

            "game": game,
            "plan": clean_plan,
            "amount": amount,
            "username": username,
            "user_id": user_id,
            "order_id": order_id,
            "key": "Pending",
            "purchase_time": payment_time_text,
            "expiry_time": expiry_time_text
        })

        save_data(data)
        
        # =====================================
        # OWNER DELIVERY PANEL
        # =====================================

        keyboard = [

            [
                InlineKeyboardButton(
                    "🔑 Delivery Key",
                    callback_data=(
                        f"delivery|"
                        f"{user_id}|"
                        f"{order_id}"
                    )
                )
            ],

            [
                InlineKeyboardButton(
                    "🧚🏻 Cancel",
                    callback_data=(
                        f"cancelpayment|"
                        f"{user_id}"
                    )
                )
            ]
        ]

        await query.message.edit_text(
            text=(
                "╔════════════════════╗\n"
                "  🈲 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 💸\n"
                "╚════════════════════╝\n\n"

                "🎨 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆\n\n"

                "🔑 𝗡𝗼𝘄 𝗦𝗲𝗻𝗱 𝗧𝗵𝗲 𝗣𝗿𝗲𝗺𝗶𝘂𝗺\n"
                "𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆 𝗞𝗲𝘆 𝗧𝗼 𝗧𝗵𝗲 𝗨𝘀𝗲𝗿.\n\n"

                "🧚🏻 𝗗𝗲𝗹𝗶𝘃𝗲𝗿 𝗧𝗵𝗲 𝗞𝗲𝘆 𝗕𝗲𝗹𝗼𝘄."
            ),
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    except Exception as e:

        print(
            "APPROVE PAYMENT ERROR :",
            e
        )
        
# =========================================
# DELIVERY KEY
# =========================================

async def delivery_key(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    try:

        # DOUBLE CLICK FIX
        await query.edit_message_reply_markup(reply_markup=None)

        data = query.data.split("|")

        user_id = int(data[1])
        order_id = data[2]

        data_db = load_data()

        user_id_str = str(user_id)

        if user_id_str not in data_db:
            return

        if "pending_delivery" not in data_db[user_id_str]:
            return

        delivery_data = data_db[user_id_str]["pending_delivery"]

        game = delivery_data["game"]
        plan = delivery_data["plan"]
        amount = delivery_data["amount"]
        payment_time = delivery_data["payment_time"]
        expiry_time = delivery_data["expiry_time"]

        # USERNAME
        try:

            user_info = await context.bot.get_chat(user_id)

            if user_info.username:
                username_text = f"@{user_info.username}"
            else:
                username_text = "No Username"

        except:
            username_text = "No Username"

        # KEY
        try:
            days = plan.split(" ")[0]
        except:
            days = "30Day"

        game_key = (
            game.upper()
            .replace(" ", "-")
            .replace("[", "")
            .replace("]", "")
        )

        final_key = f"{days}x-{game_key}"

        text = (

            "🎉 *Payment Successful!*\n\n"

            f"🎮 *Game :* `{game}`\n"
            f"⏳ *Duration :* `{plan}`\n"
            f"💰 *Price :* `₹{amount}`\n\n"

            "📋 *Order Details :*\n\n"

            f"👤 *Username :* `{username_text}`\n"
            f"🙆🏻‍♂️ *User Id :* `{user_id}`\n\n"

            f"🧾 *Order ID :* `{order_id}`\n"
            f"🕒 *Purchase Time :* `{payment_time}`\n"
            f"⚠️ *Expire Time :* `{expiry_time}`\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            f"🔑 *Your Key :*\n`{final_key}`\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "❄️ *Thanks For Purchasing* 💥"

        )

        # ONLY ONE MESSAGE
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "🏚️ Go To Main Menu 🧚🏻",
                        callback_data="main_menu"
                    )
                ]
            ])
        )

        # UPDATE ORDER
        for order in data_db[user_id_str]["orders"]:

            if order.get("order_id") == order_id:

                order["key"] = final_key
                break

        # REMOVE DELIVERY DATA
        del data_db[user_id_str]["pending_delivery"]

        save_data(data_db)

        await query.message.edit_text(
            "🍓 Key Delivered Successfully 🗳️"
        )

    except Exception as e:

        print("DELIVERY KEY ERROR :", e)

        await query.message.edit_text(
            f"❌ Delivery Failed\n\n{e}"
        )
    
# =========================================
# MY ORDERS
# =========================================

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)

    data = load_data()

    # =====================================
    # NO ORDERS
    # =====================================

    if user_id not in data or not data[user_id]["orders"]:

        text = (
            "╔════════════════════╗\n"
            ".    🛒 𝗡𝗢 𝗢𝗥𝗗𝗘𝗥𝗦 𝗬𝗘𝗧 🍓\n"
            "╚════════════════════╝\n\n"

            "✨ 𝗬𝗼𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗖𝗼𝗹𝗹𝗲𝗰𝘁𝗶𝗼𝗻 𝗜𝘀 𝗘𝗺𝗽𝘁𝘆\n\n"

            "🚀 𝗬𝗼𝘂 𝗛𝗮𝘃𝗲𝗻'𝘁 𝗣𝘂𝗿𝗰𝗵𝗮𝘀𝗲𝗱 𝗔𝗻𝘆\n"
            "𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗣𝗿𝗼𝗱𝘂𝗰𝘁𝘀 𝗬𝗲𝘁 𝗙𝗿𝗼𝗺 𝗢𝘂𝗿 𝗦𝘁𝗼𝗿𝗘.\n\n"

            "🎯 𝗦𝘁𝗮𝗿𝘁 𝗦𝗵𝗼𝗽𝗽𝗶𝗻𝗴 𝗧𝗼 𝗨𝗻𝗹𝗼𝗰𝗸\n"
            "𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀 & 𝗜𝗻𝘀𝘁𝗮𝗻𝘁 𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝘆.\n\n"

            "🧚🏻 𝗖𝗹𝗶𝗰𝗸 𝗕𝗲𝗹𝗼𝘄 𝗕𝘂𝘁𝘁𝗼𝗻 𝗧𝗼 𝗦𝘁𝗮𝗿𝘁\n"
            "𝗦𝗵𝗼𝗽𝗽𝗶𝗻𝗴."
        )

        keyboard = [

            [
                InlineKeyboardButton(
                    "🎨 Shop Now 🈲",
                    callback_data="shop_now"
                )
            ],

            [
                InlineKeyboardButton(
                    "🍓 Back To Menu",
                    callback_data="main_menu"
                )
            ]
        ]

        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # =====================================
    # USER ORDERS
    # =====================================

    orders = data[user_id]["orders"]

    text = (
        "╔════════════════════╗\n"
        "     📦 𝗠𝗬 𝗢𝗥𝗗𝗘𝗥𝗦 🧚🏻\n"
        "╚════════════════════╝\n\n"
    )

    for count, order in enumerate(orders, start=1):

        text += (

            f"✨ Order {count}\n\n"

            f"🎮 Game : {order['game']}\n"
            f"⏳ Plan : {order['plan']}\n"
            f"💰 Price : ₹{order['amount']}\n\n"

            f"🧑🏻 Username : "
            f"{('@' + order['username']) if order.get('username') != 'No Username' else 'No Username'}\n"

            f"🥇 User ID : {order['user_id']}\n"

            f"🧾 Order ID : "
            f"{order.get('order_id', 'Not Available')}\n\n"

            f"🕒 Purchase Time :\n"
            f"{order['purchase_time']}\n\n"

            f"⚠️ Expire Time :\n"
            f"{order['expiry_time']}\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            f"🔑 Key :\n"
            f"<code>{order.get('key', 'Pending')}</code>\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"
        )

    keyboard = [

        [
            InlineKeyboardButton(
                "📨 Back To Menu",
                callback_data="main_menu"
            )
        ]
    ]

    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    user_data = get_user(user_id)

    total_refers = user_data.get("total_refers", 0)
    earnings = user_data.get("referral_earnings", 0)

    bot_username = (await context.bot.get_me()).username

    referral_link = (
        f"https://t.me/{bot_username}?start=ref_{user_id}"
    )

    text = (

        "╔════════════════════╗\n"
        "    🎁 𝗥𝗘𝗙𝗘𝗥 & 𝗘𝗔𝗥𝗡 💸\n"
        "╚════════════════════╝\n\n"

        "✨ *Invite Your Friends & Earn Money*\n\n"

        "🚀 Share your referral link with friends.\n"
        "💰 When someone joins using your link,\n"
        "you will receive *₹5 reward instantly.*\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🔗 *Your Invite Link :*\n"
        f"`{referral_link}`\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🙆🏻‍♂️ *Total Refers :* `{total_refers}`\n"
        f"💸 *Referral Balance :* `₹{earnings}`\n\n"

        "🎯 *Keep Sharing & Unlock Free Premium Keys!*"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "📤 Share With Friends",
                url=f"https://t.me/share/url?url={referral_link}"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 Claim Free Key",
                callback_data="claim_free_key"
            )
        ],

        [
            InlineKeyboardButton(
                "🧚🏻 Back To Main Menu",
                callback_data="main_menu"
            )
        ]
    ]

    sent_msg = await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    data = load_data()

    data[user_id]["refer_message_id"] = sent_msg.message_id

    save_data(data)
    
# =========================================
# CLAIM FREE KEY
# =========================================

async def claim_free_key(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    user_id = str(query.from_user.id)

    data = load_data()

    # AUTO CREATE USER
    if user_id not in data:

        get_user(user_id)

        data = load_data()

    balance = data[user_id].get(
        "referral_earnings",
        0
    )

    # ==============================
    # NOT ENOUGH BALANCE
    # ==============================

    if balance < 550:

        need = 550 - balance

        # IMPORTANT FIX
        try:
            await query.answer(
                text=(
                    "💎 𝗙𝗥𝗘𝗘 𝗞𝗘𝗬 𝗜𝗡𝗙𝗢 💎\n\n"

                    "🔑 𝗞𝗲𝘆 𝗡𝗮𝗺𝗲 : 𝗗𝗿𝗶𝗽 𝗖𝗹𝗶𝗲𝗻𝘁\n"
                    "⏳ 𝗣𝗹𝗮𝗻 : 𝟭𝟱 𝗗𝗮𝘆\n"
                    "💰 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : ₹𝟱𝟱𝟬\n\n"

                    f"💸 𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : ₹{balance}\n"
                    f"❌ 𝗡𝗲𝗲𝗱 𝗠𝗼𝗿𝗲 : ₹{need}\n\n"

                    "👥 𝗜𝗻𝘃𝗶𝘁𝗲 𝗙𝗿𝗶𝗲𝗻𝗱𝘀 & 𝗘𝗮𝗿𝗻 𝗠𝗼𝗿𝗲\n"
                    "🚀 𝗧𝗵𝗲𝗻 𝗖𝗹𝗮𝗶𝗺 𝗬𝗼𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗞𝗲𝘆"
                ),
                show_alert=True
            )
        except Exception as e:
            print("POPUP ERROR :", e)

        return

    # ==============================
    # ALREADY CLAIMED
    # ==============================

    if "FREE-KEY" in data[user_id].get(
        "claimed_keys",
        []
    ):

        await query.answer(
            text="🈲 You Already Claimed Free Key 🧚🏻",
            show_alert=True
        )

        return

    # ==============================
    # REMOVE BALANCE
    # ==============================

    data[user_id]["referral_earnings"] -= 550

    # SAVE CLAIM
    data[user_id]["claimed_keys"].append(
        "FREE-KEY"
    )

    save_data(data)

    # RANDOM KEY
    free_key = (
        "FREE-KEY-" +
        ''.join(
            random.choices(
                string.ascii_uppercase +
                string.digits,
                k=10
            )
        )
    )

    text = (

        "╔════════════════════╗\n"
        "  🎁 𝗙𝗥𝗘𝗘 𝗞𝗘𝗬 𝗖𝗟𝗔𝗜𝗠𝗘𝗗 🔥\n"
        "╚════════════════════╝\n\n"

        "✨ 𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀 𝗕𝘂𝗱𝗱𝘆 ✨\n\n"

        "🎮 𝗠𝗼𝗱 𝗡𝗮𝗺𝗲 : 𝗗𝗿𝗶𝗽 𝗖𝗹𝗶𝗲𝗡𝘁\n"
        "⏳ 𝗣𝗹𝗮𝗻 : 𝟭𝟱 𝗗𝗮𝘆\n"
        "💸 𝗣𝗿𝗶𝗰𝗲 : ₹𝟱𝟱𝟬\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🔑 𝗬𝗼𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗞𝗲𝘆 :\n\n`{free_key}`\n\n"

        "━━━━━━━━━━━━━━━━━━"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🍓 Back To Main Menu",
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
            approve_payment,
            pattern=r"^approve\|"
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
            claim_free_key,
            pattern="^claim_free_key$"
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
