import logging
import os
import threading
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from dotenv import load_dotenv
from command_handler import CommandHandlerLogic
from order_manager import OrderManager
from file_watcher import start_watchdog

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Keyboards for orders and file options
order_keyboard = ReplyKeyboardMarkup([['нет', 'конец']], one_time_keyboard=True, resize_keyboard=True)
file_options_keyboard = ReplyKeyboardMarkup([['Дополнить заказ', 'Сформировать ТН', 'Посчитать стоимость']], one_time_keyboard=True, resize_keyboard=True)

# Initialize order management and command logic
order_manager = OrderManager(order_keyboard, file_options_keyboard)
command_logic = CommandHandlerLogic(order_manager, order_keyboard)

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        f"Привет! Я бот для управления заказами.\n"
        f"Используйте команду /заказ для начала работы."
    )

def main() -> None:
    # Start watchdog in background thread to monitor file changes
    watchdog_thread = threading.Thread(target=start_watchdog, args=("/usr/src/app/watched_directory",))
    watchdog_thread.daemon = True
    watchdog_thread.start()

    # Initialize bot
    application = Application.builder().token(API_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("order", command_logic.start_order))
    application.add_handler(MessageHandler(filters.Regex('заказ'), command_logic.start_order))
    
    # File upload handler
    application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), command_logic.handle_uploaded_file))
    
    # Action buttons handler
    application.add_handler(MessageHandler(filters.Regex('Дополнить заказ'), command_logic.supplement_order))
    application.add_handler(MessageHandler(filters.Regex('Сформировать ТН'), command_logic.generate_shipping_file))
    application.add_handler(MessageHandler(filters.Regex('Посчитать стоимость'), command_logic.calculate_total_cost))

    # Order text handling
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_logic.handle_text))

    application.run_polling()

if __name__ == '__main__':
    main()