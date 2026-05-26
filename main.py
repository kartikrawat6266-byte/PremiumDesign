import os
import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "users.json"

PRODUCTS = {
    "DRIPCLIENT NONROOT FF": {
        "features": [
            "NON ROOT",
            "ESP",
            "AIM ASSIST",
            "HIGH DAMAGE"
        ],
        "status": "SAFE",
        "prices": {
            "1 Day": 90,
            "3 Days": 169,
            "7 Days": 325,
            "15 Days": 560,
            "30 Days": 788
        }
    },

    "HG CHEATS FF NONROOT+ROOT": {
        "features": [
            "ROOT",
            "NON ROOT",
            "AIMBOT",
            "ESP"
        ],
        "status": "SAFE",
        "prices": {
            "1 Day": 120,
            "7 Days": 450,
            "30 Days": 999
        }
    }
}


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


users = load_users()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if str(user.id) not in users:
        users[str(user.id)] = {
            "name": user.first_name,
            "orders": 0,
            "spent": 0
        }
        save_users(users)

    keyboard = [
        ["🛒 Shop"],
        ["👤 My Profile", "📄 History"],
        ["🎬 How To Use", "📞 Helpline"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    text = f"""
🔥 Welcome {user.first_name}

✅ Premium Shop Bot Online
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []

    for product_name in PRODUCTS.keys():
        buttons.append([
            InlineKeyboardButton(
                product_name,
                callback_data=f"product|{product_name}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "⬅ Back",
            callback_data="back"
        )
    ])

    await update.message.reply_text(
        "📦 Select Product",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = users.get(str(user.id), {})

    text = f"""
📄 ACCOUNT INFORMATION

👤 Name : {user.first_name}
🆔 UserID : {user.id}

📊 STATISTICS

📦 Total Orders : {data.get("orders", 0)}
💰 Total Spent : ₹{data.get("spent", 0)}
"""

    await update.message.reply_text(text)


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📄 No Order History Found"
    )


async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Buy Product → Payment → Receive Access"
    )


async def helpline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Contact Admin"
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back":
        return

    if data.startswith("product|"):
        product_name = data.split("|")[1]

        product = PRODUCTS[product_name]

        features = "\n".join(
            [f"• {x}" for x in product["features"]]
        )

        text = f"""🔥 Features:

{features}

⚠ Status:
🟢 {product["status"]}
"""

        buttons = []

        for plan, price in product["prices"].items():
            buttons.append([
                InlineKeyboardButton(
                    f"₹{price} • {plan}",
                    callback_data=f"buy|{product_name}|{plan}"
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                "🎬 Watch Gameplay",
                url="https://youtube.com"
            )
        ])

        buttons.append([
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="back"
            )
        ])

        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data.startswith("buy|"):
        split_data = data.split("|")

        product_name = split_data[1]
        plan = split_data[2]

        price = PRODUCTS[product_name]["prices"][plan]

        text = f"""
✅ ORDER CREATED

📦 Product : {product_name}
⏳ Plan : {plan}
💰 Price : ₹{price}

📞 Contact Admin For Payment
"""

        await query.message.reply_text(text)


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛒 Shop":
        await shop(update, context)

    elif text == "👤 My Profile":
        await profile(update, context)

    elif text == "📄 History":
        await history(update, context)

    elif text == "🎬 How To Use":
        await help_menu(update, context)

    elif text == "📞 Helpline":
        await helpline(update, context)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            messages
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_click)
    )

    print("Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
