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
import pandas as pd

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

# Путь к файлу Excel для сохранения данных
EXCEL_FILE_PATH = 'products.xlsx'

def clean_url(url):
    """Отсекаем все параметры после '?' в URL, чтобы получить чистую ссылку на товар"""
    clean_url = url.split('?')[0]  # Убираем все, что идет после '?'
    logger.info(f"Чистая ссылка на товар: {clean_url}")
    return clean_url

def add_product_to_excel(url, prices):
    """Добавляем товар в Excel"""
    # Проверяем, существует ли файл
    if os.path.exists(EXCEL_FILE_PATH):
        df = pd.read_excel(EXCEL_FILE_PATH)
    else:
        # Если файл не существует, создаем новый DataFrame
        df = pd.DataFrame(columns=['Ссылка', 'Оригинальная цена', 'Продажная цена', 'Цена по купону'])

    # Создаем новую запись для таблицы
    new_product = pd.DataFrame([{
        'Ссылка': url,
        'Оригинальная цена': prices.get('original_price', ''),
        'Продажная цена': prices.get('sale_price', ''),
        'Цена по купону': prices.get('coupon_price', '')
    }])

    # Добавляем новую строку
    df = pd.concat([df, new_product], ignore_index=True)

    # Сохраняем обновленную таблицу в Excel
    df.to_excel(EXCEL_FILE_PATH, index=False)
    logger.info(f"Товар добавлен в таблицу: {new_product}")

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        f"Привет! Я бот для парсинга ссылок и цен.\n"
        f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке.\n"
        f"Также можете просто отправить ссылку на товар с сайта coupang.com."
    )

async def check_coupang_link(update: Update, context: CallbackContext) -> None:
    """Проверка ссылки на coupang.com и парсинг цены"""
    message_text = update.message.text

    # Регулярное выражение для поиска ссылок в сообщении
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, message_text)

    if urls:
        for url in urls:
            # Очищаем ссылку, убираем параметры после '?'
            clean_product_url = clean_url(url)

            # Проверяем, что это ссылка на coupang.com
            if "coupang.com" in clean_product_url:
                await update.message.reply_text(f"Обнаружена ссылка на Coupang: {clean_product_url}")
                logger.info(f"Обнаружена ссылка на Coupang: {clean_product_url}")
                
                await update.message.reply_text("Начинаем парсинг страницы через браузер...")
                logger.info("Начинаем парсинг страницы через браузер...")

                # Создаем объект Parser для парсинга страницы через Selenium
                parser = Parser(clean_product_url)
                prices = parser.parse_prices()

                if prices:
                    response_text = "Цены на товар:\n"
                    for price_type, price in prices.items():
                        response_text += f"{price_type}: {price}\n"
                    
                    # Добавляем информацию о товаре в таблицу
                    add_product_to_excel(clean_product_url, prices)

                    # Отправляем сообщение с ценами
                    await update.message.reply_text(response_text)
                    logger.info("Цены успешно отправлены в чат и добавлены в таблицу")
                else:
                    await update.message.reply_text("Не удалось извлечь цены с указанной страницы.")
                    logger.error("Не удалось извлечь цены с указанной страницы.")
                return
            else:
                await update.message.reply_text("Пожалуйста, укажите ссылку на товар с сайта coupang.com.")
                logger.error("Ссылка не принадлежит coupang.com")
    else:
        await update.message.reply_text("Пожалуйста, отправьте ссылку для парсинга.")
        logger.error("Сообщение не содержит ссылок")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start))
    
    # Обрабатываем команду 'цена [URL]'
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^цена '), check_coupang_link))

    # Обрабатываем любые текстовые сообщения с проверкой на ссылку на coupang.com
    application.add_handler(MessageHandler(filters.TEXT, check_coupang_link))

    application.run_polling()

if __name__ == '__main__':
    main()
