import logging
from telegram import Update
from telegram.ext import CallbackContext
from order_manager import OrderManager  # Подключаем наш класс OrderManager
from parser import Parser

# Инициализация клавиатур
order_keyboard = [['нет', 'конец']]
file_options_keyboard = [['Дополнить заказ', 'Сформировать ТН', 'Посчитать стоимость']]

# Создание экземпляра класса OrderManager
order_manager = OrderManager(order_keyboard=order_keyboard, file_options_keyboard=file_options_keyboard)

# Обработка команды для получения цены товара
async def handle_price(update: Update, context: CallbackContext):
    try:
        message_text = update.message.text
        if not message_text:
            await update.message.reply_text("Не удалось получить текст сообщения.")
            return

        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, message_text)

        if urls:
            product_url = urls[0]
            parser = Parser(product_url)  # Используем парсер для получения информации о товаре
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
    except Exception as e:
        logging.error(f"Ошибка при обработке команды 'цена': {e}")
        await update.message.reply_text("Произошла ошибка при обработке команды.")


# Обработка команды для начала заказа
async def start_order(update: Update, context: CallbackContext):
    try:
        await order_manager.initiate_order_process(update, context)
    except Exception as e:
        logging.error(f"Ошибка при начале заказа: {e}")
        await update.message.reply_text("Произошла ошибка при начале заказа.")

# Обработка текстовых сообщений для процесса заказа
async def handle_order(update: Update, context: CallbackContext):
    try:
        await order_manager.process_order(update, context)
    except Exception as e:
        logging.error(f"Ошибка при обработке заказа: {e}")
        await update.message.reply_text("Произошла ошибка при обработке заказа.")

# Обработка загруженного файла
async def handle_uploaded_file(update: Update, context: CallbackContext):
    try:
        await order_manager.process_uploaded_file(update, context)
    except Exception as e:
        logging.error(f"Ошибка при обработке загруженного файла: {e}")
        await update.message.reply_text("Произошла ошибка при обработке файла.")

# Обработка команды для дополнения заказа
async def supplement_order(update: Update, context: CallbackContext):
    try:
        await order_manager.supplement_order(update, context)
    except Exception as e:
        logging.error(f"Ошибка при дополнении заказа: {e}")
        await update.message.reply_text("Произошла ошибка при дополнении заказа.")

# Обработка команды для генерации файла для транспортной компании
async def generate_shipping_file(update: Update, context: CallbackContext):
    try:
        await order_manager.generate_shipping_file(update, context)
    except Exception as e:
        logging.error(f"Ошибка при генерации файла для транспортной компании: {e}")
        await update.message.reply_text("Произошла ошибка при генерации файла для транспортной компании.")

# Обработка команды для подсчета общей стоимости заказа
async def calculate_total_cost(update: Update, context: CallbackContext):
    try:
        await order_manager.calculate_total_cost(update, context)
    except Exception as e:
        logging.error(f"Ошибка при подсчете стоимости заказа: {e}")
        await update.message.reply_text("Произошла ошибка при подсчете стоимости заказа.")
