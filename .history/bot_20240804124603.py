import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')  # Имя пользователя вашего бота, например "mybot"

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

# Global state
parsing_mode = False
parsed_data = []

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        f"Привет! Я бот для парсинга ссылок.\n"
        f"Напишите @{BOT_USERNAME} заказ чтобы начать парсинг.\n"
        f"Напишите @{BOT_USERNAME} конец чтобы завершить парсинг и получить таблицу."
    )

async def start_parsing(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    parsing_mode = True
    parsed_data.clear()
    logger.info("Parsing mode activated")
    await update.message.reply_text(
        "Режим парсинга активирован. Отправьте ссылки и количество. Напишите 'конец' чтобы завершить."
    )

async def stop_parsing(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    parsing_mode = False
    logger.info("Parsing mode deactivated")

    if parsed_data:
        df = pd.DataFrame(parsed_data, columns=['Ссылка', 'Количество'])
        file_path = 'parsed_links.xlsx'
        df.to_excel(file_path, index=False)

        with open(file_path, 'rb') as file:
            await update.message.reply_document(document=file, caption="Вот ваша таблица.")
        os.remove(file_path)
    else:
        await update.message.reply_text("Данных для записи нет.")

async def parse_message(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    logger.info(f"Parsing mode: {parsing_mode}, received message: {update.message.text}")
    if parsing_mode:
        try:
            link, quantity = update.message.text.split()
            parsed_data.append((link, int(quantity)))
            logger.info(f"Added: {link} - {quantity}")
            await update.message.reply_text(f"Добавлено: {link} - {quantity}")
        except ValueError:
            logger.error("Error parsing message")
            await update.message.reply_text("Ошибка! Убедитесь, что отправляете сообщение в формате 'ссылка количество'.")

async def log_message(update: Update, context: CallbackContext) -> None:
    logger.info(f"Received message: {update.message.text}")
    logger.info(f"From user: {update.message.from_user.username}")
    logger.info(f"Chat ID: {update.message.chat_id}")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Add handlers for commands and messages with @username
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start_parsing))
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} конец'), stop_parsing))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message))

    # Log all incoming messages
    application.add_handler(MessageHandler(filters.ALL, log_message))

    application.run_polling()

if __name__ == '__main__':
    main()
