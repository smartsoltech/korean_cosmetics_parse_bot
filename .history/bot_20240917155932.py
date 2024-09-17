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
import threading
from .watchdog import start_watchdog, path

def run_watchdog():
    """Функция для запуска watchdog в отдельном потоке"""
    start_watchdog(path)
    
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

# Клавиатура для загруженного файла
file_options_keyboard = ReplyKeyboardMarkup(
    [['Дополнить заказ', 'Сформировать ТН']],
    one_time_keyboard=False,
    resize_keyboard=True
)

# Состояния для управления ботом
WAITING_FOR_ORDER = False
CURRENT_ORDER = {}
LOADED_FILE = None  # Переменная для хранения загруженного файла
WAITING_FOR_ACTION = False  # Переменная для отслеживания состояния после загрузки файла

# Функция для генерации уникальных имен файлов на основе текущей даты
def generate_file_names():
    current_date = datetime.now().strftime('%Y-%m-%d')
    orders_file = f"order_{current_date}.xlsx"
    shipping_file = f"shipping_{current_date}.xlsx"
    return orders_file, shipping_file

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

async def handle_price(update: Update, context: CallbackContext) -> None:
    """Обработка команды 'цена [URL]' для получения информации о товаре"""
    message_text = update.message.text
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, message_text)

    if urls:
        clean_product_url = clean_url(urls[0])
        logger.info(f"Парсинг информации о товаре по ссылке: {clean_product_url}")
        parser = Parser(clean_product_url)
        product_info = parser.parse_product_info()

        if product_info:
            response_message = (
                f"Название товара: {product_info.get('Название товара', 'Неизвестно')}\n"
                f"Оригинальная цена: {product_info.get('Оригинальная цена', 'Неизвестно')}\n"
                f"Стоимость доставки: {product_info.get('Стоимость доставки', 'Неизвестно')}\n"
                f"Продавец: {product_info.get('Продавец', 'Неизвестно')}"
            )
            await update.message.reply_text(response_message)
        else:
            await update.message.reply_text("Не удалось получить информацию о товаре.")
    else:
        await update.message.reply_text("Пожалуйста, отправьте корректную ссылку.")

async def start_order(update: Update, context: CallbackContext) -> None:
    """Переход в режим получения данных для заказа"""
    global WAITING_FOR_ORDER, WAITING_FOR_ACTION
    WAITING_FOR_ORDER = True
    WAITING_FOR_ACTION = False  # Сбрасываем, если было ожидание действия после загрузки файла
    CURRENT_ORDER.clear()  # Очищаем текущий заказ
    await update.message.reply_text(
        "Вы перешли в режим заказа. Отправьте ссылку на товар или напишите 'конец' для завершения.",
        reply_markup=order_keyboard
    )
    logger.info("Бот перешел в режим получения заказа")

async def handle_order(update: Update, context: CallbackContext) -> None:
    """Обработка данных заказа: получение ссылки, количества и опций"""
    global WAITING_FOR_ORDER, CURRENT_ORDER, LOADED_FILE, WAITING_FOR_ACTION
    message_text = update.message.text.lower()

    # Проверка на ожидание действия после загрузки файла
    if WAITING_FOR_ACTION:
        if message_text.lower() == 'дополнить заказ':
            logger.info("Дополняем заказ на основе загруженного файла")
            await update.message.reply_text("Вы перешли в режим дополнения заказа. Пожалуйста, добавьте ссылки и параметры.", reply_markup=order_keyboard)
            WAITING_FOR_ORDER = True  # Активируем режим добавления заказа
            WAITING_FOR_ACTION = False
            return  # Переход сразу в режим получения данных
        elif message_text.lower() == 'сформировать тн':
            logger.info("Формируем ТН на основе загруженного файла")
            orders_file, shipping_file = generate_file_names()
            if LOADED_FILE:
                df = pd.read_excel(LOADED_FILE)
                df.to_excel(orders_file, index=False)  # Сохраняем загруженные данные
                create_shipping_file(orders_file)
                # Отправляем файл shipping.xlsx
                with open(shipping_file, 'rb') as file:
                    await update.message.reply_document(document=file, caption="Вот таблица для отправки товаров.")
                # Удаляем файлы после отправки
                os.remove(orders_file)
                os.remove(shipping_file)
                logger.info(f"Файлы {orders_file} и {shipping_file} успешно удалены после отправки")
                LOADED_FILE = None
            WAITING_FOR_ACTION = False
            return

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
        LOADED_FILE = None
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

            # Если был загружен файл, переносим его данные
            if LOADED_FILE:
                loaded_data = pd.read_excel(LOADED_FILE)
                loaded_data.to_excel(orders_file, index=False)
                LOADED_FILE = None  # Сбрасываем после переноса

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

async def handle_uploaded_file(update: Update, context: CallbackContext) -> None:
    """Обработка загруженного файла Excel"""
    global LOADED_FILE, WAITING_FOR_ACTION
    document = update.message.document

    # Сохраняем файл
    file = await document.get_file()
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    try:
        # Проверяем, соответствует ли структура файла ожидаемой
        df = pd.read_excel(file_path)
        required_columns = ['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец']
        
        if all(col in df.columns for col in required_columns):
            LOADED_FILE = file_path  # Сохраняем путь к файлу
            WAITING_FOR_ACTION = True  # Включаем ожидание выбора действия
            await update.message.reply_text("Файл успешно загружен. Выберите действие:", reply_markup=file_options_keyboard)
        else:
            await update.message.reply_text("Файл не соответствует ожидаемой структуре.")
    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await update.message.reply_text("Произошла ошибка при обработке файла.")

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
    
    # Обработка команды 'цена [URL]'
    application.add_handler(MessageHandler(filters.Regex(r'^цена\s+https?://'), handle_price))

    # Переход в режим заказа
    application.add_handler(MessageHandler(filters.Regex(f'@{BOT_USERNAME} заказ'), start_order))

    # Обработка загрузки файлов Excel
    application.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), handle_uploaded_file))

    # Обработка текста в режиме заказа
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()

if __name__ == '__main__':
    main()
