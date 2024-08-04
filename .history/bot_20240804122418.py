import logging
from telegram import Update, Document
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

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global state
parsing_mode = False
parsed_data = []

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я бот для парсинга ссылок.\n"
        "Напишите @bot заказ чтобы начать парсинг.\n"
        "Напишите конец чтобы завершить парсинг и получить таблицу."
    )

async def start_parsing(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    parsing_mode = True
    parsed_data.clear()
    await update.message.reply_text(
        "Режим парсинга активирован. Отправьте ссылки и количество. Напишите 'конец' чтобы завершить."
    )

async def stop_parsing(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    parsing_mode = False

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
    if parsing_mode:
        try:
            link, quantity = update.message.text.split()
            parsed_data.append((link, int(quantity)))
            await update.message.reply_text(f"Добавлено: {link} - {quantity}")
        except ValueError:
            await update.message.reply_text("Ошибка! Убедитесь, что отправляете сообщение в формате 'ссылка количество'.")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Add handlers for commands and messages with @username
    bot_username = 'your_bot_username'  # Replace with your bot's username

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.Regex(f'@{bot_username} заказ'), start_parsing))
    application.add_handler(MessageHandler(filters.Regex(f'@{bot_username} конец'), stop_parsing))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message))

    application.run_polling()

if __name__ == '__main__':
    main()
сщг