import logging
from telegram import Update
from telegram.ext import CallbackContext
from parser import Parser
import re


class CommandHandlerLogic:
    def __init__(self, order_manager, order_keyboard):
        self.order_manager = order_manager
        self.order_keyboard = order_keyboard
        self.logger = logging.getLogger(__name__)

    async def start_order(self, update: Update, context: CallbackContext) -> None:
        """Переход в режим заказа"""
        await self.order_manager.initiate_order_process(update, context)

async def handle_price(update: Update, context: CallbackContext) -> None:
    # Проверяем, содержит ли обновление текстовое сообщение
    if update.message and update.message.text:
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
    else:
        logger.error("Полученное обновление не содержит текстового сообщения.")

    async def handle_uploaded_file(self, update: Update, context: CallbackContext) -> None:
        """Обработка загруженного файла"""
        await self.order_manager.process_uploaded_file(update, context)

    async def handle_text(self, update: Update, context: CallbackContext) -> None:
        """Обработка текстовых сообщений в режиме заказа"""
        if self.order_manager.waiting_for_order:
            await self.order_manager.process_order(update, context)
        else:
            await update.message.reply_text("Пожалуйста, используйте команду /заказ, чтобы начать добавление.")
