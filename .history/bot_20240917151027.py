# # # # bot.py
# # # import logging
# # # from telegram import Update
# # # from telegram.ext import (
# # #     Application,
# # #     CommandHandler,
# # #     MessageHandler,
# # #     filters,
# # #     CallbackContext,
# # # )
# # # import os
# # # from dotenv import load_dotenv
# # # from parser import Parser  # Импортируем Parser из модуля parser
# # # import re
# # # import pandas as pd

# # # # Load environment variables from .env file
# # # load_dotenv()

# # # API_TOKEN = os.getenv('API_TOKEN')
# # # BOT_USERNAME = os.getenv('BOT_USERNAME')

# # # # Configure logging to log to a file
# # # logging.basicConfig(
# # #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# # #     level=logging.INFO,
# # #     handlers=[
# # #         logging.FileHandler("bot.log"),
# # #         logging.StreamHandler()
# # #     ]
# # # )

# # # logger = logging.getLogger(__name__)

# # # # Путь к файлу Excel для сохранения данных
# # # EXCEL_FILE_PATH = 'products.xlsx'

# # # def clean_url(url):
# # #     """Отсекаем все параметры после '?' в URL, чтобы получить чистую ссылку на товар"""
# # #     clean_url = url.split('?')[0]  # Убираем все, что идет после '?'
# # #     logger.info(f"Чистая ссылка на товар: {clean_url}")
# # #     return clean_url

# # # def add_product_to_excel(url, product_info):
# # #     """Добавляем товар в Excel"""
# # #     # Проверяем, существует ли файл
# # #     if os.path.exists(EXCEL_FILE_PATH):
# # #         df = pd.read_excel(EXCEL_FILE_PATH)
# # #     else:
# # #         # Если файл не существует, создаем новый DataFrame
# # #         df = pd.DataFrame(columns=['Ссылка', 'Название товара', 'Страна происхождения', 'Рейтинг', 'Количество отзывов', 'Оригинальная цена', 'Стоимость доставки', 'Продавец', 'Опции товара'])

# # #     # Создаем новую запись для таблицы
# # #     new_product = pd.DataFrame([{
# # #         'Ссылка': url,
# # #         'Название товара': product_info.get('Название товара', ''),
# # #         'Страна происхождения': product_info.get('Страна происхождения', ''),
# # #         'Рейтинг': product_info.get('Рейтинг', ''),
# # #         'Количество отзывов': product_info.get('Количество отзывов', ''),
# # #         'Оригинальная цена': product_info.get('Оригинальная цена', ''),
# # #         'Стоимость доставки': product_info.get('Стоимость доставки', ''),
# # #         'Продавец': product_info.get('Продавец', ''),
# # #         'Опции товара': product_info.get('Опции товара', '')
# # #     }])

# # #     # Добавляем новую строку
# # #     df = pd.concat([df, new_product], ignore_index=True)

# # #     # Сохраняем обновленную таблицу в Excel
# # #     df.to_excel(EXCEL_FILE_PATH, index=False)
# # #     logger.info(f"Товар добавлен в таблицу: {new_product}")

# # # async def start(update: Update, context: CallbackContext) -> None:
# # #     logger.info("Command /start received")
# # #     await update.message.reply_text(
# # #         f"Привет! Я бот для парсинга ссылок и цен.\n"
# # #         f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке.\n"
# # #         f"Также можете просто отправить ссылку на товар с сайта coupang.com."
# # #     )

# # # async def check_coupang_link(update: Update, context: CallbackContext) -> None:
# # #     """Проверка ссылки на coupang.com и парсинг данных о товаре"""
# # #     message_text = update.message.text

# # #     # Регулярное выражение для поиска ссылок в сообщении
# # #     url_pattern = r'(https?://[^\s]+)'
# # #     urls = re.findall(url_pattern, message_text)

# # #     if urls:
# # #         for url in urls:
# # #             # Очищаем ссылку, убираем параметры после '?'
# # #             clean_product_url = clean_url(url)

# # #             # Проверяем, что это ссылка на coupang.com
# # #             if "coupang.com" in clean_product_url:
# # #                 await update.message.reply_text(f"Обнаружена ссылка на Coupang: {clean_product_url}")
# # #                 logger.info(f"Обнаружена ссылка на Coupang: {clean_product_url}")
                
# # #                 await update.message.reply_text("Начинаем парсинг страницы через браузер...")
# # #                 logger.info("Начинаем парсинг страницы через браузер...")

# # #                 # Создаем объект Parser для парсинга страницы через Selenium
# # #                 parser = Parser(clean_product_url)
# # #                 product_info = parser.parse_product_info()

# # #                 if product_info:
# # #                     response_text = "Информация о товаре:\n"
# # #                     for info_type, info in product_info.items():
# # #                         response_text += f"{info_type}: {info}\n"
                    
# # #                     # Добавляем информацию о товаре в таблицу
# # #                     add_product_to_excel(clean_product_url, product_info)

# # #                     # Отправляем сообщение с данными о товаре
# # #                     await update.message.reply_text(response_text)
# # #                     logger.info("Информация о товаре успешно отправлена в чат и добавлена в таблицу")
# # #                 else:
# # #                     await update.message.reply_text("Не удалось извлечь данные с указанной страницы.")
# # #                     logger.error("Не удалось извлечь данные с указанной страницы.")
# # #                 return
# # #             else:
# # #                 await update.message.reply_text("Пожалуйста, укажите ссылку на товар с сайта coupang.com.")
# # #                 logger.error("Ссылка не принадлежит coupang.com")
# # #     else:
# # #         await update.message.reply_text("Пожалуйста, отправьте ссылку для парсинга.")
# # #         logger.error("Сообщение не содержит ссылок")

# # # def main() -> None:
# # #     application = Application.builder().token(API_TOKEN).build()

# # #     # Add handlers for commands and messages
# # #     application.add_handler(CommandHandler("start", start))
# # #     application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start))
    
# # #     # Обрабатываем команду 'цена [URL]'
# # #     application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^цена '), check_coupang_link))

# # #     # Обрабатываем любые текстовые сообщения с проверкой на ссылку на coupang.com
# # #     application.add_handler(MessageHandler(filters.TEXT, check_coupang_link))

# # #     application.run_polling()

# # # if __name__ == '__main__':
# # #     main()
# # # bot.py
# # import logging
# # from telegram import Update
# # from telegram.ext import (
# #     Application,
# #     CommandHandler,
# #     MessageHandler,
# #     filters,
# #     CallbackContext,
# # )
# # import os
# # from dotenv import load_dotenv
# # import re
# # import pandas as pd
# # from parser import Parser  # Импортируем Parser из модуля parser

# # # Load environment variables from .env file
# # load_dotenv()

# # API_TOKEN = os.getenv('API_TOKEN')
# # BOT_USERNAME = os.getenv('BOT_USERNAME')

# # # Configure logging to log to a file
# # logging.basicConfig(
# #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# #     level=logging.INFO,
# #     handlers=[
# #         logging.FileHandler("bot.log"),
# #         logging.StreamHandler()
# #     ]
# # )

# # logger = logging.getLogger(__name__)

# # # Путь к файлу Excel для сохранения данных
# # EXCEL_FILE_PATH = 'orders.xlsx'

# # # Состояния для управления ботом
# # WAITING_FOR_ORDER = False
# # CURRENT_ORDER = {}

# # def clean_url(url):
# #     """Отсекаем все параметры после '?' в URL, чтобы получить чистую ссылку на товар"""
# #     clean_url = url.split('?')[0]  # Убираем все, что идет после '?'
# #     logger.info(f"Чистая ссылка на товар: {clean_url}")
# #     return clean_url

# # def add_order_to_excel(order):
# #     """Добавляем заказ в Excel"""
# #     # Проверяем, существует ли файл
# #     if os.path.exists(EXCEL_FILE_PATH):
# #         df = pd.read_excel(EXCEL_FILE_PATH)
# #     else:
# #         # Если файл не существует, создаем новый DataFrame
# #         df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Страна происхождения', 'Рейтинг', 'Количество отзывов', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

# #     # Создаем новую запись для таблицы
# #     new_order = pd.DataFrame([{
# #         'Ссылка': order['url'],
# #         'Количество': order['quantity'],
# #         'Опции': order['options'],
# #         'Название товара': order['product_info'].get('Название товара', ''),
# #         'Страна происхождения': order['product_info'].get('Страна происхождения', ''),
# #         'Рейтинг': order['product_info'].get('Рейтинг', ''),
# #         'Количество отзывов': order['product_info'].get('Количество отзывов', ''),
# #         'Оригинальная цена': order['product_info'].get('Оригинальная цена', ''),
# #         'Стоимость доставки': order['product_info'].get('Стоимость доставки', ''),
# #         'Продавец': order['product_info'].get('Продавец', '')
# #     }])

# #     # Добавляем новую строку
# #     df = pd.concat([df, new_order], ignore_index=True)

# #     # Сохраняем обновленную таблицу в Excel
# #     df.to_excel(EXCEL_FILE_PATH, index=False)
# #     logger.info(f"Заказ добавлен в таблицу: {new_order}")

# # async def start(update: Update, context: CallbackContext) -> None:
# #     logger.info("Command /start received")
# #     await update.message.reply_text(
# #         f"Привет! Я бот для парсинга ссылок и оформления заказов.\n"
# #         f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке.\n"
# #         f"Напишите '@{BOT_USERNAME} заказ' для добавления заказа."
# #     )

# # async def start_order(update: Update, context: CallbackContext) -> None:
# #     """Переход в режим получения данных для заказа"""
# #     global WAITING_FOR_ORDER
# #     WAITING_FOR_ORDER = True
# #     CURRENT_ORDER.clear()  # Очищаем текущий заказ
# #     await update.message.reply_text("Вы перешли в режим заказа. Отправьте ссылку на товар или напишите 'конец' для завершения.")
# #     logger.info("Бот перешел в режим получения заказа")

# # async def handle_order(update: Update, context: CallbackContext) -> None:
# #     """Обработка данных заказа: получение ссылки, количества и опций"""
# #     global WAITING_FOR_ORDER, CURRENT_ORDER
# #     message_text = update.message.text.lower()

# #     # Завершение режима заказа по команде 'конец'
# #     if message_text == 'конец':
# #         if os.path.exists(EXCEL_FILE_PATH):
# #             with open(EXCEL_FILE_PATH, 'rb') as file:
# #                 await update.message.reply_document(document=file, caption="Вот ваша таблица заказов.")
# #             logger.info("Таблица заказов отправлена")
# #         else:
# #             await update.message.reply_text("Таблица заказов пуста.")
# #             logger.info("Таблица заказов пуста")

# #         WAITING_FOR_ORDER = False
# #         CURRENT_ORDER.clear()
# #         return

# #     # Если еще нет ссылки в заказе, ждем ссылку
# #     if 'url' not in CURRENT_ORDER:
# #         # Проверка, является ли сообщение ссылкой
# #         url_pattern = r'(https?://[^\s]+)'
# #         urls = re.findall(url_pattern, message_text)
# #         if urls:
# #             clean_product_url = clean_url(urls[0])
# #             CURRENT_ORDER['url'] = clean_product_url
# #             await update.message.reply_text(f"Ссылка на товар получена: {clean_product_url}\nВведите количество.")
# #             logger.info(f"Ссылка на товар получена: {clean_product_url}")
# #         else:
# #             await update.message.reply_text("Пожалуйста, отправьте корректную ссылку на товар.")
# #         return

# #     # Если ссылка получена, ждем количество
# #     if 'quantity' not in CURRENT_ORDER:
# #         try:
# #             quantity = int(message_text)
# #             CURRENT_ORDER['quantity'] = quantity
# #             await update.message.reply_text(f"Количество товара: {quantity}\nВведите опции (или напишите 'нет', если их нет).")
# #             logger.info(f"Количество товара: {quantity}")
# #         except ValueError:
# #             await update.message.reply_text("Пожалуйста, введите корректное количество.")
# #         return

# #     # Если количество получено, ждем опции
# #     if 'options' not in CURRENT_ORDER:
# #         CURRENT_ORDER['options'] = message_text if message_text.lower() != 'нет' else 'Без опций'
# #         await update.message.reply_text(f"Опции товара: {CURRENT_ORDER['options']}\nНачинаем парсинг данных товара...")
# #         logger.info(f"Опции товара: {CURRENT_ORDER['options']}")

# #         # Начинаем парсинг данных о товаре
# #         parser = Parser(CURRENT_ORDER['url'])
# #         product_info = parser.parse_product_info()

# #         if product_info:
# #             CURRENT_ORDER['product_info'] = product_info
# #             # Добавляем данные в Excel
# #             add_order_to_excel(CURRENT_ORDER)
# #             await update.message.reply_text("Заказ успешно добавлен в таблицу.")
# #             logger.info("Заказ успешно добавлен в таблицу")
# #         else:
# #             await update.message.reply_text("Не удалось получить данные о товаре.")
# #             logger.error("Не удалось получить данные о товаре")

# #         # Выходим из режима заказа
# #         WAITING_FOR_ORDER = False
# #         CURRENT_ORDER.clear()
# #         return

# # async def handle_text(update: Update, context: CallbackContext) -> None:
# #     """Обработка текстовых сообщений вне режима заказа"""
# #     global WAITING_FOR_ORDER
# #     if not WAITING_FOR_ORDER:
# #         await update.message.reply_text("Пожалуйста, используйте команду '@имя_бота заказ', чтобы начать добавление заказа.")
# #     else:
# #         await handle_order(update, context)

# # def main() -> None:
# #     application = Application.builder().token(API_TOKEN).build()

# #     # Обработка команды /start
# #     application.add_handler(CommandHandler("start", start))
    
# #     # Переход в режим заказа
# #     application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start_order))

# #     # Обработка текста в режиме заказа
# #     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# #     application.run_polling()

# # if __name__ == '__main__':
# #     main()



# # bot.py
# import logging
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     CallbackContext,
# )
# import os
# from dotenv import load_dotenv
# import re
# import pandas as pd
# from parser import Parser  # Импортируем Parser из модуля parser

# # Load environment variables from .env file
# load_dotenv()

# API_TOKEN = os.getenv('API_TOKEN')
# BOT_USERNAME = os.getenv('BOT_USERNAME')

# # Configure logging to log to a file
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO,
#     handlers=[
#         logging.FileHandler("bot.log"),
#         logging.StreamHandler()
#     ]
# )

# logger = logging.getLogger(__name__)

# # Пути к файлам Excel
# EXCEL_FILE_PATH = 'orders.xlsx'
# SHIPPING_FILE_PATH = 'shipping.xlsx'

# # Состояния для управления ботом
# WAITING_FOR_ORDER = False
# CURRENT_ORDER = {}

# # Клавиатура с кнопками "нет" и "конец"
# order_keyboard = ReplyKeyboardMarkup(
#     [['нет', 'конец']],
#     one_time_keyboard=False,
#     resize_keyboard=True
# )

# def clean_url(url):
#     """Отсекаем все параметры после '?' в URL, чтобы получить чистую ссылку на товар"""
#     clean_url = url.split('?')[0]  # Убираем все, что идет после '?'
#     logger.info(f"Чистая ссылка на товар: {clean_url}")
#     return clean_url

# def add_order_to_excel(order):
#     """Добавляем заказ в Excel"""
#     # Проверяем, существует ли файл
#     if os.path.exists(EXCEL_FILE_PATH):
#         df = pd.read_excel(EXCEL_FILE_PATH)
#     else:
#         # Если файл не существует, создаем новый DataFrame
#         df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

#     # Создаем новую запись для таблицы заказов
#     new_order = pd.DataFrame([{
#         'Ссылка': order['url'],
#         'Количество': order['quantity'],
#         'Опции': order['options'],
#         'Название товара': order['product_info'].get('Название товара', ''),
#         'Оригинальная цена': order['product_info'].get('Оригинальная цена', ''),
#         'Стоимость доставки': order['product_info'].get('Стоимость доставки', ''),
#         'Продавец': order['product_info'].get('Продавец', '')
#     }])

#     # Добавляем новую строку в файл orders.xlsx
#     df = pd.concat([df, new_order], ignore_index=True)
#     df.to_excel(EXCEL_FILE_PATH, index=False)
#     logger.info(f"Заказ добавлен в таблицу: {new_order}")

#     # Формирование таблицы для shipping.xlsx
#     create_shipping_file()

# def create_shipping_file():
#     """Формируем таблицу для отправки товаров"""
#     if os.path.exists(EXCEL_FILE_PATH):
#         df = pd.read_excel(EXCEL_FILE_PATH)

#         # Берем только наименование товара и количество
#         shipping_df = df[['Название товара', 'Количество']]

#         # Сохраняем в файл shipping.xlsx
#         shipping_df.to_excel(SHIPPING_FILE_PATH, index=False)
#         logger.info("Таблица shipping.xlsx успешно создана")

# async def start(update: Update, context: CallbackContext) -> None:
#     logger.info("Command /start received")
#     await update.message.reply_text(
#         f"Привет! Я бот для парсинга ссылок и оформления заказов.\n"
#         f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке.\n"
#         f"Напишите '@{BOT_USERNAME} заказ' для добавления заказа."
#     )

# async def start_order(update: Update, context: CallbackContext) -> None:
#     """Переход в режим получения данных для заказа"""
#     global WAITING_FOR_ORDER
#     WAITING_FOR_ORDER = True
#     CURRENT_ORDER.clear()  # Очищаем текущий заказ
#     await update.message.reply_text(
#         "Вы перешли в режим заказа. Отправьте ссылку на товар или напишите 'конец' для завершения.",
#         reply_markup=order_keyboard
#     )
#     logger.info("Бот перешел в режим получения заказа")

# async def handle_order(update: Update, context: CallbackContext) -> None:
#     """Обработка данных заказа: получение ссылки, количества и опций"""
#     global WAITING_FOR_ORDER, CURRENT_ORDER
#     message_text = update.message.text.lower()

#     # Завершение режима заказа по команде 'конец'
#     if message_text == 'конец':
#         if os.path.exists(EXCEL_FILE_PATH):
#             # Отправляем файл orders.xlsx
#             with open(EXCEL_FILE_PATH, 'rb') as file:
#                 await update.message.reply_document(document=file, caption="Вот ваша таблица заказов.")

#             # Отправляем файл shipping.xlsx
#             if os.path.exists(SHIPPING_FILE_PATH):
#                 with open(SHIPPING_FILE_PATH, 'rb') as file:
#                     await update.message.reply_document(document=file, caption="Вот таблица для отправки товаров.")
#             logger.info("Таблицы orders.xlsx и shipping.xlsx отправлены")
#         else:
#             await update.message.reply_text("Таблица заказов пуста.")
#             logger.info("Таблица заказов пуста")

#         WAITING_FOR_ORDER = False
#         CURRENT_ORDER.clear()
#         return

#     # Если еще нет ссылки в заказе, ждем ссылку
#     if 'url' not in CURRENT_ORDER:
#         # Проверка, является ли сообщение ссылкой
#         url_pattern = r'(https?://[^\s]+)'
#         urls = re.findall(url_pattern, message_text)
#         if urls:
#             clean_product_url = clean_url(urls[0])
#             CURRENT_ORDER['url'] = clean_product_url
#             await update.message.reply_text(f"Ссылка на товар получена: {clean_product_url}\nВведите количество.", reply_markup=order_keyboard)
#             logger.info(f"Ссылка на товар получена: {clean_product_url}")
#         else:
#             await update.message.reply_text("Пожалуйста, отправьте корректную ссылку на товар.", reply_markup=order_keyboard)
#         return

#     # Если ссылка получена, ждем количество
#     if 'quantity' not in CURRENT_ORDER:
#         try:
#             quantity = int(message_text)
#             CURRENT_ORDER['quantity'] = quantity
#             await update.message.reply_text(f"Количество товара: {quantity}\nВведите опции (или нажмите 'нет', если их нет).", reply_markup=order_keyboard)
#             logger.info(f"Количество товара: {quantity}")
#         except ValueError:
#             await update.message.reply_text("Пожалуйста, введите корректное количество.", reply_markup=order_keyboard)
#         return

#     # Если количество получено, ждем опции
#     if 'options' not in CURRENT_ORDER:
#         CURRENT_ORDER['options'] = message_text if message_text.lower() != 'нет' else 'Без опций'
#         await update.message.reply_text(f"Опции товара: {CURRENT_ORDER['options']}\nНачинаем парсинг данных товара...", reply_markup=order_keyboard)
#         logger.info(f"Опции товара: {CURRENT_ORDER['options']}")

#         # Начинаем парсинг данных о товаре
#         parser = Parser(CURRENT_ORDER['url'])
#         product_info = parser.parse_product_info()

#         if product_info:
#             CURRENT_ORDER['product_info'] = product_info
#             # Добавляем данные в Excel
#             add_order_to_excel(CURRENT_ORDER)
#             await update.message.reply_text("Заказ успешно добавлен в таблицу.", reply_markup=order_keyboard)
#             logger.info("Заказ успешно добавлен в таблицу")
#         else:
#             await update.message.reply_text("Не удалось получить данные о товаре.", reply_markup=order_keyboard)
#             logger.error("Не удалось получить данные о товаре")

#         # Остаемся в режиме заказа
#         CURRENT_ORDER.clear()  # Очищаем данные для следующего заказа
#         return

# async def handle_text(update: Update, context: CallbackContext) -> None:
#     """Обработка текстовых сообщений вне режима заказа"""
#     global WAITING_FOR_ORDER
#     if not WAITING_FOR_ORDER:
#         await update.message.reply_text("Пожалуйста, используйте команду '@имя_бота заказ', чтобы начать добавление заказа.")
#     else:
#         await handle_order(update, context)

# def main() -> None:
#     application = Application.builder().token(API_TOKEN).build()

#     # Обработка команды /start
#     application.add_handler(CommandHandler("start", start))
    
#     # Переход в режим заказа
#     application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start_order))

#     # Обработка текста в режиме заказа
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

#     application.run_polling()

# if __name__ == '__main__':
#     main()



# bot.py
import logging
import os
import re
from datetime import datetime
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

# Клавиатура с кнопками "нет" и "конец"
order_keyboard = ReplyKeyboardMarkup(
    [['нет', 'конец']],
    one_time_keyboard=False,
    resize_keyboard=True
)

# Функция для генерации уникальных имен файлов на основе текущей даты
def generate_file_names():
    current_date = datetime.now().strftime('%Y-%m-%d')
    orders_file = f"order_{current_date}.xlsx"
    shipping_file = f"shipping_{current_date}.xlsx"
    return orders_file, shipping_file

# Состояния для управления ботом
WAITING_FOR_ORDER = False
CURRENT_ORDER = {}

def clean_url(url):
    """Отсекаем все параметры после '?' в URL, чтобы получить чистую ссылку на товар"""
    clean_url = url.split('?')[0]  # Убираем все, что идет после '?'
    logger.info(f"Чистая ссылка на товар: {clean_url}")
    return clean_url

def add_order_to_excel(order, orders_file):
    """Добавляем заказ в Excel"""
    # Проверяем, существует ли файл
    if os.path.exists(orders_file):
        df = pd.read_excel(orders_file)
    else:
        # Если файл не существует, создаем новый DataFrame
        df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

    # Создаем новую запись для таблицы заказов
    new_order = pd.DataFrame([{
        'Ссылка': order['url'],
        'Количество': order['quantity'],
        'Опции': order['options'],
        'Название товара': order['product_info'].get('Название товара', ''),
        'Оригинальная цена': order['product_info'].get('Оригинальная цена', ''),
        'Стоимость доставки': order['product_info'].get('Стоимость доставки', ''),
        'Продавец': order['product_info'].get('Продавец', '')
    }])

    # Добавляем новую строку в файл orders.xlsx
    df = pd.concat([df, new_order], ignore_index=True)
    df.to_excel(orders_file, index=False)
    logger.info(f"Заказ добавлен в таблицу: {new_order}")

    # Формирование таблицы для shipping.xlsx
    create_shipping_file(orders_file)

def create_shipping_file(orders_file):
    """Формируем таблицу для отправки товаров"""
    if os.path.exists(orders_file):
        df = pd.read_excel(orders_file)

        # Берем только наименование товара и количество
        shipping_df = df[['Название товара', 'Количество']]

        # Генерируем имя для файла shipping
        _, shipping_file = generate_file_names()

        # Сохраняем в файл shipping.xlsx
        shipping_df.to_excel(shipping_file, index=False)
        logger.info(f"Таблица {shipping_file} успешно создана")

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Command /start received")
    await update.message.reply_text(
        f"Привет! Я бот для парсинга ссылок и оформления заказов.\n"
        f"Напишите 'цена [URL]' чтобы получить цену товара по ссылке.\n"
        f"Напишите '@{BOT_USERNAME} заказ' для добавления заказа."
    )

async def start_order(update: Update, context: CallbackContext) -> None:
    """Переход в режим получения данных для заказа"""
    global WAITING_FOR_ORDER
    WAITING_FOR_ORDER = True
    CURRENT_ORDER.clear()  # Очищаем текущий заказ
    await update.message.reply_text(
        "Вы перешли в режим заказа. Отправьте ссылку на товар или напишите 'конец' для завершения.",
        reply_markup=order_keyboard
    )
    logger.info("Бот перешел в режим получения заказа")

async def handle_order(update: Update, context: CallbackContext) -> None:
    """Обработка данных заказа: получение ссылки, количества и опций"""
    global WAITING_FOR_ORDER, CURRENT_ORDER
    message_text = update.message.text.lower()

    # Завершение режима заказа по команде 'конец'
    if message_text == 'конец':
        # Генерируем уникальные имена файлов для orders.xlsx и shipping.xlsx
        orders_file, shipping_file = generate_file_names()

        if os.path.exists(orders_file):
            # Отправляем файл orders.xlsx
            with open(orders_file, 'rb') as file:
                await update.message.reply_document(document=file, caption="Вот ваша таблица заказов.")

            # Отправляем файл shipping.xlsx
            if os.path.exists(shipping_file):
                with open(shipping_file, 'rb') as file:
                    await update.message.reply_document(document=file, caption="Вот таблица для отправки товаров.")
            
            # Удаляем файлы после отправки
            os.remove(orders_file)
            os.remove(shipping_file)
            logger.info(f"Файлы {orders_file} и {shipping_file} успешно удалены после отправки")
        else:
            await update.message.reply_text("Таблица заказов пуста.")
            logger.info("Таблица заказов пуста")

        WAITING_FOR_ORDER = False
        CURRENT_ORDER.clear()
        return

    # Если еще нет ссылки в заказе, ждем ссылку
    if 'url' not in CURRENT_ORDER:
        # Проверка, является ли сообщение ссылкой
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, message_text)
        if urls:
            clean_product_url = clean_url(urls[0])
            CURRENT_ORDER['url'] = clean_product_url
            await update.message.reply_text(f"Ссылка на товар получена: {clean_product_url}\nВведите количество.", reply_markup=order_keyboard)
            logger.info(f"Ссылка на товар получена: {clean_product_url}")
        else:
            await update.message.reply_text("Пожалуйста, отправьте корректную ссылку на товар.", reply_markup=order_keyboard)
        return

    # Если ссылка получена, ждем количество
    if 'quantity' not in CURRENT_ORDER:
        try:
            quantity = int(message_text)
            CURRENT_ORDER['quantity'] = quantity
            await update.message.reply_text(f"Количество товара: {quantity}\nВведите опции (или нажмите 'нет', если их нет).", reply_markup=order_keyboard)
            logger.info(f"Количество товара: {quantity}")
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите корректное количество.", reply_markup=order_keyboard)
        return

    # Если количество получено, ждем опции
    if 'options' not in CURRENT_ORDER:
        CURRENT_ORDER['options'] = message_text if message_text.lower() != 'нет' else 'Без опций'
        await update.message.reply_text(f"Опции товара: {CURRENT_ORDER['options']}\nНачинаем парсинг данных товара...", reply_markup=order_keyboard)
        logger.info(f"Опции товара: {CURRENT_ORDER['options']}")

        # Начинаем парсинг данных о товаре
        parser = Parser(CURRENT_ORDER['url'])
        product_info = parser.parse_product_info()

        if product_info:
            CURRENT_ORDER['product_info'] = product_info

            # Генерируем уникальное имя файла для orders.xlsx
            orders_file, _ = generate_file_names()

            # Добавляем данные в Excel
            add_order_to_excel(CURRENT_ORDER, orders_file)
            await update.message.reply_text("Заказ успешно добавлен в таблицу.", reply_markup=order_keyboard)
            logger.info("Заказ успешно добавлен в таблицу")
        else:
            await update.message.reply_text("Не удалось получить данные о товаре.", reply_markup=order_keyboard)
            logger.error("Не удалось получить данные о товаре")

        # Остаемся в режиме заказа
        CURRENT_ORDER.clear()  # Очищаем данные для следующего заказа
        return

async def handle_text(update: Update, context: CallbackContext) -> None:
    """Обработка текстовых сообщений вне режима заказа"""
    global WAITING_FOR_ORDER
    if not WAITING_FOR_ORDER:
        await update.message.reply_text("Пожалуйста, используйте команду '@имя_бота заказ', чтобы начать добавление заказа.")
    else:
        await handle_order(update, context)

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Обработка команды /start
    application.add_handler(CommandHandler("start", start))
    
    # Переход в режим заказа
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start_order))

    # Обработка текста в режиме заказа
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()

if __name__ == '__main__':
    main()
