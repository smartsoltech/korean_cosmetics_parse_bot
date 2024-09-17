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
        if message_text == 'дополнить заказ':
            logger.info("Дополняем заказ на основе загруженного файла")
            await update.message.reply_text("Вы перешли в режим дополнения заказа. Пожалуйста, добавьте ссылки и параметры.", reply_markup=order_keyboard)
            WAITING_FOR_ORDER = True  # Активируем режим добавления заказа
            WAITING_FOR_ACTION = False
            return  # Переход сразу в режим получения данных
        elif message_text == 'сформировать тн':
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
            clean
