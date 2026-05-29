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
    MessageHandler,
    filters
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

OWNER_USERNAME = "BeStChEaT_OwNeR"

OWNER_ID = 7614459746
owner_users = [OWNER_ID]

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
# UPDATE LAST ACTIVITY
# =========================================

def update_last_activity(user_id, button_name="Unknown"):

    data = load_data()

    user_id = str(user_id)

    if user_id not in data:
        get_user(user_id)
        data = load_data()

    now = datetime.now(IST)

    data[user_id]["last_activity"] = (
        now.strftime("%d/%m/%Y %I:%M:%S %p")
    )

    data[user_id]["last_button"] = button_name

    data[user_id]["last_activity_timestamp"] = (
        now.strftime("%H:%M:%S")
    )

    save_data(data)
    
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

def main_menu_keyboard(user_id=None):

    keyboard = [

        [
            InlineKeyboardButton(
                "🗳️ ALL GAMES HACKS FF 🛒",
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

    # OWNER BUTTON AUTO FIX
    if user_id and int(user_id) == OWNER_ID:

        keyboard.append([
            InlineKeyboardButton(
                "🧝🏻‍♀️ AuRa KaRtiK FaTheR 🈲",
                callback_data="owner_panel"
            )
        ])

    return InlineKeyboardMarkup(keyboard)
    
# =========================================
# START
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return

    user_id = str(update.effective_user.id)

    data = load_data()

    user = update.effective_user

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

        save_data(data)
        
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

                                    f"🈲 *Balance :* "
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

    keyboard = list(main_menu_keyboard().inline_keyboard)

    if is_owner(user_id):
        keyboard.append([
            InlineKeyboardButton(
                "🧝🏻‍♀️ AuRa KaRtiK FaTheR 🈲",
                callback_data="owner_panel"
            )
        ])

    await update.message.reply_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================================
# MAIN MENU
# =========================================

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "MAIN MENU"
    )

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

    keyboard = list(main_menu_keyboard().inline_keyboard)

    # OWNER BUTTON FIX
    if is_owner(query.from_user.id):
        keyboard.append([
            InlineKeyboardButton(
                "🧝🏻‍♀️ AuRa KaRtiK FaTheR 🈲",
                callback_data="owner_panel"
            )
        ])

    await query.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(query.from_user.id)
    )

# =========================================
# SHOP
# =========================================

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "SHOP NOW"
    )
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

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "GAME PLANS"
    )
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

    if await check_banned(update):
        return
    
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "CREATE PAYMENT"
    )
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

    if await check_banned(update):
        return
        
    query = update.callback_query

    await query.answer()

    update_last_activity(
        query.from_user.id,
        "VERIFY PAYMENT"
    )
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

            "username": username,
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
            text=(
                "╔════════════════════╗\n"
                " 🧚🏻 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 🪩\n"
                "╚════════════════════╝\n\n"

                "🔍 <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗪𝗔𝗜𝗧...</b>\n\n"

                "⚡ <b>𝗬𝗼𝘂𝗿 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗜𝘀 𝗕𝗲𝗶𝗻𝗴</b>\n"
                "<b>𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱 𝗕𝘆 𝗢𝘂𝗿 𝗦𝘆𝘀𝘁𝗲𝗺.</b>"
            ),
            parse_mode="HTML"
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
                "╔════════════════════╗\n"
                " 🧚🏻 <b>𝗡𝗘𝗪 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗥𝗘𝗤𝗨𝗘𝗦𝗧</b> 🪩\n"
                "╚════════════════════╝\n\n"

                f"🎮 <b>𝗚𝗔𝗠𝗘 :</b> "
                f"<b>{game}</b>\n\n"

                f"📦 <b>𝗣𝗟𝗔𝗡 :</b> "
                f"<b>{clean_plan}</b>\n\n"

                f"💵 <b>𝗣𝗥𝗜𝗖𝗘 :</b> "
                f"<b>₹{amount}</b>\n\n"

                f"🆔 <b>𝗢𝗥𝗗𝗘𝗥 𝗜𝗗 :</b>\n"
                f"<code>{order_id}</code>\n\n"

                f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗗 :</b>\n"
                f"<code>{user_id}</code>\n\n"

                f"🌐 <b>𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :</b> "
                f"<b>{username_text}</b>\n\n"

                f"🕒 <b>𝗩𝗘𝗥𝗜𝗙𝗬 𝗧𝗜𝗠𝗘 :</b>\n"
                f"<b>{verify_time}</b>"
            ),
            parse_mode="HTML",
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

    if await check_banned(update):
        return
    
    query = update.callback_query

    await query.answer()

    update_last_activity(
        query.from_user.id,
        "CANCEL ORDER"
    )
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
        reply_markup=main_menu_keyboard(query.from_user.id)
    )
    
# =========================================
# CANCEL PAYMENT
# =========================================

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return
    
    query = update.callback_query

    await query.answer()

    update_last_activity(
        query.from_user.id,
        "CANCEL PAYMENT"
    )
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
            text=(
                "╔════════════════════╗\n"
                " 🍫 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗 🎭\n"
                "╚════════════════════╝\n\n"

                "❌ <b>𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗</b>\n\n"

                "⚡ <b>𝗨𝘀𝗲𝗿 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗛𝗮𝘀</b>\n"
                "<b>𝗕𝗲𝗲𝗻 𝗖𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱.</b>"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "🧚🏻 Go To Back Main Menu 🪩",
                        callback_data="main_menu"
                    )
                ]
            ])
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

# REMOVE FROM PENDING PAYMENTS
    verify_orders = context.bot_data.get(
        "verify_orders",
        {}
    )

    if str(user_id) in verify_orders:

        del verify_orders[
            str(user_id)
        ]

    elif user_id in verify_orders:

        del verify_orders[
            user_id
        ]

    # REMOVE PENDING DELIVERY
    data = load_data()

    user_id_str = str(user_id)

    if user_id_str in data:

        if "pending_delivery" in data[user_id_str]:

            del data[user_id_str][
                "pending_delivery"
            ]

    save_data(data)
    
    # USER MESSAGE
    sent_msg = await context.bot.send_message(
        chat_id=user_id,
        text=(
            "⚠️ 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗡𝗢𝗧 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗 𝗬𝗘𝗧\n\n"
            "🧚🏻 𝗣𝗹𝗲𝗮𝘀𝗘 𝗧𝗿𝘆 𝗔𝗴𝗮𝗶𝗻\n"
            "𝗜𝗻 𝗔 𝗙𝗲𝘄 𝗦𝗲𝗰𝗼𝗻𝗱𝘀."
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
  
# =========================================
# APPROVE PAYMENT
# =========================================

async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return
    
    query = update.callback_query

    await query.answer()

    update_last_activity(
        query.from_user.id,
        "APPROVE PAYMENT"
    )
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
                "╔════════════════════╗\n"
                " 🧚🏻 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗 🪩\n"
                "╚════════════════════╝\n\n"

                "🈲 <b>𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗</b>\n\n"

                "⚡ <b>𝗬𝗼𝘂𝗿 𝗞𝗲𝘆 𝗪𝗶𝗹𝗹 𝗕𝗲</b>\n"
                "<b>𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝗲𝗱 𝗦𝗵𝗼𝗿𝘁𝗹𝘆.</b>"
            ),
            parse_mode="HTML"
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

        # REMOVE FROM PENDING PAYMENTS
        if "verify_orders" in context.bot_data:

            if str(user_id) in context.bot_data["verify_orders"]:
                del context.bot_data["verify_orders"][str(user_id)]

            elif user_id in context.bot_data["verify_orders"]:
                del context.bot_data["verify_orders"][user_id]

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

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "DELIVERY KEY"
    )
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
                    text=(
                        "╔════════════════════╗\n"
                        "  🍓 𝗞𝗘𝗬 𝗗𝗘𝗟𝗜𝗩𝗘𝗥𝗘𝗗 🗳️\n"
                        "╚════════════════════╝\n\n"

                        "🧝🏻‍♀️ <b>𝗞𝗘𝗬 𝗗𝗘𝗟𝗜𝗩𝗘𝗥𝗘𝗗</b>\n\n"

                        "⚡ <b>𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗞𝗲𝘆 𝗛𝗮𝘀</b>\n"
                        "<b>𝗕𝗲𝗲𝗻 𝗦𝗲𝗻𝘁 𝗧𝗼 𝗨𝘀𝗲𝗿.</b>"
                    ),
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([

                        [
                            InlineKeyboardButton(
                                "🧚🏻 Go To Back Main Menu 🪩",
                                callback_data="main_menu"
                            )
                         ]
                    ])
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

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "MY ORDERS"
    )
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

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "PROFILE"
    )
    user_id = str(query.from_user.id)

    user_data = get_user(user_id)

    username = user_data.get("username")

    if username:
        username = f"@{username}"
    else:
        username = "Not Set"

    text = (
        "╔══════════════════╗\n"
        "  🆈🅾🆄🆁 🅿🆁🅾🅵🅸🅻🅴\n"
        "╚══════════════════╝\n\n"

        f"🙆🏻‍♂️ <b>𝗡𝗮𝗺𝗘 :</b> <i>{user_data['name']}</i>\n"
        f"🥇 <b>𝗨𝘀𝗘𝗿𝗻𝗮𝗺𝗘 :</b> <i>{username}</i>\n"
        f"🧾 <b>𝗨𝘀𝗘𝗿 𝗜𝗗 :</b> <code>{user_id}</code>\n\n"

        "╔══════════════════╗\n"
        "   🆈🅾🆄🆁 🆂🆃🅰🆃🆄🆂 \n"
        "╚══════════════════╝\n\n"

        f"🗳️ <b>𝗧𝗼𝘁𝗮𝗹 𝗢𝗿𝗱𝗘𝗿𝘀 :</b> <i>{user_data['total_orders']}</i>\n"
        f"📩 <b>𝗥𝗘𝗳𝗘𝗿𝗿𝗮𝗹 𝗘𝗮𝗿𝗻𝗶𝗻𝗴𝘀 :</b> <i>₹{user_data['referral_earnings']:.2f}</i>\n"
        f"🧙🏻‍♂️ <b>𝗧𝗼𝘁𝗮𝗹 𝗥𝗘𝗳𝗘𝗿𝘀 :</b> <i>{user_data['total_refers']}</i>\n\n"

        "╔══════════════════╗\n"
        " 🅰🅲🆃🅸🆅🅸🆃🆈 🆃🅸🅼🅴\n"
        "╚══════════════════╝\n\n"

        f"📅 <b>𝗝𝗼𝗶𝗻𝗘𝗱 :</b> <i>{user_data['joined']}</i>\n\n"

        f"🧙🏻‍♂️ <b>𝗟-𝗦𝗲𝗲𝗡 :</b> "
        f"<i>{user_data.get('last_activity', 'Unknown')}</i>\n\n"

        f"🧝🏻‍♀️ <b>𝗥𝗲𝗖𝗲𝗻𝘁 𝗖𝗹𝗶𝗰𝗞 :</b> "
        f"<i>{user_data.get('last_button', 'None')}</i>"
    )
    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🈲 Go Back To Main Menu 🧚🏻",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================
# HOW TO USE
# =========================================

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "HOW TO USE"
    )
    await query.message.edit_text(
        text=(
            "╔══════════════════════╗\n"
            "    🈲 🅷🅾🆆 🆃🅾 🆄🆂🅴 🧚🏻\n"
            "╚══════════════════════╝\n\n"

            "✨ *𝗪𝗲𝗹𝗰𝗼𝗺𝗘 𝗧𝗼 𝗕𝗲𝗦𝘁𝗖𝗵𝗲𝗮𝘁*\n"
            "*𝗣𝗿𝗘𝗺𝗶𝘂𝗺 𝗦𝘁𝗼𝗿𝗘* ✨\n\n"

            "🧚🏻 *𝗙𝗼𝗹𝗹𝗼𝘄 𝗔𝗹𝗹 𝗦𝘁𝗲𝗽𝘀*\n"
            "*𝗖𝗮𝗿𝗘𝗳𝘂𝗹𝗹𝘆 𝗧𝗼 𝗚𝗲𝘁*\n"
            "*𝗬𝗼𝘂𝗿 𝗣𝗿𝗘𝗺𝗶𝘂𝗺 𝗞𝗘𝘆*\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "1️⃣ *𝗖𝗹𝗶𝗰𝗸 𝗢𝗻*\n"
            "🛒 *𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗛𝗢𝗣*\n\n"

            "2️⃣ *𝗦𝗘𝗹𝗘𝗰𝘁 𝗬𝗼𝘂𝗿*\n"
            "🎮 *𝗙𝗮𝘃𝗼𝗿𝗶𝘁𝗘 𝗚𝗮𝗺𝗘*\n\n"

            "3️⃣ *𝗖𝗵𝗼𝗼𝘀𝗘 𝗬𝗼𝘂𝗿*\n"
            "⏳ *𝗣𝗿𝗘𝗺𝗶𝘂𝗺 𝗣𝗹𝗮𝗻*\n\n"

            "4️⃣ *𝗦𝗰𝗮𝗻 𝗧𝗵𝗘*\n"
            "💸 *𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗤𝗥*\n\n"

            "5️⃣ *𝗖𝗼𝗺𝗽𝗹𝗘𝘁𝗘 𝗣𝗮𝘆𝗺𝗘𝗻𝘁*\n"
            "*𝗔𝗻𝗱 𝗖𝗹𝗶𝗰𝗸*\n"
            "🧚🏻 *𝗩𝗘𝗥𝗜𝗙𝗬 𝗣𝗔𝗬𝗠𝗘𝗡𝗧*\n\n"

            "6️⃣ *𝗚𝗘𝘁 𝗬𝗼𝘂𝗿*\n"
            "🔑 *𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗞𝗘𝗬*\n"
            "*𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬*\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "🎨 *𝗙𝗮𝘀𝘁 𝗗𝗘𝗹𝗶𝘃𝗘𝗿𝘆*\n"
            "🛡️ *𝗦𝗮𝗳𝗘 & 𝗧𝗿𝘂𝘀𝘁𝗘𝗱*\n"
            "🚀 *𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗘𝗥𝗩𝗜𝗖𝗘*\n\n"

            "🔻 *𝗖𝗹𝗶𝗰𝗸 𝗕𝗮𝗰𝗸*\n"
            "*𝗧𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗘 𝗦𝗵𝗼𝗽𝗽𝗶𝗻𝗴*"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🪄 Go Back To Main Menu 🧝🏻‍♀️",
                    callback_data="main_menu"
                )
            ]
        ])
    )
    
# =========================================
# SUPPORT CENTER
# =========================================

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if await check_banned(update):
        return
        
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "SUPPORT"
    )
    text = (
        "╔══════════════════════╗\n"
        " 🈲 🆂🆄🅿🅿🅾🆁🆃 🅲🅴🅽🆃🅴🆁\n"
        "╚══════════════════════╝\n\n"

        "✨ *𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹 𝗕𝗲𝗦𝘁𝗖𝗵𝗲𝗮𝘁\n"
        "𝗦𝘂𝗽𝗽𝗼𝗿𝘁* ✨\n\n"

        "🧚🏻 *𝗡𝗲𝗲𝗱 𝗛𝗲𝗹𝗽 𝗪𝗶𝘁𝗵 𝗣𝘂𝗿𝗰𝗵𝗮𝘀𝗲,\n"
        "𝗞𝗲𝘆, 𝗟𝗼𝗴𝗶𝗻 𝗢𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺\n"
        "𝗦𝗲𝘁𝘂𝗽?* \n\n"

        "🧙🏻‍♂️ *𝗢𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗦𝘂𝗽𝗽𝗼𝗿𝘁\n"
        "𝗧𝗲𝗮𝗺 𝗜𝘀 𝗔𝗹𝘄𝗮𝘆𝘀 𝗥𝗲𝗮𝗱𝘆\n"
        "𝗧𝗼 𝗛𝗲𝗹𝗽 𝗬𝗼𝘂*\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "🧝🏻‍♀️ *𝗙𝗮𝘀𝘁 𝗥𝗲𝗽𝗹𝘆 𝗚𝘂𝗮𝗿𝗮𝗻𝘁𝗲𝗲*\n"
        "🛡️ *𝗧𝗿𝘂𝘀𝘁𝗲𝗱 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝗰𝗲*\n"
        "🎨 *𝗙𝗿𝗶𝗲𝗻𝗱𝗹𝘆 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗦𝘂𝗽𝗽𝗼𝗿𝘁*\n"
        "🪄 *𝟮𝟰×𝟳 𝗔𝗰𝘁𝗶𝘃𝗲 𝗦𝗲𝗿𝘃𝗶𝗰𝗲*\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "🔻 *𝗖𝗹𝗶𝗰𝗸 𝗧𝗵𝗲 𝗕𝘂𝘁𝘁𝗼𝗻 𝗕𝗲𝗹𝗼𝘄\n"
        "𝗧𝗼 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹\n"
        "𝗢𝘄𝗻𝗲𝗿*"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "🈲 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 🧚🏻",
                url="http://BESTCHEAT_OWNER.t.me"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 🧿",
                url="https://t.me/+vWCKsh56iIpiOWQ9"
            )
        ],
        
        [
            InlineKeyboardButton(
                "🍓 Back To Main Menu 🎨",
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

    if await check_banned(update):
        return
    
    query = update.callback_query
    await query.answer()

    update_last_activity(
        query.from_user.id,
        "REFER & EARN"
    )
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

    if user_id not in data:
        data[user_id] = {}

    data[user_id]["refer_message_id"] = sent_msg.message_id

    save_data(data)
    
# =========================================
# CLAIM FREE KEY
# =========================================

async def claim_free_key(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    update_last_activity(
        query.from_user.id,
        "CLAIM FREE KEY"
    )
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
                    "🧚🏻 🅵🆁🅴🅴 🅺🅴🆈 🅸🅽🅵🅾 🈲\n\n"

                    "🔑 𝗞𝗲𝘆 𝗡𝗮𝗺𝗲 : 𝗗𝗿𝗶𝗽 𝗖𝗹𝗶𝗲𝗻𝘁\n"
                    "⏳ 𝗣𝗹𝗮𝗻 : 𝟭𝟱 𝗗𝗮𝘆\n"
                    "🎨 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : ₹𝟱𝟱𝟬\n\n"

                    f"💸 𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : ₹{balance}\n"
                    f"🈲 𝗡𝗲𝗲𝗱 𝗠𝗼𝗿𝗲 : ₹{need}\n\n"

                    "🙆🏻‍♂️ 𝗜𝗻𝘃𝗶𝘁𝗲 𝗙𝗿𝗶𝗲𝗻𝗱𝘀 & 𝗘𝗮𝗿𝗻 𝗠𝗼𝗿𝗲\n"
                    "🧚🏻 𝗧𝗵𝗲𝗻 𝗖𝗹𝗮𝗶𝗺 𝗬𝗼𝘂𝗿 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗞𝗲𝘆"
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
# OWNER SYSTEM
# =========================================

BANNED_USERS = set()

def is_owner(user_id):
    return int(user_id) == OWNER_ID

def owner_panel_keyboard():
    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton("📩 SeNd MeSSaGe 🪩", callback_data="send_message_panel"),
        ],
            
        [
            InlineKeyboardButton("📊 Status", callback_data="owner_stats"),
            InlineKeyboardButton("🧝🏻‍♀️ Users", callback_data="owner_users")
        ],

        [
            InlineKeyboardButton("🛒 Pending", callback_data="owner_pending"),
            InlineKeyboardButton("🌈 Verified", callback_data="owner_verified")
        ],

        [
            InlineKeyboardButton("🕹️ Activity", callback_data="owner_activity"),            
        ],

        [
           InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
           InlineKeyboardButton("🕹️ Unban User", callback_data="unban_user")
        ],

        [
            InlineKeyboardButton("🎨 Main Menu", callback_data="main_menu")
        ]
    ])

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    total_users = len(data)

    total_orders = 0
    total_earnings = 0

    for user_data in data.values():

        total_orders += user_data.get("total_orders", 0)

        for order in user_data.get("orders", []):
            total_earnings += int(order.get("amount", 0))

    text = (
        "╔════════════════════╗\n"
        " <b>  OWNER CONTROL PANEL</b>\n"
        "╚════════════════════╝\n\n"

        f"🧙🏻‍♂️ <b>TOTAL USERS :</b> <code>{total_users}</code>\n\n"

        f"🛒 <b>TOTAL ORDERS :</b> <code>{total_orders}</code>\n\n"

        f"💸 <b>TOTAL EARNINGS :</b> <code>₹{total_earnings}</code>\n\n"

        "<b>🍓 PREMIUM OWNER CONTROLS ACTIVE</b>"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=owner_panel_keyboard()
    )

async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    # TOTAL USERS
    total_users = len(data)

    # ACTIVE USERS
    active_users = 0

    # BLOCKED USERS
    blocked_users = len(BANNED_USERS)

    # ADMINS
    total_admins = 1

    # DELIVERIES
    total_deliveries = 0

    for user_data in data.values():

        orders = user_data.get("orders", [])

        total_deliveries += len(orders)

        if user_data.get("last_activity"):
            active_users += 1

# =========================================
# SEND MESSAGE PANEL
# =========================================

async def send_message_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    text = (
        "╔════════════════════╗\n"
        "    📩 <b>𝗦𝗘𝗡𝗗 𝗠𝗘𝗦𝗦𝗔𝗚𝗘</b>\n"
        "╚════════════════════╝\n\n"

        "🎭 <b>Select Message Style</b>"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "📝 Normal ❄️",
                    callback_data="msg_normal"
                ),

                InlineKeyboardButton(
                    "🧝🏻‍♀️ Bold 🧚🏻",
                    callback_data="msg_bold"
                )
            ],

            [
                InlineKeyboardButton(
                    "🌈 Italic 🎨",
                    callback_data="msg_italic"
                ),

                InlineKeyboardButton(
                    "🍫 Bold + Italic 🍓",
                    callback_data="msg_bolditalic"
                )
            ],

            [
                InlineKeyboardButton(
                    "🏚️ Premium 🧛🏻‍♂️",
                    callback_data="msg_premium"
                )
            ],

            [
                InlineKeyboardButton(
                    "🧙🏻‍♂️ BacK 🪩",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🌈 MaiN MenU 🈲",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================
# SELECT MESSAGE STYLE
# =========================================

async def select_message_style(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    style = query.data.replace(
        "msg_",
        ""
    )

    context.user_data["broadcast_style"] = style

    await query.message.reply_text(

        "📝 <b>𝗦𝗘𝗡𝗗 𝗬𝗢𝗨𝗥 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗡𝗢𝗪</b>\n\n"

        "⚡ <b>𝗦𝗘𝗟𝗘𝗖𝗧𝗘𝗗 𝗦𝗧𝗬𝗟𝗘 𝗦𝗔𝗩𝗘𝗗</b>\n\n"

        "🌈 <b>Your Message Will Be Sent</b>\n"
        "<b>In Selected Premium Style</b>",

        parse_mode="HTML",
    )

    context.user_data["waiting_broadcast"] = True

# =========================================
# BROADCAST MESSAGE
# =========================================

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.user_data.get("waiting_broadcast"):
        return

    context.user_data["waiting_broadcast"] = False

    style = context.user_data.get(
        "broadcast_style",
        "normal"
    )

    msg = update.message.text

    if style == "bold":

        msg = f"<b>{msg}</b>"

    elif style == "italic":

        msg = f"<i>{msg}</i>"

    elif style == "bolditalic":

        msg = f"<b><i>{msg}</i></b>"

    elif style == "premium":

        msg = (
            "╔════════════════════╗\n"
            "   ⚠️ <b> 𝗡𝗢𝗧𝗜𝗖𝗘 𝗕𝗢𝗔𝗥𝗗 </b> 🚫\n"
            "╚════════════════════╝\n\n"

            f"<b>{msg}</b>"
        )

    data = load_data()

    success = 0

    for uid in data:

        try:

            await context.bot.send_message(
                chat_id=int(uid),
                text=msg,
                parse_mode="HTML"
            )

            success += 1

        except:
            pass

    await update.message.reply_text(

          f"🧚🏻 <b>𝗠𝗘𝗦𝗦𝗔𝗚𝗘 𝗦𝗘𝗡𝗧 𝗧𝗢 {success} 𝗨𝗦𝗘𝗥𝗦</b>",

        parse_mode="HTML"
    )
    
# =========================================
# OWNER USERS
# =========================================

async def owner_users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    text = ""

    if not data:

        text = (
            "❌ <b>𝗡𝗼 𝗨𝘀𝗲𝗿𝘀 𝗙𝗼𝘂𝗻𝗱</b>"
        )

    else:

for uid, user_data in data.items():

            username = user_data.get("username")

            if username:
                username = f"@{username}"
            else:
                username = "Not Set"

            first_name = user_data.get("name")

            if not first_name:
                first_name = "Not Available"

            text += (

                "<b>🆄🆂🅴🆁🆂 🅷🅸🆂🆃🅾🆁🆈</b>\n\n"

                f"🥇 <b>𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :</b> "
                f"<b>{username}</b>\n\n"

                f"🙆🏻‍♂️ <b>𝗨𝗦𝗘𝗥 𝗜𝗗 :</b>\n"
                f"<code>{uid}</code>\n\n"

                f"👤 <b>𝗡𝗔𝗠𝗘 :</b> "
                f"<b>{first_name}</b>\n\n"

                f"📅 <b>𝗝𝗢𝗜𝗡𝗘𝗗 :</b>\n"
                f"<b>{user_data.get('joined', 'Unknown')}</b>\n\n"

                "━━━━━━━━━━━━━━━━━━\n\n"
            )

            text += (

                "<b>🆄🆂🅴🆁🆂 🅷🅸🆂🆃🅾🆁🆈</b>\n\n"

                f"🥇 <b>𝗨𝘀𝗘𝗿𝗻𝗮𝗺𝗘 :</b> <i>{username}</i>\n"

                f"🙆🏻‍♂️ <b>𝗨𝗦𝗘𝗥 𝗜𝗗 :</b>\n"
                f"<code>{uid}</code>\n\n"

                f"🙆🏻‍♂️ <b>𝗡𝗮𝗺𝗘 :</b> <i>{user_data['name']}</i>\n"

                f"📅 <b>𝗝𝗢𝗜𝗡𝗘𝗗 :</b>\n"
                f"<b>{user_data.get('joined', 'Unknown')}</b>\n\n"

                "━━━━━━━━━━━━━━━━━━\n\n"
            )

    await query.message.edit_text(
        text=text[:4000],
        parse_mode="HTML",
reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🈲 UpDaTe 📜",
                    callback_data="owner_users"
                )
            ],

            [
                InlineKeyboardButton(
                    "🧝🏻‍♀️ BacK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🌈 MaiN MenU",
                    callback_data="main_menu"
                )
            ]
        ])
    )
    
# =========================================
# BOT LIVE STATUS
# =========================================

async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    # TOTAL USERS
    total_users = len(data)

    # ACTIVE USERS
    active_users = 0

    # BLOCKED USERS
    blocked_users = len(BANNED_USERS)

    # ADMINS
    total_admins = 1

    # DELIVERIES
    total_deliveries = 0

    for user_data in data.values():

        orders = user_data.get("orders", [])

        total_deliveries += len(orders)

        if user_data.get("last_activity"):
            active_users += 1

    text = (

        "<b>🅱🅾🆃 🅻🅸🆅🅴 🆂🆃🅰🆃🆄🆂</b>\n\n"

        f"🙆🏻‍♂️ <b>𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀 :</b> "
        f"<code>{total_users}</code>\n\n"

        f"🧝🏻‍♀️ <b>𝗔𝗰𝘁𝗶𝘃𝗲 𝗨𝘀𝗲𝗿𝘀 :</b> "
        f"<code>{active_users}</code>\n\n"

        f"🚫 <b>𝗕𝗹𝗼𝗰𝗸𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 :</b> "
        f"<code>{blocked_users}</code>\n\n"

        f"👨‍💻 <b>𝗧𝗼𝘁𝗮𝗹 𝗔𝗱𝗺𝗶𝗻𝘀 :</b> "
        f"<code>{total_admins}</code>\n\n"

        f"🗳️ <b>𝗧𝗼𝘁𝗮𝗹 𝗗𝗲𝗹𝗶𝘃𝗲𝗿𝗶𝗲𝘀 :</b> "
        f"<code>{total_deliveries}</code>\n\n"

        "🍓 <b>𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝘂𝘀 :</b> "
        "<code>ONLINE</code>"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🈲 UpDaTe 📜",
                    callback_data="owner_stats"
                )
            ],

            [
                InlineKeyboardButton(
                    "🧝🏻‍♀️ BacK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🌈 MaiN MenU",
                    callback_data="main_menu"
                )
            ]
        ])
    )    
    
# =========================================
# OWNER PENDING
# =========================================

async def owner_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    verify_orders = context.bot_data.get(
        "verify_orders",
        {}
    )

    text = ""

    if not verify_orders:

        text = (
            "❌ <b>𝗡𝗼 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗣𝗮𝘆𝗺𝗲𝗻𝘁𝘀 𝗙𝗼𝘂𝗻𝗱</b>"
        )

    else:

        for uid, order in verify_orders.items():

            text += (

                "<b>🅿🅴🅽🅳🅸🅽🅶 🅿🅰🆈🅼🅴🅽🆃🆂</b>\n\n"

                f"🥇 <b>𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :</b> "
                f"<b>@{order.get('username', 'No Username')}</b>\n\n"

                f"🙆🏻‍♂️ <b>𝗨𝗦𝗘𝗥 𝗜𝗗 :</b> "
                f"<b><code>{uid}</code></b>\n\n"

                f"🎮 <b>𝗚𝗔𝗠𝗘 :</b> "
                f"<b>{order.get('game')}</b>\n\n"

                f"💰 <b>𝗔𝗠𝗢𝗨𝗡𝗧 :</b> "
                f"<b>₹{order.get('amount')}</b>\n\n"

                f"🧾 <b>𝗢𝗥𝗗𝗘𝗥 𝗜𝗗 :</b>\n"
                f"<code>{order.get('order_id')}</code>\n\n"

                "━━━━━━━━━━━━━━━━━━\n\n"
            )

    await query.message.edit_text(
        text=text[:4000],
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🈲 UpDaTe 📜",
                    callback_data="owner_pending"
                )
            ],

            [
                InlineKeyboardButton(
                    "🧝🏻‍♀️ BacK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🌈 MaiN MenU",
                    callback_data="main_menu"
                )
            ]
        ])
    )
    
# =========================================
# OWNER VERIFIED
# =========================================

async def owner_verified(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    text = ""

    found = False

    for uid, user in data.items():

        for order in user.get("orders", []):

            found = True

            text += (

                "<b>🆅🅴🆁🅸🅵🅸🅴🅳 🅿🅰🆈🅼🅴🅽🆃🆂</b>\n\n"

                f"🥇 <b>𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :</b> "
                f"<b>@{order.get('username', 'No Username')}</b>\n\n"

                f"🙆🏻‍♂️ <b>𝗨𝗦𝗘𝗥 𝗜𝗗 :</b> "
                f"<b><code>{uid}</code></b>\n\n"

                f"🎮 <b>𝗚𝗔𝗠𝗘 :</b> "
                f"<b>{order.get('game')}</b>\n\n"

                f"💰 <b>𝗔𝗠𝗢𝗨𝗡𝗧 :</b> "
                f"<b>₹{order.get('amount')}</b>\n\n"

                f"🔑 <b>𝗞𝗘𝗬 :</b>\n"
                f"<code>{order.get('key')}</code>\n\n"

                "━━━━━━━━━━━━━━━━━━\n\n"
            )

    if not found:

        text = (
            "❌ <b>𝗡𝗼 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱 𝗣𝗮𝘆𝗺𝗲𝗻𝘁𝘀 𝗙𝗼𝘂𝗻𝗱</b>"
        )

    await query.message.edit_text(
        text=text[:4000],
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🈲 UpDaTe 🍫",
                    callback_data="owner_verified"
                )
            ],

            [
                InlineKeyboardButton(
                    "🧝🏻‍♀️ BacK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🌈 MaiN MenU",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================
# OWNER ACTIVITY
# =========================================

async def owner_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    data = load_data()

    text = ""

    if not data:

        text = (
            "❌ <b>𝗡𝗼 𝗨𝘀𝗲𝗿 𝗔𝗰𝘁𝗶𝘃𝗶𝘁𝘆 𝗙𝗼𝘂𝗻𝗱</b>"
        )

    else:

        for user_id, user_data in data.items():

            username = user_data.get("username")

            if username:
                username = f"@{username}"
            else:
                username = "No Username"

            text += (

                "🅰🅲🆃🅸🆅🅸🆃🆈 🆃🅸🅼🅴\n\n"

                f"🙆🏻‍♂️ <b>𝗡𝗮𝗺𝗘 :</b> "
                f"<b>{user_data.get('name', 'Unknown')}</b>\n"

                f"🥇 <b>𝗨𝘀𝗘𝗿𝗻𝗮𝗺𝗘 :</b> "
                f"<b>{username}</b>\n"

                f"🧾 <b>𝗨𝘀𝗘𝗿 𝗜𝗗 :</b> "
                f"<b><code>{user_id}</code></b>\n\n"

                f"📅 <b>𝗝𝗼𝗶𝗻𝗘𝗱 :</b> "
                f"<b>{user_data.get('joined', 'Unknown')}</b>\n\n"

                f"🧙🏻‍♂️ <b>𝗟-𝗦𝗲𝗲𝗡 :</b> "
                f"<b>{user_data.get('last_activity', 'Unknown')}</b>\n\n"

                f"🧝🏻‍♀️ <b>𝗥𝗲𝗖𝗲𝗻𝘁 𝗖𝗹𝗶𝗰𝗞 :</b> "
                f"<b>{user_data.get('last_button', 'None')}</b>\n\n"

                "━━━━━━━━━━━━━━━━━━\n\n"
            )

    await query.message.edit_text(
        text=text[:4000],
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "🛡️ UpDaTe 📜",
                    callback_data="owner_activity"
                )

            ],    
            
            [
                InlineKeyboardButton(
                    "🧝🏻‍♀️ BacK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🌈 MaiN MenU",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================================
# BAN USER
# =========================================

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    text = (
        "╔════════════════════╗\n"
        "   🚫 <b>BAN USER SYSTEM</b>\n"
        "╚════════════════════╝\n\n"

        "🧝🏻‍♀️ <b>REPLY COMMAND FORMAT:</b>\n\n"

        "<code>/ban USER_ID</code>\n\n"

        "<b>EXAMPLE:</b>\n"
        "<code>/ban 123456789</code>"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=owner_panel_keyboard()
    )


# =========================================
# UNBAN USER
# =========================================

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if not is_owner(query.from_user.id):
        return

    text = (
        "╔════════════════════╗\n"
        "  🧚🏻 <b>UNBAN USER SYSTEM</b>\n"
        "╚════════════════════╝\n\n"

        "🧚🏻 <b>REPLY COMMAND FORMAT:</b>\n\n"

        "<code>/unban USER_ID</code>\n\n"

        "<b>EXAMPLE:</b>\n"
        "<code>/unban 123456789</code>"
    )

    await query.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=owner_panel_keyboard()
    )

# =========================================
# CHECK BANNED USER
# =========================================

async def check_banned(update):

    user_id = update.effective_user.id

    if user_id in BANNED_USERS:

        text = (
            "╔════════════════════╗\n"
            "  🚫 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗕𝗔𝗡𝗡𝗘𝗗 🚫\n"
            "╚════════════════════╝\n\n"

            "🈲 <b>Your Access Has Been Removed</b>\n\n"

            "⚠️ <b>You Cannot Use This Bot</b>\n\n"

            "🧝🏻‍♀️ <b>Contact Owner For Unban</b>"
        )

        if update.callback_query:

            await update.callback_query.message.edit_text(
                text=text,
                parse_mode="HTML"
            )

        elif update.message:

            await update.message.reply_text(
                text=text,
                parse_mode="HTML"
            )

        return True

    return False

# =========================================
# BAN COMMAND
# =========================================

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/ban USER_ID"
        )

        return

    user_id = int(context.args[0])

    BANNED_USERS.add(user_id)

    # OWNER MESSAGE
    await update.message.reply_text(

        "╔════════════════════╗\n"
        "   🚫 𝗨𝗦𝗘𝗥 𝗕𝗔𝗡𝗡𝗘𝗗 🚫\n"
        "╚════════════════════╝\n\n"

        f"🙆🏻‍♂️ <b>USER ID :</b> <code>{user_id}</code>\n\n"

        "⚡ <b>User Successfully Banned</b>\n\n"

        "🛡️ <b>All Bot Access Removed</b>",

        parse_mode="HTML"
    )

    # SEND AUTO MESSAGE TO USER
    try:

        text = (
            "╔════════════════════╗\n"
            "  🚫 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗕𝗔𝗡𝗡𝗘𝗗 🚫\n"
            "╚════════════════════╝\n\n"

            "🈲 <b>Your Access Has Been Removed</b>\n\n"

            "⚠️ <b>You Cannot Use This Bot</b>\n\n"

            "🧝🏻‍♀️ <b>Contact Owner For Unban</b>"
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "🧝🏻‍♀️ Contact FaTheR 🈲",
                        url="http://BESTCHEAT_OWNER.t.me"
                    )
                ]
            ])
        )

    except:
        pass


# =========================================
# UNBAN COMMAND
# =========================================

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/unban USER_ID"
        )

        return

    user_id = int(context.args[0])

    BANNED_USERS.discard(user_id)

    # OWNER MESSAGE
    await update.message.reply_text(

        "╔════════════════════╗\n"
        "  🌈 𝗨𝗦𝗘𝗥 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗 🌈\n"
        "╚════════════════════╝\n\n"

        f"🙆🏻‍♂️ <b>USER ID :</b> <code>{user_id}</code>\n\n"

        "✨ <b>User Successfully Unbanned</b>\n\n"

        "⚡ <b>Bot Access Restored</b>",

        parse_mode="HTML"
    )

    # SEND AUTO MESSAGE TO USER
    try:

        text = (
            "╔════════════════════╗\n"
            " 🌈 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗 🌈\n"
            "╚════════════════════╝\n\n"

            "✨ <b>Your Access Has Been Restored</b>\n\n"

            "🧝🏻‍♀️ <b>You Can Use Bot Again</b>\n\n"

            "⚡ <b>Welcome Back Buddy</b>"
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "🌈 Go Back To Main Menu 🧚🏻",
                        callback_data="main_menu"
                    )
                ]
            ])
        )

    except:
        pass
        
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


    app.add_handler(
        CallbackQueryHandler(
            owner_panel,
            pattern="^owner_panel$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            stats_callback,
            pattern="^owner_stats$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            ban_user,
            pattern="^ban_user$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            unban_user,
            pattern="^unban_user$"
        )
    )

    app.add_handler(
        CommandHandler(
            "ban",
            ban_command
        )
    )

    app.add_handler(
        CommandHandler(
            "unban",
            unban_command
         )
    )

    app.add_handler(
        CallbackQueryHandler(
            send_message_panel,
            pattern="^send_message_panel$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_message_style,
            pattern="^msg_"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            broadcast_message
        )
    )
    
    app.add_handler(
        CallbackQueryHandler(
            owner_users,
            pattern="^owner_users$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            owner_pending,
            pattern="^owner_pending$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            owner_verified,
            pattern="^owner_verified$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            owner_activity,
            pattern="^owner_activity$"
        )
    )
    
    print("BOT STARTED SUCCESSFULLY")

    app.run_polling()

if __name__ == "__main__":
    main()
