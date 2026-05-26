import os
import json
import logging
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
# BIGGER BUTTONS - EXACT LAYOUT
def main_menu_keyboard():
    """Buttons with bigger size - exact screenshot layout"""
    keyboard = [
        [InlineKeyboardButton("  🛍️  SHOP NOW  🛍️  ", callback_data="shop_now")],
        [InlineKeyboardButton("  📦  MY ORDERS  📦  ", callback_data="my_orders"), 
         InlineKeyboardButton("  👤  PROFILE  👤  ", callback_data="profile")],
        [InlineKeyboardButton("  📖  HOW TO USE  📖  ", callback_data="how_to_use"), 
         InlineKeyboardButton("  🆘  SUPPORT  🆘  ", callback_data="support")],
        [InlineKeyboardButton("  💰  REFER & EARN  💰  ", callback_data="refer_earn")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Back button - same size
def get_back_menu():
    return main_menu_keyboard()

def product_list_keyboard():
    keyboard = []
    for name, price in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(f"✨ {name} - ₹{price:.2f} ✨", callback_data=f"product_{name}")])
    keyboard.append([InlineKeyboardButton("🔙  BACK TO MENU  🔙", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def payment_keyboard(product_name, amount):
    upi_link = f"upi://pay?pa={UPI_ID}&pn=Satyam%20X%20Store&am={amount}&cu=INR"
    keyboard = [
        [InlineKeyboardButton("✅  I HAVE PAID  ✅", callback_data=f"paid_{product_name}")],
        [InlineKeyboardButton("💳  COPY UPI ID  💳", callback_data="copy_upi")],
        [InlineKeyboardButton("📱  OPEN UPI APP  📱", url=upi_link)],
        [InlineKeyboardButton("🔙  BACK TO MENU  🔙", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_contact_keyboard():
    keyboard = [
        [InlineKeyboardButton("📞  CONTACT ADMIN  📞", url="https://t.me/SATYAM_X_OFC")],
        [InlineKeyboardButton("🔙  BACK TO MENU  🔙", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def refer_earn_keyboard(referral_link, total_refers, free_available):
    keyboard = []
    if total_refers >= FREE_KEY_REFERRALS_NEEDED and free_available:
        keyboard.append([InlineKeyboardButton("🎁  CLAIM FREE KEY  🎁", callback_data="claim_free_key")])
    keyboard.append([InlineKeyboardButton("📤  SHARE WITH FRIEND  📤", url=f"https://t.me/share/url?url={referral_link}&text=🔥 Join Satyam X Ofc Store and get premium keys! Use my referral link:")])
    keyboard.append([InlineKeyboardButton("🔙  BACK TO MENU  🔙", callback_data="main_menu")])
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
                        text=f"🎉 *NEW REFERRAL!* 🎉\n\n{username} joined!\n\n📊 *TOTAL REFERS:* {updated_referrer.get('total_refers', 0)}\n💰 *EARNINGS:* ₹{updated_referrer.get('referral_earnings', 0):.2f}",
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
                        "🎉 WELCOME! You were referred by a friend!\n\nUse the buttons below.",
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
        f"👋 WELCOME TO *SATYAM X OFC STORE*!\n\n"
        f"✅ TRUSTED SELLING BOT\n"
        f"⭐ *SUPER FAST DELIVERY*\n\n"
        f"📌 USE THE BUTTONS BELOW TO START SHOPPING."
    )
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    await query.edit_message_text(
        "🏠 *MAIN MENU*\n\nCHOOSE AN OPTION:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    await query.edit_message_text(
        "🛍️ *OUR PRODUCTS*\n\nSELECT A PRODUCT TO PURCHASE:",
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
        await query.edit_message_text("❌ PRODUCT NOT FOUND.", reply_markup=get_back_menu())
        return
    
    update_user(user_id, {"pending_payment": product_name})
    
    payment_text = (
        f"💸 *PAYMENT REQUIRED*\n\n"
        f"📦 PRODUCT: {product_name}\n"
        f"💰 AMOUNT: ₹{price:.2f}\n\n"
        f"📌 *HOW TO PAY:*\n"
        f"1️⃣ TAP '✅ I HAVE PAID'\n"
        f"2️⃣ ENTER UPI REGISTERED NAME\n\n"
        f"💳 *UPI ID:* `{UPI_ID}`\n"
        f"⚠️ PAY EXACT AMOUNT!"
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
        "✅ ENTER YOUR UPI REGISTERED NAME:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙  CANCEL  🔙", callback_data="shop_now")]])
    )

async def handle_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    update_last_activity(user_id)
    product_name = context.user_data.get("pending_product")
    
    if not product_name:
        await update.message.reply_text("❌ NO PENDING PAYMENT.", reply_markup=get_back_menu())
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
        f"🎉 *PAYMENT CONFIRMED!* 🎉\n\n📦 {product_name}\n🔑 `{license_key}`\n\n⭐ *SUPER FAST DELIVERY*",
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
            "📭 *NO ORDERS YET!*\n\nSTART SHOPPING TO SEE YOUR ORDERS HERE.",
            reply_markup=get_back_menu(),
            parse_mode="Markdown"
        )
        return
    
    text = "*📦 YOUR ORDERS*\n\n"
    for i, o in enumerate(reversed(orders[-10:]), 1):
        amt = f"₹{o['amount']:.2f}" if o['amount'] > 0 else "🎁 FREE"
        text += f"{i}. *{o['product']}*\n   💰 AMOUNT: {amt}\n   📅 DATE: {o['date']}\n   🔑 KEY: `{o['key']}`\n\n"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode="Markdown")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    u = get_user(user_id)
    
    username = u.get('username', '')
    username_display = f"@{username}" if username else "NOT SET"
    
    referral_history = u.get("referral_history", [])
    referral_text = ""
    if referral_history:
        referral_text = "\n\n📜 *REFERRAL HISTORY:*"
        for ref in referral_history[-5:]:
            referral_text += f"\n   • {ref.get('username', 'UNKNOWN')} - ₹{ref.get('earned', 0):.2f} ({ref.get('date', '')})"
    
    text = (
        f"❄️ *USER ACCOUNT INFORMATION*\n\n"
        f"• NAME : {u.get('name', 'N/A')}\n"
        f"• USERNAME : {username_display}\n"
        f"• USER ID : `{user_id}`\n\n"
        f"• TOTAL ORDERS : {u.get('total_orders', 0)}\n"
        f"• REFERRAL EARNINGS : ₹{u.get('referral_earnings', 0):.2f}{referral_text}\n\n"
        f"• JOINED DATE : {u.get('joined', get_joined_date())}\n"
        f"⭐ LAST ACTIVITY : {u.get('last_activity', get_current_ist())}"
    )
    
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode="Markdown")

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    text = (
        "*📖 HOW TO BUY — SATYAM X MOD STORE*\n\n"
        "1️⃣ TAP SHOP NOW\n"
        "2️⃣ PICK YOUR PRODUCT & PLAN\n"
        "3️⃣ SCAN UPI QR OR COPY UPI ID\n"
        "4️⃣ PAY EXACT AMOUNT (WITH PAISA!)\n"
        "5️⃣ TAP ✅ I HAVE PAID\n"
        "6️⃣ ENTER YOUR UPI REGISTERED NAME\n"
        "7️⃣ YOUR KEY ARRIVES IN SECONDS!\n\n"
        "⚠️ *ALWAYS PAY EXACT AMOUNT INCLUDING PAISA!*"
    )
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_activity(user_id)
    text = (
        "*🆘 OFFICIAL SUPPORT CENTER*\n\n"
        "IF YOU FACE ANY ISSUES OR HAVE QUESTIONS REGARDING OUR SERVICES, FEEL FREE TO CONTACT OUR EXPERT TEAM.\n\n"
        "📅 ACTIVE TIME: 9 AM - 11 PM\n"
        "⏱️ RESPONSE: WITHIN 5-10 MINUTES\n\n"
        "CLICK THE BUTTON BELOW TO START A CHAT:"
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
    
    text = f"""*💰 REFERRAL PROGRAM*

INVITE YOUR FRIENDS AND EARN REAL BALANCE FOR EVERY SUCCESSFUL JOINING.

• *TOTAL REFERS:* {total} USER(S)
• *INVITE REWARD:* ₹{earnings:.2f} (₹1 PER REFER)

"""
    if not claimed:
        if remaining > 0:
            text += f"🎯 *REFER {remaining} MORE TO GET A FREE {FREE_KEY_PRODUCT}!*\n\n"
        else:
            text += f"🎉 *YOU'VE EARNED A FREE {FREE_KEY_PRODUCT}!*\n\n"
    else:
        text += f"✅ *YOU HAVE CLAIMED YOUR FREE KEY!*\n\n"
    
    text += f"""*YOUR INVITE LINK:*
`{referral_link}`

SHARE YOUR LINK TO GROW YOUR EARNINGS!"""
    
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
            f"❌ NEED {remaining} MORE REFERRALS FOR FREE KEY!",
            reply_markup=get_back_menu()
        )

async def copy_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("UPI ID COPIED!", show_alert=True)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("❌ PLEASE USE MENU BUTTONS.", reply_markup=main_menu_keyboard())

# ==================== MAIN ====================
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
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
    
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
