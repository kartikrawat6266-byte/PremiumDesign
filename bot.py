import os
import json
import logging
import random
import string
from datetime import datetime, timezone, timedelta

from telegram import Update, BotCommand, BotCommandScopeDefault
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIGURATION ====================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found")

UPI_ID = os.environ.get("UPI_ID", "example@okhdfcbank")

# Indian Timezone
IST = timezone(timedelta(hours=5, minutes=30))

def get_current_ist():
    return datetime.now(IST).strftime("%d/%m/%Y, %I:%M:%S %p")

def get_joined_date():
    return datetime.now(IST).strftime("%d/%m/%Y, %I:%M:%S %p")

# Products
PRODUCTS = {
    "1 Day Premium Key": 80.00,
    "1 Month Premium Key": 99.00,
    "1 Year Premium Key": 499.00,
    "Lifetime Premium Key": 999.00,
}

FREE_KEY_REFERRALS_NEEDED = 80
FREE_KEY_PRODUCT = "1 Day Premium Key"

DB_FILE = "user_data.json"

# ==================== DATABASE FUNCTIONS ====================
def load_user_data():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def get_user(user_id):
    data = load_user_data()
    if user_id not in data:
        data[user_id] = {
            "name": "",
            "username": "",
            "total_orders": 0,
            "referral_earnings": 0.0,
            "referral_history": [],
            "total_refers": 0,
            "referred_users": [],
            "free_key_claimed": False,
            "referred_by": None,
            "joined": get_joined_date(),
            "last_activity": get_current_ist(),
            "orders": [],
            "pending_payment": None,
        }
        save_user_data(data)
    return data[user_id]

def update_user(user_id, update_data):
    data = load_user_data()
    if user_id not in data:
        data[user_id] = get_user(user_id)
    data[user_id].update(update_data)
    data[user_id]["last_activity"] = get_current_ist()
    save_user_data(data)

def update_last_activity(user_id):
    data = load_user_data()
    if user_id in data:
        data[user_id]["last_activity"] = get_current_ist()
        save_user_data(data)

def add_referral(referrer_id, new_user_id, new_username):
    referrer_data = get_user(referrer_id)
    referred_users = referrer_data.get("referred_users", [])
    
    if new_user_id in referred_users:
        return False
    
    referred_users.append(new_user_id)
    new_refers_count = len(referred_users)
    new_earnings = new_refers_count * 1.0
    
    referral_history = referrer_data.get("referral_history", [])
    referral_history.append({
        "user_id": new_user_id,
        "username": new_username,
        "date": get_current_ist(),
        "earned": 1.0
    })
    
    update_user(referrer_id, {
        "total_refers": new_refers_count,
        "referral_earnings": new_earnings,
        "referred_users": referred_users,
        "referral_history": referral_history
    })
    return True

def check_and_grant_free_key(user_id):
    user_data = get_user(user_id)
    total_refers = user_data.get("total_refers", 0)
    free_key_claimed = user_data.get("free_key_claimed", False)
    
    if total_refers >= FREE_KEY_REFERRALS_NEEDED and not free_key_claimed:
        license_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        
        new_order = {
            "product": f"🎁 FREE {FREE_KEY_PRODUCT} (Referral Reward)",
            "amount": 0.00,
            "date": get_current_ist(),
            "key": license_key,
            "upi_name": "REFERRAL_REWARD",
            "is_free": True
        }
        orders = user_data.get("orders", [])
        orders.append(new_order)
        
        update_user(user_id, {
            "total_orders": user_data.get("total_orders", 0) + 1,
            "orders": orders,
            "free_key_claimed": True
        })
        return True, license_key
    return False, None

# ==================== KEYBOARD BUILDERS ====================
# VERTICAL LIST - EK KE NECHE EK
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛍️ Shop Now", callback_data="shop_now")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("📖 How to Use", callback_data="how_to_use")],
        [InlineKeyboardButton("🆘 Support", callback_data="support")],
        [InlineKeyboardButton("💰 Refer & Earn", callback_data="refer_earn")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_button():
    return main_menu_keyboard()

def product_list_keyboard():
    keyboard = []
    for name, price in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(f"{name} - ₹{price:.2f}", callback_data=f"product_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def payment_keyboard(product_name, amount):
    upi_link = f"upi://pay?pa={UPI_ID}&pn=Satyam%20X%20Store&am={amount}&cu=INR"
    keyboard = [
        [InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{product_name}")],
        [InlineKeyboardButton("💳 Copy UPI ID", callback_data="copy_upi")],
        [InlineKeyboardButton("📱 Open UPI App", url=upi_link)],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_contact_keyboard():
    keyboard = [
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/SATYAM_X_OFC")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def refer_earn_keyboard(referral_link, total_refers, free_available):
    keyboard = []
    if total_refers >= FREE_KEY_REFERRALS_NEEDED and free_available:
        keyboard.append([InlineKeyboardButton("🎁 CLAIM YOUR FREE KEY 🎁", callback_data="claim_free_key")])
    keyboard.append([InlineKeyboardButton("📤 Share with Friend", url=f"https://t.me/share/url?url={referral_link}&text=🔥 Join Satyam X Ofc Store and get premium keys! Use my referral link:")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Referral logic
    if context.args and context.args[0].startswith("ref_"):
        referrer_id = context.args[0][4:]
        if referrer_id != user_id:
            referrer_data = get_user(referrer_id)
            user_data = get_user(user_id)
            if referrer_data and not user_data.get("referred_by"):
                username = f"@{user.username}" if user.username else user.full_name
                referral_added = add_referral(referrer_id, user_id, username)
                if referral_added:
                    update_user(user_id, {"referred_by": referrer_id})
                    updated_referrer = get_user(referrer_id)
                    await context.bot.send_message(
                        chat_id=int(referrer_id),
                        text=f"🎉 *New Referral!* 🎉\n\n{username} joined!\n\n📊 *Total Refers:* {updated_referrer.get('total_refers', 0)}\n💰 *Earnings:* ₹{updated_referrer.get('referral_earnings', 0):.2f}",
                        parse_mode="Markdown"
                    )
                    qualified, key = check_and_grant_free_key(referrer_id)
                    if qualified:
                        await context.bot.send_message(
                            chat_id=int(referrer_id),
                            text=f"🎉 *CONGRATULATIONS!* 🎉\n\nFREE {FREE_KEY_PRODUCT}!\n🔑 `{key}`",
                            parse_mode="Markdown"
                        )
                    await update.message.reply_text(
                        "🎉 Welcome! You were referred by a friend!\n\nUse the buttons below.",
                        reply_markup=main_menu_keyboard()
                    )
                    return
    
    user_data = get_user(user_id)
    if not user_data["name"]:
        update_user(user_id, {
            "name": user.full_name or "User",
            "username": user.username or ""
        })
    
    update_last_activity(user_id)
    
    welcome_text = (
        f"👋 Welcome to *Satyam X Ofc Store*!\n\n"
        f"Trusted selling bot – anyone can purchase from this bot.\n"
        f"⭐ *SUPER FAST DELIVERY*\n\n"
        f"📌 Use the buttons below to start shopping."
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    await query.edit_message_text(
        "🏠 *Main Menu*\n\nChoose an option:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    await query.edit_message_text(
        "🛍️ *Our Products*\n\nSelect a product to purchase:",
        reply_markup=product_list_keyboard(),
        parse_mode="Markdown"
    )

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    product_name = query.data.replace("product_", "")
    price = PRODUCTS.get(product_name)
    if not price:
        await query.edit_message_text("❌ Product not found.", reply_markup=back_to_menu_button())
        return
    
    update_user(user_id, {"pending_payment": product_name})
    
    payment_text = (
        f"💸 *Payment Required*\n\n"
        f"Product: {product_name}\n"
        f"Amount: ₹{price:.2f}\n\n"
        f"*How to Pay:*\n"
        f"1️⃣ Tap '✅ I Have Paid'\n"
        f"2️⃣ Enter UPI registered name\n\n"
        f"💳 *UPI ID:* `{UPI_ID}`\n"
        f"⚠️ Pay exact amount!"
    )
    await query.edit_message_text(payment_text, reply_markup=payment_keyboard(product_name, price), parse_mode="Markdown")

async def paid_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    product_name = query.data.replace("paid_", "")
    context.user_data["pending_product"] = product_name
    await query.edit_message_text(
        "✅ Enter your UPI registered name:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="shop_now")]])
    )

async def handle_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    product_name = context.user_data.get("pending_product")
    
    if not product_name:
        await update.message.reply_text("❌ No pending payment.", reply_markup=back_to_menu_button())
        return
    
    license_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    price = PRODUCTS.get(product_name, 0)
    
    user_data = get_user(user_id)
    orders = user_data.get("orders", [])
    orders.append({
        "product": product_name, "amount": price,
        "date": get_current_ist(), "key": license_key, "upi_name": user_name
    })
    update_user(user_id, {"total_orders": user_data.get("total_orders", 0) + 1, "orders": orders, "pending_payment": None})
    context.user_data["pending_product"] = None
    
    await update.message.reply_text(
        f"🎉 *Payment Confirmed!*\n\n📦 {product_name}\n🔑 `{license_key}`\n\n⭐ SUPER FAST DELIVERY",
        parse_mode="Markdown", reply_markup=main_menu_keyboard()
    )

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    user_data = get_user(user_id)
    orders = user_data.get("orders", [])
    
    if not orders:
        await query.edit_message_text(
            "📭 *No orders yet!*\n\nStart shopping to see your orders here.",
            reply_markup=back_to_menu_button(),
            parse_mode="Markdown"
        )
        return
    
    text = "*📦 Your Orders*\n\n"
    for i, o in enumerate(reversed(orders[-10:]), 1):
        amt = f"₹{o['amount']:.2f}" if o['amount'] > 0 else "🎁 FREE"
        text += f"{i}. *{o['product']}*\n   Amount: {amt}\n   Date: {o['date']}\n   Key: `{o['key']}`\n\n"
    await query.edit_message_text(text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    u = get_user(user_id)
    
    username = u.get('username', '')
    username_display = f"@{username}" if username else "Not set"
    
    referral_history = u.get("referral_history", [])
    referral_text = ""
    if referral_history:
        referral_text = "\n\n📜 *Referral History:*"
        for ref in referral_history[-5:]:
            referral_text += f"\n   • {ref.get('username', 'Unknown')} - ₹{ref.get('earned', 0):.2f} ({ref.get('date', '')})"
    
    text = (
        f"❄️ *User Account Information*\n\n"
        f"• Name : {u.get('name', 'N/A')}\n"
        f"• Username : {username_display}\n"
        f"• User Id : `{user_id}`\n\n"
        f"• Total Orders : {u.get('total_orders', 0)}\n"
        f"• Referral Earnings : ₹{u.get('referral_earnings', 0):.2f}{referral_text}\n\n"
        f"• Joined : {u.get('joined', get_joined_date())}\n"
        f"⭐ Last Activity : {u.get('last_activity', get_current_ist())}"
    )
    
    await query.edit_message_text(text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    text = (
        "*📖 How to Buy — SATYAM X MOD STORE*\n\n"
        "1. Tap Shop Now\n"
        "2. Pick your product & plan\n"
        "3. Scan the UPI QR or copy UPI ID\n"
        "4. Pay the exact amount shown (with paisa!)\n"
        "5. Tap ✅ I Have Paid\n"
        "6. Enter your UPI registered name\n"
        "7. Sit back – your key arrives in seconds!\n\n"
        "⚠️ Always pay the exact amount including paisa!"
    )
    await query.edit_message_text(text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    text = (
        "*🆘 OFFICIAL SUPPORT CENTER*\n\n"
        "If you face any issues or have questions regarding our services, feel free to contact our expert team.\n\n"
        "📅 Active Time: 9 AM - 11 PM\n"
        "⏱️ Response: Within 5-10 Minutes\n\n"
        "Click the button below to start a chat:"
    )
    await query.edit_message_text(text, reply_markup=admin_contact_keyboard(), parse_mode="Markdown")

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    u = get_user(user_id)
    total = u.get("total_refers", 0)
    earnings = u.get("referral_earnings", 0.0)
    claimed = u.get("free_key_claimed", False)
    remaining = max(0, FREE_KEY_REFERRALS_NEEDED - total)
    
    text = f"""*💰 Referral Program*

Invite your friends and earn real balance for every successful joining.

• *Total Refers:* {total} User(s)
• *Invite Reward:* ₹{earnings:.2f} (₹1 per refer)

"""
    if not claimed:
        if remaining > 0:
            text += f"🎯 *Refer {remaining} more to get a FREE {FREE_KEY_PRODUCT}!*\n\n"
        else:
            text += f"🎉 *You've earned a FREE {FREE_KEY_PRODUCT}!*\n\n"
    else:
        text += f"✅ *You have claimed your FREE key!*\n\n"
    
    text += f"""*Your Invite Link:*
`{referral_link}`

Share your link to grow your earnings!"""
    
    await query.edit_message_text(text, reply_markup=refer_earn_keyboard(referral_link, total, not claimed), parse_mode="Markdown")

async def claim_free_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    
    qualified, key = check_and_grant_free_key(user_id)
    if qualified:
        await query.edit_message_text(
            f"🎉 *FREE KEY CLAIMED!* 🎉\n\n🔑 `{key}`\n📦 {FREE_KEY_PRODUCT}",
            parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )
    else:
        u = get_user(user_id)
        total = u.get("total_refers", 0)
        remaining = FREE_KEY_REFERRALS_NEEDED - total
        await query.edit_message_text(
            f"❌ Need {remaining} more referrals for FREE key!",
            reply_markup=back_to_menu_button()
        )

async def copy_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("UPI ID copied!", show_alert=True)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("❌ Please use menu buttons.", reply_markup=main_menu_keyboard())

# ==================== SET BOT MENU BUTTONS (BOTTOM NAVIGATION) ====================
async def set_bot_commands(app: Application):
    """Set bot menu buttons that appear at bottom (where typing happens)"""
    commands = [
        BotCommand("shop", "🛍️ Browse products & purchase"),
        BotCommand("orders", "📦 View your order history"),
        BotCommand("profile", "👤 Check your account info"),
        BotCommand("howtouse", "📖 How to buy guide"),
        BotCommand("support", "🆘 Contact support"),
        BotCommand("refer", "💰 Refer & earn rewards"),
        BotCommand("start", "🏠 Back to main menu"),
    ]
    await app.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("Bot menu buttons set successfully!")

# ==================== COMMAND HANDLERS FOR BOTTOM BUTTONS ====================
async def cmd_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await shop_now_callback(update, context)

async def cmd_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    user_data = get_user(user_id)
    orders = user_data.get("orders", [])
    
    if not orders:
        await update.message.reply_text(
            "📭 *No orders yet!*\n\nStart shopping to see your orders here.",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    text = "*📦 Your Orders*\n\n"
    for i, o in enumerate(reversed(orders[-10:]), 1):
        amt = f"₹{o['amount']:.2f}" if o['amount'] > 0 else "🎁 FREE"
        text += f"{i}. *{o['product']}*\n   Amount: {amt}\n   Date: {o['date']}\n   Key: `{o['key']}`\n\n"
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    u = get_user(user_id)
    
    username = u.get('username', '')
    username_display = f"@{username}" if username else "Not set"
    
    text = (
        f"❄️ *User Account Information*\n\n"
        f"• Name : {u.get('name', 'N/A')}\n"
        f"• Username : {username_display}\n"
        f"• User Id : `{user_id}`\n\n"
        f"• Total Orders : {u.get('total_orders', 0)}\n"
        f"• Referral Earnings : ₹{u.get('referral_earnings', 0):.2f}\n\n"
        f"• Joined : {u.get('joined', get_joined_date())}\n"
        f"⭐ Last Activity : {u.get('last_activity', get_current_ist())}"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def cmd_howtouse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    text = (
        "*📖 How to Buy — SATYAM X MOD STORE*\n\n"
        "1️⃣ Tap Shop Now\n"
        "2️⃣ Pick your product & plan\n"
        "3️⃣ Scan the UPI QR or copy UPI ID\n"
        "4️⃣ Pay the exact amount shown (with paisa!)\n"
        "5️⃣ Tap ✅ I Have Paid\n"
        "6️⃣ Enter your UPI registered name\n"
        "7️⃣ Sit back – your key arrives in seconds!\n\n"
        "⚠️ Always pay the exact amount including paisa!"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    text = (
        "*🆘 OFFICIAL SUPPORT CENTER*\n\n"
        "If you face any issues or have questions regarding our services, feel free to contact our expert team.\n\n"
        "📅 Active Time: 9 AM - 11 PM\n"
        "⏱️ Response: Within 5-10 Minutes\n\n"
        "Click the button below to start a chat:"
    )
    await update.message.reply_text(text, reply_markup=admin_contact_keyboard(), parse_mode="Markdown")

async def cmd_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    u = get_user(user_id)
    total = u.get("total_refers", 0)
    earnings = u.get("referral_earnings", 0.0)
    claimed = u.get("free_key_claimed", False)
    remaining = max(0, FREE_KEY_REFERRALS_NEEDED - total)
    
    text = f"""*💰 Referral Program*

Invite your friends and earn real balance for every successful joining.

• *Total Refers:* {total} User(s)
• *Invite Reward:* ₹{earnings:.2f} (₹1 per refer)

"""
    if not claimed:
        if remaining > 0:
            text += f"🎯 *Refer {remaining} more to get a FREE {FREE_KEY_PRODUCT}!*\n\n"
        else:
            text += f"🎉 *You've earned a FREE {FREE_KEY_PRODUCT}!*\n\n"
    else:
        text += f"✅ *You have claimed your FREE key!*\n\n"
    
    text += f"""*Your Invite Link:*
`{referral_link}`

Share your link to grow your earnings!"""
    
    await update.message.reply_text(text, reply_markup=refer_earn_keyboard(referral_link, total, not claimed), parse_mode="Markdown")

async def shop_now_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    await update.message.reply_text(
        "🛍️ *Our Products*\n\nSelect a product to purchase:",
        reply_markup=product_list_keyboard(),
        parse_mode="Markdown"
    )

# ==================== MAIN ====================
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers for bottom menu buttons
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("shop", cmd_shop))
    application.add_handler(CommandHandler("orders", cmd_orders))
    application.add_handler(CommandHandler("profile", cmd_profile))
    application.add_handler(CommandHandler("howtouse", cmd_howtouse))
    application.add_handler(CommandHandler("support", cmd_support))
    application.add_handler(CommandHandler("refer", cmd_refer))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(shop_now, pattern="^shop_now$"))
    application.add_handler(CallbackQueryHandler(product_selected, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(paid_confirmation, pattern="^paid_"))
    application.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    application.add_handler(CallbackQueryHandler(profile, pattern="^profile$"))
    application.add_handler(CallbackQueryHandler(how_to_use, pattern="^how_to_use$"))
    application.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    application.add_handler(CallbackQueryHandler(refer_earn, pattern="^refer_earn$"))
    application.add_handler(CallbackQueryHandler(claim_free_key, pattern="^claim_free_key$"))
    application.add_handler(CallbackQueryHandler(copy_upi, pattern="^copy_upi$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_name))
    application.add_handler(MessageHandler(filters.ALL, unknown))
    
    # Set bottom menu buttons
    application.job_queue.run_once(lambda x: set_bot_commands(application), 0)
    
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
