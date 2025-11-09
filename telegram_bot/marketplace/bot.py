"""
Marketplace Bot - интернет-магазин в Telegram
"""
import logging
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show marketplace"""
    user = update.effective_user
    
    # Main keyboard with Mini App
    keyboard = [
        [KeyboardButton(
            text="🛍️ Open Store",
            web_app=WebAppInfo(url="https://online-shop-rose-omega.vercel.app/")
        )],
        [
            KeyboardButton(text="📦 My Orders"),
            KeyboardButton(text="❤️ Favorites")
        ],
        [
            KeyboardButton(text="👤 Profile"),
            KeyboardButton(text="💬 Support")
        ]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    welcome_text = (
        f"👋 <b>Welcome to Shopify Clone, {user.first_name}!</b>\n\n"
        f"🛍️ Browse thousands of products\n"
        f"🚚 Fast delivery\n"
        f"💳 Secure payments\n"
        f"🎁 Special offers\n\n"
        f"Click <b>'🛍️ Open Store'</b> to start shopping!\n"
        f"Or use the menu below to navigate."
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product categories"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Electronics", callback_data="cat_electronics"),
            InlineKeyboardButton("👕 Fashion", callback_data="cat_fashion")
        ],
        [
            InlineKeyboardButton("🏠 Home & Garden", callback_data="cat_home"),
            InlineKeyboardButton("📚 Books", callback_data="cat_books")
        ],
        [
            InlineKeyboardButton("🎮 Gaming", callback_data="cat_gaming"),
            InlineKeyboardButton("⚽ Sports", callback_data="cat_sports")
        ],
        [
            InlineKeyboardButton("🎨 Art & Crafts", callback_data="cat_art"),
            InlineKeyboardButton("🍔 Food", callback_data="cat_food")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📂 <b>Choose a category:</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's orders"""
    keyboard = [
        [InlineKeyboardButton("📦 View Order #12345", callback_data="order_12345")],
        [InlineKeyboardButton("📦 View Order #12344", callback_data="order_12344")],
        [InlineKeyboardButton("📦 View Order #12343", callback_data="order_12343")],
        [InlineKeyboardButton("📋 All Orders", callback_data="all_orders")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📦 <b>Your Recent Orders:</b>\n\n"
        "1. Order #12345 - $150.00 - ✅ <i>Delivered</i>\n"
        "2. Order #12344 - $89.99 - 🚚 <i>In Transit</i>\n"
        "3. Order #12343 - $45.50 - ⏳ <i>Processing</i>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show favorites"""
    await update.message.reply_text(
        "❤️ <b>Your Favorites (5 items)</b>\n\n"
        "1. Wireless Headphones - $89.99\n"
        "2. Smart Watch - $199.99\n"
        "3. Laptop Stand - $45.50\n"
        "4. USB-C Cable - $15.99\n"
        "5. Phone Case - $25.00\n\n"
        "Open store to view details!",
        parse_mode='HTML'
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile"""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")],
        [InlineKeyboardButton("📍 Addresses", callback_data="addresses")],
        [InlineKeyboardButton("💳 Payment Methods", callback_data="payments")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👤 <b>Your Profile</b>\n\n"
        f"<b>Name:</b> {user.first_name} {user.last_name or ''}\n"
        f"<b>Username:</b> @{user.username or 'Not set'}\n"
        f"<b>Telegram ID:</b> <code>{user.id}</code>\n\n"
        f"📊 <b>Statistics:</b>\n"
        f"• Total Orders: 12\n"
        f"• Total Spent: $1,234.56\n"
        f"• Member Since: Jan 2024",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Support information"""
    keyboard = [
        [InlineKeyboardButton("💬 Chat with Support", callback_data="chat_support")],
        [InlineKeyboardButton("📝 Submit Ticket", callback_data="submit_ticket")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💬 <b>Customer Support</b>\n\n"
        "📧 <b>Email:</b> support@shopify-clone.com\n"
        "📱 <b>Telegram:</b> @shopify_support\n"
        "⏰ <b>Working hours:</b> 24/7\n\n"
        "💡 We usually respond within 1 hour!",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    
    if text == "📦 My Orders":
        await my_orders(update, context)
    elif text == "❤️ Favorites":
        await favorites(update, context)
    elif text == "👤 Profile":
        await profile(update, context)
    elif text == "💬 Support":
        await support(update, context)
    elif text == "📂 Categories":
        await categories(update, context)
    else:
        await update.message.reply_text(
            "Please use the buttons below to navigate! 😊"
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("cat_"):
        category = data.replace("cat_", "").title()
        await query.edit_message_text(
            f"📂 <b>{category} Category</b>\n\n"
            f"Loading products...\n"
            f"Please use 'Open Store' button for full catalog!",
            parse_mode='HTML'
        )
    
    elif data.startswith("order_"):
        order_id = data.replace("order_", "")
        await query.edit_message_text(
            f"📦 <b>Order #{order_id}</b>\n\n"
            f"<b>Status:</b> In Transit\n"
            f"<b>Total:</b> $89.99\n"
            f"<b>Items:</b> 3\n"
            f"<b>Tracking:</b> TRACK123456\n\n"
            f"Expected delivery: Tomorrow",
            parse_mode='HTML'
        )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data from Web App"""
    import json
    data = json.loads(update.message.web_app_data.data)
    
    order_id = data.get('order_id', 'N/A')
    total = data.get('total', 0)
    
    await update.message.reply_text(
        f"✅ <b>Order Confirmed!</b>\n\n"
        f"📦 Order ID: #{order_id}\n"
        f"💰 Total: ${total}\n\n"
        f"We'll process your order shortly.\n"
        f"Track your order in 'My Orders'.",
        parse_mode='HTML'
    )


def main():
    """Start marketplace bot"""
    import os
    token = os.getenv('MARKETPLACE_BOT_TOKEN')
    
    if not token:
        logger.error("MARKETPLACE_BOT_TOKEN not found!")
        return
    
    application = Application.builder().token(token).build()
    
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("categories", categories))
    
    # Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("Marketplace Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
