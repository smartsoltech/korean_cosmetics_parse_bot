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
import re

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
        f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке.\n"
        f"Также можете просто отправить ссылку на товар с сайта coupang.com."
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

        # Проверяем, что ссылка начинается с https://coupang.com
        if not url.startswith("https://coupang.com"):
            await update.message.reply_text("Пожалуйста, укажите ссылку на товар с сайта coupang.com.")
            return

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

async def check_coupang_link(update: Update, context: CallbackContext) -> None:
    """Проверка ссылки на coupang.com и парсинг цены"""
    message_text = update.message.text

    # Регулярное выражение для поиска ссылок в сообщении
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, message_text)

    if urls:
        for url in urls:
            # Проверяем, что это ссылка на coupang.com
            if "coupang.com" in url:
                await update.message.reply_text(f"Обнаружена ссылка на Coupang: {url}")
                
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
                return
            else:
                await update.message.reply_text("Пожалуйста, укажите ссылку на товар с сайта coupang.com.")
    else:
        await update.message.reply_text("Пожалуйста, отправьте ссылку для парсинга.")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start))
    
    # Обрабатываем команду 'цена [URL]'
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^цена '), get_price))

    # Обрабатываем любые текстовые сообщения с проверкой на ссылку на coupang.com
    application.add_handler(MessageHandler(filters.TEXT, check_coupang_link))

    application.run_polling()

if __name__ == '__main__':
    main()
