# # import logging
# # import os
# # import re
# # from datetime import datetime
# # import threading
# # import pandas as pd
# # from telegram import Update, ReplyKeyboardMarkup
# # from telegram.ext import (
# #     Application,
# #     CommandHandler,
# #     MessageHandler,
# #     filters,
# #     CallbackContext,
# # )
# # from dotenv import load_dotenv
# # from command_handler import CommandHandlerLogic
# # from order_manager import OrderManager
# # from file_watcher import start_watchdog

# # # Load environment variables from .env file
# # load_dotenv()

# # API_TOKEN = os.getenv('API_TOKEN')
# # BOT_USERNAME = os.getenv('BOT_USERNAME')

# # logging.basicConfig(
# #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# #     level=logging.INFO,
# #     handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
# # )

# # logger = logging.getLogger(__name__)

# # # Клавиатура для заказов и файлов
# # order_keyboard = ReplyKeyboardMarkup([['нет', 'конец']], one_time_keyboard=True, resize_keyboard=True)
# # file_options_keyboard = ReplyKeyboardMarkup([['Дополнить заказ', 'Сформировать ТН', 'Посчитать стоимость']], one_time_keyboard=True, resize_keyboard=True)

# # # Инициализация управления заказами и командной логики
# # order_manager = OrderManager(order_keyboard, file_options_keyboard)
# # command_logic = CommandHandlerLogic(order_manager, order_keyboard)

# # async def start(update: Update, context: CallbackContext) -> None:
# #     logger.info("Command /start received")
# #     await update.message.reply_text(
# #         f"Привет! Я бот для парсинга ссылок и оформления заказов.\n"
# #         f"Используйте команду /заказ для начала работы."
# #     )

# # def main() -> None:
# #     # Запуск watchdog в фоновом режиме
# #     watchdog_thread = threading.Thread(target=start_watchdog, args=("/usr/src/app/watched_directory",))
# #     watchdog_thread.daemon = True
# #     watchdog_thread.start()

# #     # Инициализация бота
# #     application = Application.builder().token(API_TOKEN).build()

# #     # Команды
# #     application.add_handler(CommandHandler("start", start))
# #     application.add_handler(MessageHandler(filters.Regex('заказ'), command_logic.start_order))
# #     application.add_handler(MessageHandler(filters.Regex(r'^цена\s+https?://'), command_logic.handle_price))

# #     # Обработка файла
# #     application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), command_logic.handle_uploaded_file))
    
# #     application.add_handler(MessageHandler(filters.Regex('Дополнить заказ'), order_manager.supplement_order))
# #     application.add_handler(MessageHandler(filters.Regex('Сформировать ТН'), order_manager.generate_shipping_filename))
# #     application.add_handler(MessageHandler(filters.Regex('Посчитать стоимость'), order_manager.calculate_total_cost))

# #     # Обработка текста для заказа
# #     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_logic.handle_text))

# #     application.run_polling()

# # if __name__ == '__main__':
# #     main()


# import logging
# import os
# import re
# from datetime import datetime
# import threading
# import pandas as pd
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     CallbackContext,
# )
# from dotenv import load_dotenv
# from command_handler import CommandHandlerLogic
# from order_manager import OrderManager
# from file_watcher import start_watchdog

# # Load environment variables from .env file
# load_dotenv()

# API_TOKEN = os.getenv('API_TOKEN')
# BOT_USERNAME = os.getenv('BOT_USERNAME')

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO,
#     handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
# )

# logger = logging.getLogger(__name__)

# # Клавиатура для заказов и файлов
# order_keyboard = ReplyKeyboardMarkup([['нет', 'конец']], one_time_keyboard=True, resize_keyboard=True)
# file_options_keyboard = ReplyKeyboardMarkup([['Дополнить заказ', 'Сформировать ТН', 'Посчитать стоимость']], one_time_keyboard=True, resize_keyboard=True)

# # Инициализация управления заказами и командной логики
# order_manager = OrderManager(order_keyboard, file_options_keyboard)
# command_logic = CommandHandlerLogic(order_manager, order_keyboard)

# async def start(update: Update, context: CallbackContext) -> None:
#     logger.info("Command /start received")
#     await update.message.reply_text(
#         f"Привет! Я бот для парсинга ссылок и оформления заказов.\n"
#         f"Используйте команду /заказ для начала работы."
#     )

# def main() -> None:
#     # Запуск watchdog в фоновом режиме
#     watchdog_thread = threading.Thread(target=start_watchdog, args=("/usr/src/app/watched_directory",))
#     watchdog_thread.daemon = True
#     watchdog_thread.start()

#     # Инициализация бота
#     application = Application.builder().token(API_TOKEN).build()

#     # Команды
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.Regex('заказ'), command_logic.start_order))
#     application.add_handler(MessageHandler(filters.Regex(r'^цена\s+https?://'), command_logic.handle_price))

#     # Обработка файла
#     application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), command_logic.handle_uploaded_file))
    
#     # Обработка кнопок действий
#     application.add_handler(MessageHandler(filters.Regex('Дополнить заказ'), order_manager.supplement_order))
#     application.add_handler(MessageHandler(filters.Regex('Сформировать ТН'), order_manager.generate_shipping_file))  # Исправляем на правильный метод
#     application.add_handler(MessageHandler(filters.Regex('Посчитать стоимость'), order_manager.calculate_total_cost))

#     # Обработка текста для заказа
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_logic.handle_text))

#     application.run_polling()

# if __name__ == '__main__':
#     main()

import logging
import os
import re
from datetime import datetime
import threading
import pandas as pd
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

# Клавиатура для заказов и файлов
order_keyboard = ReplyKeyboardMarkup([['нет', 'конец']], one_time_keyboard=True, resize_keyboard=True)
file_options_keyboard = ReplyKeyboardMarkup([['Дополнить заказ', 'Сформировать ТН', 'Посчитать стоимость']], one_time_keyboard=True, resize_keyboard=True)

# Инициализация управления заказами и командной логики
order_manager = OrderManager(order_keyboard, file_options_keyboard)
command_logic = CommandHandlerLogic(order_manager, order_keyboard)

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        f"Привет! Я бот для парсинга ссылок и оформления заказов.\n"
        f"Используйте команду /заказ для начала работы."
    )

def main() -> None:
    # Запуск watchdog в фоновом режиме
    watchdog_thread = threading.Thread(target=start_watchdog, args=("/usr/src/app/watched_directory",))
    watchdog_thread.daemon = True
    watchdog_thread.start()

    # Инициализация бота
    application = Application.builder().token(API_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("order", command_logic.start_order))
    application.add_handler(MessageHandler(filters.Regex(r'^цена\s+https?://'), command_logic.handle_price))
    application.add_handler(MessageHandler(filters.Regex('заказ'), command_logic.start_order))
    # Обработка файла
    application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), command_logic.handle_uploaded_file))
    
    # Обработка кнопок действий
    application.add_handler(MessageHandler(filters.Regex('Дополнить заказ'), order_manager.supplement_order))
    application.add_handler(MessageHandler(filters.Regex('Сформировать ТН'), lambda update, context: order_manager.generate_shipping_file(update, context)))  # Исправлено
    application.add_handler(MessageHandler(filters.Regex('Посчитать стоимость'), lambda update, context: order_manager.calculate_total_cost(update, context)))  # Добавлен context

    # Обработка текста для заказа
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_logic.handle_text))

    # # Обработка текстов и команд
    # application.add_handler(MessageHandler(filters.Text & ~filters.command, command_logic.handle_text))

    # Обработка команд (например, команда /start)
    application.add_handler(CommandHandler("start", start))

    # Обработка документов (например, файлов .xlsx)
    application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), command_logic.handle_uploaded_file))

    # Обработка команд в группе
    application.add_handler(MessageHandler(filters.Command, command_logic.handle_command_in_group))
    application.run_polling()

if __name__ == '__main__':
    main()
