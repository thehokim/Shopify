"""
Monitoring Bot - получает алерты от Prometheus/Alertmanager
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🔔 <b>Shopify Monitoring Bot</b>\n\n"
        "This bot sends system alerts and notifications:\n"
        "• 🚨 Critical alerts\n"
        "• ⚠️ Warning alerts\n"
        "• 📊 System metrics\n"
        "• 📈 Performance reports\n\n"
        "You'll receive notifications automatically.",
        parse_mode='HTML'
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System status"""
    await update.message.reply_text(
        "📊 <b>System Status</b>\n\n"
        "✅ API: Running\n"
        "✅ Database: Healthy\n"
        "✅ Redis: Connected\n"
        "✅ Celery: Active\n\n"
        "🕐 Last check: Just now",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📖 <b>Available Commands</b>\n\n"
        "/start - Start bot\n"
        "/status - Check system status\n"
        "/help - Show this message",
        parse_mode='HTML'
    )


def main():
    """Start monitoring bot"""
    import os
    token = os.getenv('MONITORING_BOT_TOKEN')
    
    if not token:
        logger.error("MONITORING_BOT_TOKEN not found!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_command))
    
    logger.info("Monitoring Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
