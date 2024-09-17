# bot.py
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
import os
from dotenv import load_dotenv
from parser import Parser  # Импортируем Parser из модуля parser

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# Configure logging to log to a file
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        f"Привет! Я бот для парсинга ссылок и цен.\n"
        f"Напишите @{BOT_USERNAME} заказ чтобы начать парсинг.\n"
        f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке."
    )

async def get_price(update: Update, context: CallbackContext) -> None:
    """Извлекаем цену товара по URL"""
    try:
        # Извлекаем URL из сообщения пользователя
        message_text = update.message.text
        parts = message_text.split()
        
        if len(parts) < 2:
            await update.message.reply_text("Пожалуйста, укажите ссылку на товар. Формат: 'цена [URL]'.")
            return
        
        url = parts[1]

        # Создаем объект Parser для парсинга страницы
        parser = Parser(url)
        prices = parser.parse_prices()

        if prices:
            response_text = "Цены на товар:\n"
            for price_type, price in prices.items():
                response_text += f"{price_type}: {price}\n"
            await update.message.reply_text(response_text)
        else:
            await update.message.reply_text("Не удалось извлечь цены с указанной страницы.")
    except Exception as e:
        logger.error(f"Произошла ошибка при извлечении цены: {e}")
        await update.message.reply_text("Произошла ошибка при парсинге страницы. Пожалуйста, попробуйте позже.")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^цена '), get_price))  # Добавляем обработку команды 'цена'

    application.run_polling()

if __name__ == '__main__':
    main()
