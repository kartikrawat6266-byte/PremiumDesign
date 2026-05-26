# ===================================================
# CRAZY GAMING 100K BOT
# FULL FIXED COLOURED BUTTON VERSION
# PYROGRAM
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
    "CrazyGaming100KBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===================================================
# START TEXT
# ===================================================

START_TEXT = """
✨ WELCOME TO Crazy Gaming 100K Store ✨

👋 Hello, ◈ I’m ➤ HeaVen!

━━━━━━━━━━━━━━━━━━━━

🛍 Store: Buy premium services.
⚡ Instant Delivery !!

👤 Profile: Your Account Details.

📄 History: Track your Orders.

🎬 How to Use: How to buy Key

🛑 Help: Get Support from Owner.

━━━━━━━━━━━━━━━━━━━━
"""

# ===================================================
# COLOURED BUTTONS
# ===================================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["🛒 Shop"],

        ["👤 My Profile", "📄 History"],

        ["🎬 How To Use", "📞 Helpline"]
    ],
    resize_keyboard=True
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
# SHOP BUTTON
# ===================================================

@app.on_message(filters.regex("^🛒 Shop$"))
async def shop_handler(client, message):

    text = """
🛒 WELCOME TO SHOP

━━━━━━━━━━━━━━━━━━━━

🎮 BGMI KEYS
🔥 FREE FIRE KEYS
📺 NETFLIX PREMIUM
🎵 SPOTIFY PREMIUM

⚡ Instant Delivery Available

━━━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# PROFILE BUTTON
# ===================================================

@app.on_message(filters.regex("^👤 My Profile$"))
async def profile_handler(client, message):

    user = message.from_user

    username = user.username

    if username:
        username = f"@{username}"
    else:
        username = "No Username"

    text = f"""
👤 YOUR PROFILE

━━━━━━━━━━━━━━━━━━━━

🆔 User ID:
{user.id}

📛 Name:
{user.first_name}

🚀 Username:
{username}

━━━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# HISTORY BUTTON
# ===================================================

@app.on_message(filters.regex("^📄 History$"))
async def history_handler(client, message):

    text = """
📄 ORDER HISTORY

━━━━━━━━━━━━━━━━━━━━

❌ No Order History Found.

━━━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# HOW TO USE BUTTON
# ===================================================

@app.on_message(filters.regex("^🎬 How To Use$"))
async def howto_handler(client, message):

    text = """
🎬 HOW TO USE

━━━━━━━━━━━━━━━━━━━━

1️⃣ Open Shop Section

2️⃣ Select Product

3️⃣ Complete Payment

4️⃣ Send Screenshot

5️⃣ Receive Product Instantly 🚀

━━━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# HELPLINE BUTTON
# ===================================================

@app.on_message(filters.regex("^📞 Helpline$"))
async def help_handler(client, message):

    text = f"""
📞 SUPPORT CENTER

━━━━━━━━━━━━━━━━━━━━

👨‍💻 Owner:
@{OWNER_USERNAME}

⚡ Fast Reply Available

━━━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(
        text,
        reply_markup=main_keyboard
    )

# ===================================================
# UNKNOWN MESSAGE
# ===================================================

@app.on_message(filters.text & ~filters.command("start"))
async def unknown_handler(client, message):

    await message.reply_text(
        "👇 Please use buttons below",
        reply_markup=main_keyboard
    )

# ===================================================
# BOT START
# ===================================================

print("🚀 Crazy Gaming 100K Bot Started Successfully")

app.run()
