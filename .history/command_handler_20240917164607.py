import logging
from telegram import Update
from telegram.ext import CallbackContext
from parser import Parser

class CommandHandlerLogic:
    def __init__(self, order_manager, order_keyboard):
        self.order_manager = order_manager
        self.order_keyboard = order_keyboard
        self.logger = logging.getLogger(__name__)

    async def start_order(self, update: Update, context: CallbackContext) -> None:
        """Переход в режим заказа"""
        await self.order_manager.initiate_order_process(update, context)

    async def handle_price(self, update: Update, context: CallbackContext) -> None:
        """Парсинг цены по ссылке"""
        message_text = update.message.text
        urls = re.findall(r'(https?://[^\s]+)', message_text)

        if urls:
            url = urls[0]
            parser = Parser(url)
            product_info = parser.parse_product_info()
            if product_info:
                await update.message.reply_text(
                    f"Название товара: {product_info['Название товара']}\n"
                    f"Цена: {product_info['Оригинальная цена']}\n"
                    f"Доставка: {product_info['Стоимость доставки']}"
                )
            else:
                await update.message.reply_text("Не удалось получить данные о товаре.")
        else:
            await update.message.reply_text("Пожалуйста, отправьте корректную ссылку.")

    async def handle_uploaded_file(self, update: Update, context: CallbackContext) -> None:
        """Обработка загруженного файла"""
        await self.order_manager.process_uploaded_file(update, context)

    async def handle_text(self, update: Update, context: CallbackContext) -> None:
        """Обработка текстовых сообщений в режиме заказа"""
        if self.order_manager.waiting_for_order:
            await self.order_manager.process_order(update, context)
        else:
            await update.message.reply_text("Пожалуйста, используйте команду /заказ, чтобы начать добавление.")
