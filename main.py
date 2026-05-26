from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 123456
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

app = Client(
    "CrazyGamingBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# START MESSAGE
# =========================

START_TEXT = """
✨ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 SHAHID Gaming 100K Store ✨

👋 Hello, ◈ I’m ➤ HeaVen!

━━━━━━━━━━━━━━━━━━━

🛍 Store: Buy premium services.
Instant Delivery !!

👤 Profile: Your Account Details.

📄 History: Track your Orders.

🎬 How to Use: How to buy Key

🛑 Help: Get Support from Owner.

━━━━━━━━━━━━━━━━━━━
"""

# =========================
# BUTTONS
# =========================

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "🛒 Shop",
                callback_data="shop"
            )
        ],
        [
            InlineKeyboardButton(
                "👤 My Profile",
                callback_data="profile"
            ),
            InlineKeyboardButton(
                "📄 History",
                callback_data="history"
            )
        ],
        [
            InlineKeyboardButton(
                "🎬 How To Use",
                callback_data="howto"
            ),
            InlineKeyboardButton(
                "📞 Helpline",
                callback_data="help"
            )
        ]
    ]
)

# =========================
# START COMMAND
# =========================

@app.on_message(filters.command("start"))
async def start_cmd(client, message):

    await message.reply_text(
        text=START_TEXT,
        reply_markup=START_BUTTONS
    )

# =========================
# CALLBACK BUTTONS
# =========================

@app.on_callback_query()
async def callbacks(client, query):

    data = query.data

    if data == "shop":
        await query.message.edit_text(
            "🛒 Welcome To Shop Section"
        )

    elif data == "profile":
        await query.message.edit_text(
            f"""
👤 YOUR PROFILE

🆔 User ID: `{query.from_user.id}`
📛 Name: {query.from_user.first_name}
"""
        )

    elif data == "history":
        await query.message.edit_text(
            "📄 No Order History Found."
        )

    elif data == "howto":
        await query.message.edit_text(
            """
🎬 HOW TO USE

1. Open Shop
2. Select Product
3. Complete Payment
4. Receive Key Instantly
5. Enjoy Service 🚀
"""
        )

    elif data == "help":
        await query.message.edit_text(
            "📞 Contact Owner: @YourUsername"
        )

# =========================
# RUN BOT
# =========================

print("Bot Started Successfully 🚀")

app.run()
