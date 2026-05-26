# ===================================================
# PREMIUM TELEGRAM STORE BOT
# FULL FIXED VERSION
# RAILWAY READY
# ===================================================

import os

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===================================================
# VARIABLES FROM RAILWAY
# ===================================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = os.getenv("OWNER_USERNAME")

# ===================================================
# BOT CLIENT
# ===================================================

app = Client(
    "PremiumStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===================================================
# START TEXT
# ===================================================

START_TEXT = """
✨ <b>WELCOME TO Crazy Gaming 100K Store</b> ✨

👋 Hello, ◈ I’m ➤ <b>HeaVen!</b>

━━━━━━━━━━━━━━━━━━━

🛍 <b>Store:</b> Buy premium services.
⚡ Instant Delivery !!

👤 <b>Profile:</b> Your Account Details.

📄 <b>History:</b> Track your Orders.

🎬 <b>How to Use:</b> Learn how to buy keys.

🛑 <b>Help:</b> Get Support from Owner.

━━━━━━━━━━━━━━━━━━━
"""

# ===================================================
# MAIN BUTTONS
# ===================================================

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

# ===================================================
# BACK BUTTON
# ===================================================

BACK_BUTTON = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "🔙 Back To Main Menu",
                callback_data="back"
            )
        ]
    ]
)

# ===================================================
# START COMMAND
# ===================================================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    await message.reply_text(
        text=START_TEXT,
        reply_markup=START_BUTTONS,
        parse_mode=enums.ParseMode.HTML
    )

# ===================================================
# CALLBACK SYSTEM
# ===================================================

@app.on_callback_query()
async def callback_handler(client, query):

    data = query.data

    await query.answer()

    # ===================================================
    # SHOP
    # ===================================================

    if data == "shop":

        SHOP_TEXT = """
🛒 <b>WELCOME TO SHOP</b>

━━━━━━━━━━━━━━━━━━━

🎮 Premium Gaming Keys
📺 OTT Accounts
🎵 Music Premium
🎬 Streaming Services
💎 Instant Delivery

━━━━━━━━━━━━━━━━━━━
"""

        SHOP_BUTTONS = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎮 Buy Keys",
                        callback_data="buy_keys"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💳 Payment",
                        callback_data="payment"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="back"
                    )
                ]
            ]
        )

        await query.message.edit_text(
            text=SHOP_TEXT,
            reply_markup=SHOP_BUTTONS,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # PROFILE
    # ===================================================

    elif data == "profile":

        username = query.from_user.username

        if username:
            username = f"@{username}"
        else:
            username = "No Username"

        PROFILE_TEXT = f"""
👤 <b>YOUR PROFILE</b>

━━━━━━━━━━━━━━━━━━━

🆔 User ID:
<code>{query.from_user.id}</code>

📛 Name:
{query.from_user.first_name}

🚀 Username:
{username}

━━━━━━━━━━━━━━━━━━━
"""

        await query.message.edit_text(
            text=PROFILE_TEXT,
            reply_markup=BACK_BUTTON,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # HISTORY
    # ===================================================

    elif data == "history":

        HISTORY_TEXT = """
📄 <b>ORDER HISTORY</b>

━━━━━━━━━━━━━━━━━━━

❌ No Orders Found Yet.

━━━━━━━━━━━━━━━━━━━
"""

        await query.message.edit_text(
            text=HISTORY_TEXT,
            reply_markup=BACK_BUTTON,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # HOW TO USE
    # ===================================================

    elif data == "howto":

        HOW_TEXT = """
🎬 <b>HOW TO USE</b>

━━━━━━━━━━━━━━━━━━━

1️⃣ Open Shop Section

2️⃣ Select Product

3️⃣ Complete Payment

4️⃣ Send Screenshot

5️⃣ Receive Product Instantly 🚀

━━━━━━━━━━━━━━━━━━━
"""

        await query.message.edit_text(
            text=HOW_TEXT,
            reply_markup=BACK_BUTTON,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # HELP
    # ===================================================

    elif data == "help":

        HELP_TEXT = f"""
📞 <b>SUPPORT CENTER</b>

━━━━━━━━━━━━━━━━━━━

👨‍💻 Owner Support:
@{OWNER_USERNAME}

⚡ Fast Reply Available

━━━━━━━━━━━━━━━━━━━
"""

        HELP_BUTTONS = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📞 Contact Owner",
                        url=f"https://t.me/{OWNER_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="back"
                    )
                ]
            ]
        )

        await query.message.edit_text(
            text=HELP_TEXT,
            reply_markup=HELP_BUTTONS,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # BUY KEYS
    # ===================================================

    elif data == "buy_keys":

        BUY_TEXT = """
🎮 <b>BUY GAMING KEYS</b>

━━━━━━━━━━━━━━━━━━━

🔥 BGMI Key
🔥 Free Fire Key
🔥 Netflix Premium
🔥 Spotify Premium

⚡ Instant Delivery Available

━━━━━━━━━━━━━━━━━━━
"""

        BUY_BUTTONS = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💳 Buy Now",
                        callback_data="payment"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="shop"
                    )
                ]
            ]
        )

        await query.message.edit_text(
            text=BUY_TEXT,
            reply_markup=BUY_BUTTONS,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # PAYMENT
    # ===================================================

    elif data == "payment":

        PAYMENT_TEXT = """
💳 <b>PAYMENT SECTION</b>

━━━━━━━━━━━━━━━━━━━

🏦 UPI ID:
<code>yourupi@upi</code>

📸 Send Payment Screenshot
To Owner After Payment.

⚡ Instant Verification

━━━━━━━━━━━━━━━━━━━
"""

        PAYMENT_BUTTONS = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📞 Send Screenshot",
                        url=f"https://t.me/{OWNER_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="shop"
                    )
                ]
            ]
        )

        await query.message.edit_text(
            text=PAYMENT_TEXT,
            reply_markup=PAYMENT_BUTTONS,
            parse_mode=enums.ParseMode.HTML
        )

    # ===================================================
    # BACK
    # ===================================================

    elif data == "back":

        await query.message.edit_text(
            text=START_TEXT,
            reply_markup=START_BUTTONS,
            parse_mode=enums.ParseMode.HTML
        )

# ===================================================
# BOT START
# ===================================================

print("🚀 Premium Store Bot Started Successfully")

app.run()
