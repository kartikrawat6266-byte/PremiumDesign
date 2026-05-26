import os
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 123456
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 123456789

app = Client(
    "shopbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

DATA_FILE = "users.json"

# ---------------- SAVE / LOAD ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


users = load_data()

# ---------------- PRODUCTS ----------------
products = {
    "drip_nonroot": {
        "name": "DRIPCLIENT NONROOT FF",
        "prices": {
            "1 Day": 90,
            "3 Days": 169,
            "7 Days": 325,
            "15 Days": 560,
            "30 Days": 788
        }
    },

    "prime_hook": {
        "name": "PRIME HOOK FF NONROOT",
        "prices": {
            "1 Day": 99,
            "3 Days": 199,
            "7 Days": 349,
            "15 Days": 599,
            "30 Days": 899
        }
    }
}

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "name": message.from_user.first_name,
            "orders": []
        }
        save_data(users)

    buttons = [
        [InlineKeyboardButton("🛒 Shop", callback_data="shop")],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="profile"),
            InlineKeyboardButton("📄 History", callback_data="history")
        ],
        [
            InlineKeyboardButton("🎬 How To Use", url="https://youtube.com"),
            InlineKeyboardButton("📞 Helpline", url="https://t.me/yourusername")
        ]
    ]

    await message.reply_photo(
        photo="https://i.imgur.com/8KHKhxS.jpeg",
        caption="🔥 Welcome To Premium Shop Bot",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- SHOP ----------------
@app.on_callback_query(filters.regex("shop"))
async def shop_menu(client, callback_query):
    buttons = []

    for key, product in products.items():
        buttons.append([
            InlineKeyboardButton(product['name'], callback_data=f"product_{key}")
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data="back_home")
    ])

    await callback_query.message.edit_text(
        "📦 Select Product",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- PRODUCT ----------------
@app.on_callback_query(filters.regex("product_"))
async def product_page(client, callback_query):
    key = callback_query.data.split("product_")[1]
    product = products[key]

text = """🔥 Features:

• NON ROOT
• ESP
• AIM ASSIST
• HIGH DAMAGE

⚠️ Status:
🟢 SAFE
"""

buttons = []
    for plan, price in product['prices'].items():
        buttons.append([
            InlineKeyboardButton(
                f"₹{price} • {plan}",
                callback_data=f"buy_{key}_{plan}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("🎬 Watch Gameplay", url="https://youtube.com")
    ])

    buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data="shop")
    ])

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- BUY ----------------
@app.on_callback_query(filters.regex("buy_"))
async def buy_product(client, callback_query):
    data = callback_query.data.split("_")

    product_key = data[1]
    plan = data[2]

    product = products[product_key]
    price = product['prices'][plan]

    user_id = str(callback_query.from_user.id)

    order = {
        "product": product['name'],
        "plan": plan,
        "price": price,
        "status": "Pending",
        "date": str(datetime.now())
    }

    users[user_id]['orders'].append(order)
    save_data(users)

    await callback_query.message.edit_text(
        f"✅ ORDER CREATED

"
        f"📦 Product: {product['name']}
"
        f"⏳ Plan: {plan}
"
        f"💸 Price: ₹{price}

"
        f"📞 Contact Admin For Payment"
    )

    await app.send_message(
        OWNER_ID,
        f"🛒 NEW ORDER

"
        f"👤 User: {callback_query.from_user.first_name}
"
        f"🆔 ID: {user_id}
"
        f"📦 Product: {product['name']}
"
        f"💰 Price: ₹{price}
"
        f"📅 Plan: {plan}"
    )

# ---------------- PROFILE ----------------
@app.on_callback_query(filters.regex("profile"))
async def profile(client, callback_query):
    user_id = str(callback_query.from_user.id)
    user = users[user_id]

    total_orders = len(user['orders'])

    text = f"📄 ACCOUNT INFORMATION

"
    text += f"👤 Name : {user['name']}
"
    text += f"🆔 UserID : {user_id}

"
    text += f"📊 STATISTICS

"
    text += f"📦 Total Orders : {total_orders}
"

    await callback_query.message.edit_text(text)

# ---------------- HISTORY ----------------
@app.on_callback_query(filters.regex("history"))
async def history(client, callback_query):
    user_id = str(callback_query.from_user.id)
    user = users[user_id]

    if not user['orders']:
        return await callback_query.answer("No Orders Found", show_alert=True)

    text = "📄 ORDER HISTORY

"

    for order in user['orders']:
        text += (
            f"📦 {order['product']}
"
            f"💰 ₹{order['price']}
"
            f"📅 {order['plan']}
"
            f"📌 {order['status']}

"
        )

    await callback_query.message.edit_text(text)

# ---------------- BACK ----------------
@app.on_callback_query(filters.regex("back_home"))
async def back_home(client, callback_query):
    buttons = [
        [InlineKeyboardButton("🛒 Shop", callback_data="shop")],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="profile"),
            InlineKeyboardButton("📄 History", callback_data="history")
        ]
    ]

    await callback_query.message.edit_text(
        "🔥 Welcome Back",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- OWNER PRICE EDIT ----------------
@app.on_message(filters.command("setprice") & filters.user(OWNER_ID))
async def set_price(client, message):
    try:
        _, product_key, days, price = message.text.split()

        if product_key not in products:
            return await message.reply("❌ Product Not Found")

        products[product_key]['prices'][days] = int(price)

        await message.reply(
            f"✅ Price Updated

"
            f"📦 Product: {product_key}
"
            f"📅 Plan: {days}
"
            f"💸 New Price: ₹{price}"
        )

    except:
        await message.reply(
            "Usage:
/setprice drip_nonroot 7_Days 499"
        )

# ---------------- RUN ----------------
print("Bot Started...")
app.run()
