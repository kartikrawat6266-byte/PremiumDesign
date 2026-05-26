# ===================================================
# REAL COLOURED BUTTON TELEGRAM BOT
# EXACT GREEN BUTTON STYLE
# PYROGRAM WORKING VERSION
# ===================================================

import os

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup

# ===================================================
# VARIABLES
# ===================================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = os.getenv("OWNER_USERNAME")

# ===================================================
# BOT CLIENT
# ===================================================

app = Client(
    "ColourStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===================================================
# START MESSAGE
# ===================================================

START_TEXT = """
🛒 Shop Now : all key purchase & instantly delivery

📦 My Orders : check all key purchase history

👤 Profile : check your account information

📖 How to Use : view tutorial and work this bot

💬 Support : bot problem fixed for support admin

😉 Refer & Earn : invite friends & earn rewards
"""

# ===================================================
# REAL COLOUR BUTTON KEYBOARD
# ===================================================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["🛒 Shop Now"],

        ["📦 My Orders", "👤 Profile"],

        ["📖 How to Use", "💬 Support"],

        ["😉 Refer & Earn"]
    ],

    resize_keyboard=True,
    is_persistent=True,
    one_time_keyboard=False,
    selective=False
)

# ===================================================
# START COMMAND
# ===================================================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    await message.reply_text(
        START_TEXT,
        reply_markup=main_keyboard
    )

# ===================================================
# SHOP NOW
# ===================================================

@app.on_message(filters.regex("^🛒 Shop Now$"))
async def shop_handler(client, message):

    text = """
🛒 SHOP SECTION

━━━━━━━━━━━━━━━━━━

🎮 BGMI KEYS
🔥 FREE FIRE KEYS
📺 NETFLIX PREMIUM
🎵 SPOTIFY PREMIUM

⚡ Instant Delivery Available

━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# ORDERS
# ===================================================

@app.on_message(filters.regex("^📦 My Orders$"))
async def order_handler(client, message):

    text = """
📦 MY ORDERS

━━━━━━━━━━━━━━━━━━

❌ No Orders Found

━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# PROFILE
# ===================================================

@app.on_message(filters.regex("^👤 Profile$"))
async def profile_handler(client, message):

    user = message.from_user

    username = user.username

    if username:
        username = f"@{username}"
    else:
        username = "No Username"

    text = f"""
👤 PROFILE

━━━━━━━━━━━━━━━━━━

🆔 ID : {user.id}

📛 Name : {user.first_name}

🚀 Username : {username}

━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# HOW TO USE
# ===================================================

@app.on_message(filters.regex("^📖 How to Use$"))
async def how_handler(client, message):

    text = """
📖 HOW TO USE

━━━━━━━━━━━━━━━━━━

1️⃣ Open Shop

2️⃣ Select Product

3️⃣ Complete Payment

4️⃣ Send Screenshot

5️⃣ Receive Product 🚀

━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# SUPPORT
# ===================================================

@app.on_message(filters.regex("^💬 Support$"))
async def support_handler(client, message):

    text = f"""
💬 SUPPORT CENTER

━━━━━━━━━━━━━━━━━━

👨‍💻 Owner :
@{OWNER_USERNAME}

⚡ Fast Reply Available

━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# REFER
# ===================================================

@app.on_message(filters.regex("^😉 Refer & Earn$"))
async def refer_handler(client, message):

    text = """
😉 REFER & EARN

━━━━━━━━━━━━━━━━━━

👥 Invite Friends

💰 Earn Rewards

🚀 Coming Soon

━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# UNKNOWN
# ===================================================

@app.on_message(filters.text & ~filters.command("start"))
async def unknown_handler(client, message):

    await message.reply_text(
        "👇 Please use buttons below",
        reply_markup=main_keyboard
    )

# ===================================================
# START BOT
# ===================================================

print("🚀 Colour Button Bot Started Successfully")

app.run()
