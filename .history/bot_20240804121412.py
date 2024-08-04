import logging
from telegram import Update, Document
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global state
parsing_mode = False
parsed_data = []

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Я бот для парсинга ссылок.\n"
                              "Напишите @bot заказ чтобы начать парсинг.\n"
                              "Напишите конец чтобы завершить парсинг и получить таблицу.")

def start_parsing(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    parsing_mode = True
    parsed_data.clear()
    update.message.reply_text("Режим парсинга активирован. Отправьте ссылки и количество. Напишите 'конец' чтобы завершить.")

def stop_parsing(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    parsing_mode = False

    if parsed_data:
        df = pd.DataFrame(parsed_data, columns=['Ссылка', 'Количество'])
        file_path = 'parsed_links.xlsx'
        df.to_excel(file_path, index=False)

        with open(file_path, 'rb') as file:
            update.message.reply_document(document=Document(file), caption="Вот ваша таблица.")
    else:
        update.message.reply_text("Данных для записи нет.")

def parse_message(update: Update, context: CallbackContext) -> None:
    global parsing_mode
    if parsing_mode:
        try:
            link, quantity = update.message.text.split()
            parsed_data.append((link, int(quantity)))
            update.message.reply_text(f"Добавлено: {link} - {quantity}")
        except ValueError:
            update.message.reply_text("Ошибка! Убедитесь, что отправляете сообщение в формате 'ссылка количество'.")

def main() -> None:
    updater = Updater(API_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(MessageHandler(Filters.regex('@bot заказ'), start_parsing))
    dispatcher.add_handler(MessageHandler(Filters.regex('конец'), stop_parsing))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, parse_message))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
