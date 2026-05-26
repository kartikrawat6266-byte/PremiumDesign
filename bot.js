import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from Railway environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables. Please set BOT_TOKEN in Railway.")

# UPI Configuration (You should change this to your own UPI ID)
UPI_ID = os.environ.get("UPI_ID", "example@okhdfcbank")
# Map of product names to their prices (INR)
PRODUCTS = {
    "1 Month Premium Key": 99.00,
    "1 Year Premium Key": 499.00,
    "Lifetime Premium Key": 999.00,
}

# Database file path (will be stored in Railway's ephemeral disk; consider using MongoDB or PostgreSQL for production)
DB_FILE = "user_data.json"

# --- Helper functions for data persistence ---
def load_user_data() -> Dict[str, Any]:
    """Load user data from JSON file."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.exception("Error loading user data")
        return {}

def save_user_data(data: Dict[str, Any]) -> None:
    """Save user data to JSON file."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError:
        logger.exception("Error saving user data")

def get_user(user_id: str) -> Dict[str, Any]:
    """Get user data, create if not exists."""
    data = load_user_data()
    if user_id not in data:
        data[user_id] = {
            "name": "",
            "username": "",
            "total_orders": 0,
            "referral_earnings": 0.0,
            "referred_by": None,
            "joined": datetime.now().strftime("%d/%m/%Y"),
            "orders": [],
            "pending_payment": None,  # store product name for pending payment
        }
        save_user_data(data)
    return data[user_id]

def update_user(user_id: str, update_data: Dict[str, Any]) -> None:
    """Update user data fields."""
    data = load_user_data()
    if user_id not in data:
        data[user_id] = {
            "name": "", "username": "", "total_orders": 0, "referral_earnings": 0.0,
            "referred_by": None, "joined": datetime.now().strftime("%d/%m/%Y"),
            "orders": [], "pending_payment": None,
        }
    data[user_id].update(update_data)
    save_user_data(data)

# --- Inline Keyboard Builders ---
def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create the main menu keyboard with all action buttons."""
    keyboard = [
        [InlineKeyboardButton("🛍️ Shop Now", callback_data="shop_now")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("📖 How to Use", callback_data="how_to_use")],
        [InlineKeyboardButton("🆘 Support", callback_data="support")],
        [InlineKeyboardButton("💰 Refer & Earn", callback_data="refer_earn")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_button() -> InlineKeyboardMarkup:
    """Simple back button to main menu."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]])

def product_list_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for product selection."""
    keyboard = []
    for name, price in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(f"{name} - ₹{price:.2f}", callback_data=f"product_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def payment_keyboard(product_name: str, amount: float) -> InlineKeyboardMarkup:
    """Keyboard for payment actions."""
    upi_link = f"upi://pay?pa={UPI_ID}&pn=Satyam%20X%20Store&am={amount}&cu=INR"
    keyboard = [
        [InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{product_name}")],
        [InlineKeyboardButton("💳 Copy UPI ID", callback_data="copy_upi")],
        [InlineKeyboardButton("📱 Open UPI App", url=upi_link)],
        [InlineKeyboardButton("🔙 Cancel", callback_data="shop_now")],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_contact_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for support contact."""
    keyboard = [
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/SATYAM_X_OFC")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Command and Callback Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command. Show welcome message and main menu."""
    user = update.effective_user
    user_id = str(user.id)
    
    # Check if referred by someone (if start param provided)
    if context.args and context.args[0].startswith("ref_"):
        referrer_id = context.args[0][4:]
        if referrer_id != user_id:
            # Add referral logic: give ₹10 reward to referrer when new user joins
            referrer_data = get_user(referrer_id)
            if referrer_data and not get_user(user_id).get("referred_by"):
                update_user(referrer_id, {"referral_earnings": referrer_data.get("referral_earnings", 0) + 10.0})
                update_user(user_id, {"referred_by": referrer_id})
                await update.message.reply_text("🎉 Welcome! You were referred by a friend.")
    
    # Get or create user data
    user_data = get_user(user_id)
    if not user_data["name"]:
        update_user(user_id, {"name": user.full_name or "User", "username": user.username or ""})
    
    welcome_text = (
        f"👋 Welcome to *Satyam X Ofc Store*!\n\n"
        f"Trusted selling bot – anyone can purchase from this bot.\n"
        f"⭐ *SUPER FAST DELIVERY*\n\n"
        f"📌 Use the buttons below to start shopping."
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to main menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🏠 *Main Menu*\n\nChoose an option:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def shop_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show product list for shopping."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🛍️ *Our Products*\n\nSelect a product to purchase:",
        reply_markup=product_list_keyboard(),
        parse_mode="Markdown"
    )

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle product selection, show payment details."""
    query = update.callback_query
    await query.answer()
    product_name = query.data.replace("product_", "")
    price = PRODUCTS.get(product_name)
    if not price:
        await query.edit_message_text("❌ Product not found.", reply_markup=back_to_menu_button())
        return
    
    user_id = str(query.from_user.id)
    update_user(user_id, {"pending_payment": product_name})
    
    payment_text = (
        f"💸 *Payment Required*\n\n"
        f"Product: {product_name}\n"
        f"Amount: ₹{price:.2f}\n\n"
        f"*How to Pay:*\n"
        f"1️⃣ Scan the QR or use UPI ID below\n"
        f"2️⃣ Pay exact amount ₹{price:.2f} (including paisa!)\n"
        f"3️⃣ Tap '✅ I Have Paid'\n"
        f"4️⃣ Enter your UPI registered name when asked\n\n"
        f"⚠️ *Partial payments will NOT be detected.*\n\n"
        f"💳 *UPI ID:* `{UPI_ID}`\n"
    )
    await query.edit_message_text(
        payment_text,
        reply_markup=payment_keyboard(product_name, price),
        parse_mode="Markdown"
    )

async def paid_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask for UPI name to simulate payment verification."""
    query = update.callback_query
    await query.answer()
    product_name = query.data.replace("paid_", "")
    context.user_data["pending_product"] = product_name
    await query.edit_message_text(
        f"✅ *Payment Initiated*\n\n"
        f"Please reply with the *exact name* as it appears in your UPI app.\n"
        f"(For verification purposes)\n\n"
        f"Type your name here:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="shop_now")]])
    )

async def handle_upi_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simulate payment confirmation and deliver key."""
    user_name = update.message.text.strip()
    user_id = str(update.effective_user.id)
    product_name = context.user_data.get("pending_product")
    
    if not product_name:
        await update.message.reply_text("❌ No pending payment. Please start over.", reply_markup=back_to_menu_button())
        return
    
    # Simulate payment verification (in reality, check UPI transaction)
    # Here we just generate a fake key.
    import random, string
    def generate_key():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    license_key = generate_key()
    price = PRODUCTS.get(product_name, 0)
    
    # Update user data
    user_data = get_user(user_id)
    new_order = {
        "product": product_name,
        "amount": price,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "key": license_key,
        "upi_name": user_name
    }
    orders = user_data.get("orders", [])
    orders.append(new_order)
    update_user(user_id, {
        "total_orders": user_data.get("total_orders", 0) + 1,
        "orders": orders,
        "pending_payment": None
    })
    
    # Clear context
    context.user_data["pending_product"] = None
    
    delivery_text = (
        f"🎉 *Payment Confirmed!*\n\n"
        f"Thank you {user_name} for your purchase.\n\n"
        f"📦 *Product:* {product_name}\n"
        f"🔑 *Your License Key:* `{license_key}`\n\n"
        f"⭐ *SUPER FAST DELIVERY*\n"
        f"Join our files channel for more: [All Files](https://t.me/satyamxofcfiles)\n\n"
        f"Need help? Contact @SATYAM_X_OFC"
    )
    await update.message.reply_text(delivery_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's order history."""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_data = get_user(user_id)
    orders = user_data.get("orders", [])
    
    if not orders:
        await query.edit_message_text(
            "📭 *No orders yet!*\n\nStart shopping to see your orders here.",
            reply_markup=back_to_menu_button(),
            parse_mode="Markdown"
        )
        return
    
    orders_text = "*📦 Your Orders*\n\n"
    for idx, order in enumerate(reversed(orders[-5:]), 1):  # show last 5
        orders_text += (
            f"{idx}. *{order['product']}*\n"
            f"   Amount: ₹{order['amount']:.2f}\n"
            f"   Date: {order['date']}\n"
            f"   Key: `{order['key']}`\n\n"
        )
    if len(orders) > 5:
        orders_text += f"_Showing last 5 of {len(orders)} orders._"
    await query.edit_message_text(orders_text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user account information."""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_data = get_user(user_id)
    
    profile_text = (
        f"👤 *User Account Information*\n\n"
        f"• *Name:* {user_data.get('name', 'N/A')}\n"
        f"• *Username:* @{user_data.get('username', 'N/A')}\n"
        f"• *User ID:* `{user_id}`\n\n"
        f"• *Total Orders:* {user_data.get('total_orders', 0)}\n"
        f"• *Referral Earnings:* ₹{user_data.get('referral_earnings', 0):.2f}\n\n"
        f"• *Joined:* {user_data.get('joined', datetime.now().strftime('%d/%m/%Y'))}"
    )
    await query.edit_message_text(profile_text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show how to buy instructions."""
    query = update.callback_query
    await query.answer()
    usage_text = (
        "*📖 How to Buy — SATYAM X MOD STORE*\n\n"
        "1. Tap Shop Now\n"
        "2. Pick your product & plan\n"
        "3. Scan the UPI QR or copy UPI ID\n"
        "4. Pay the exact amount shown (with paisa!)\n"
        "5. Tap ✅ I Have Paid\n"
        "6. Enter your UPI registered name\n"
        "7. Sit back – your key arrives in seconds!\n\n"
        "⚠️ *Always pay the exact amount including paisa.*\n"
        "Partial or rounded payments will NOT be detected."
    )
    await query.edit_message_text(usage_text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show support center with contact button."""
    query = update.callback_query
    await query.answer()
    support_text = (
        "*🆘 OFFICIAL SUPPORT CENTER*\n\n"
        "If you face any issues or have questions regarding our services, feel free to contact our expert team.\n\n"
        "📅 *Active Time:* 9 AM - 11 PM\n"
        "⏱️ *Response:* Within 5-10 Minutes\n\n"
        "Click the button below to start a chat:"
    )
    await query.edit_message_text(support_text, reply_markup=admin_contact_keyboard(), parse_mode="Markdown")

async def refer_earn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show referral information and link."""
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    refer_text = (
        "*💰 Refer & Earn*\n\n"
        "Invite your friends and earn rewards!\n\n"
        "For each friend who joins using your link and makes their first purchase, you get **₹10** credited to your account.\n\n"
        f"*Your Referral Link:*\n`{referral_link}`\n\n"
        "Share this link with your friends and start earning!"
    )
    # Add an inline button to copy link (simple instruction)
    await query.edit_message_text(refer_text, reply_markup=back_to_menu_button(), parse_mode="Markdown")

async def copy_upi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle copy UPI ID request."""
    query = update.callback_query
    await query.answer("UPI ID copied to clipboard!", show_alert=True)
    # No actual clipboard action; just notification.

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands/messages."""
    await update.message.reply_text("❌ I don't understand that. Please use the menu buttons.", reply_markup=main_menu_keyboard())

# --- Main Application ---
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    
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
    application.add_handler(CallbackQueryHandler(copy_upi, pattern="^copy_upi$"))
    
    # Message handler for UPI name input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_upi_name))
    
    # Fallback for unknown messages
    application.add_handler(MessageHandler(filters.ALL, unknown))
    
    # Start polling
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
