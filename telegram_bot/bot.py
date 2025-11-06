"""
Telegram Bot with Mini App integration
"""
import logging
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from app.config import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show Mini App button"""
    user = update.effective_user
    
    # Кнопка для открытия Mini App
    keyboard = [
        [KeyboardButton(
            text="🛍️ Open Store",
            web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}")
        )],
        [KeyboardButton(text="📦 My Orders")],
        [KeyboardButton(text="👤 Profile")],
        [KeyboardButton(text="💬 Support")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text(
        f"👋 Welcome to Shopify Clone, {user.first_name}!\n\n"
        f"🛍️ Browse products directly in Telegram\n"
        f"📦 Track your orders\n"
        f"💳 Secure payments\n\n"
        f"Click '🛍️ Open Store' to start shopping!",
        reply_markup=reply_markup
    )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's orders"""
    await update.message.reply_text(
        "📦 Your Recent Orders:\n\n"
        "1. Order #12345 - $150.00 - ✅ Delivered\n"
        "2. Order #12344 - $89.99 - 🚚 In Transit\n"
        "3. Order #12343 - $45.50 - ⏳ Processing\n\n"
        "Click 'Open Store' to view details"
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile"""
    user = update.effective_user
    await update.message.reply_text(
        f"👤 Your Profile\n\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Telegram ID: {user.id}\n"
        f"Username: @{user.username or 'Not set'}\n\n"
        f"📊 Total Orders: 12\n"
        f"💰 Total Spent: $1,234.56"
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Support information"""
    await update.message.reply_text(
        "💬 Support\n\n"
        "📧 Email: support@shopify-clone.com\n"
        "📱 Telegram: @shopify_support\n"
        "⏰ Working hours: 24/7\n\n"
        "We usually respond within 1 hour!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    
    if text == "📦 My Orders":
        await my_orders(update, context)
    elif text == "👤 Profile":
        await profile(update, context)
    elif text == "💬 Support":
        await support(update, context)
    else:
        await update.message.reply_text(
            "Please use the buttons below to navigate!"
        )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data from Web App"""
    data = update.message.web_app_data.data
    logger.info(f"Received Web App data: {data}")
    
    await update.message.reply_text(
        f"✅ Order received!\n\n"
        f"We'll process your order shortly."
    )


def main():
    """Start the bot"""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
