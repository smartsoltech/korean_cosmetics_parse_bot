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

    async def handle_price(self, update: Update, context: CallbackContext) -> None:
        """Парсинг цены по ссылке"""
        try:
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
        except Exception as e:
            self.logger.error(f"Ошибка при обработке цены: {e}")
            await update.message.reply_text("Произошла ошибка при обработке ссылки.")

    async def handle_uploaded_file(self, update: Update, context: CallbackContext) -> None:
        """Обработка загруженного файла"""
        print("handle_uploaded_file called")
        print("update", update)
        print("context", context)
        try:
            await self.order_manager.process_uploaded_file(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при обработке файла: {e}")
            print(f"Error occurred: {e}")
            await update.message.reply_text("Произошла ошибка при обработке файла.")

    async def handle_text(self, update: Update, context: CallbackContext) -> None:
        """Обработка текстовых сообщений в режиме заказа"""
        print("handle_text called")
        print("update", update)
        print("context", context)
        print("waiting_for_order", self.order_manager.waiting_for_order)
        try:
            if self.order_manager.waiting_for_order:
                print("processing order")
                await self.order_manager.process_order(update, context)
            else:
                print("not waiting for order")
                await update.message.reply_text("Пожалуйста, используйте команду /заказ, чтобы начать добавление.")
        except Exception as e:
            print("error occurred:", e)
            self.logger.error(f"Ошибка при обработке текста бла бла бла: {e}")
            await update.message.reply_text("Произошла ошибка при обработке сообщения.")

    async def supplement_order(self, update: Update, context: CallbackContext) -> None:
        """Дополнение заказа на основе загруженного файла"""
        try:
            await self.order_manager.supplement_order(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при дополнении заказа: {e}")
            await update.message.reply_text("Произошла ошибка при дополнении заказа.")

    async def generate_shipping_file(self, update: Update, context: CallbackContext) -> None:
        """Создание файла для транспортной компании на основе загруженного заказа"""
        try:
            await self.order_manager.generate_shipping_file(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при создании файла для транспортной компании: {e}")
            await update.message.reply_text("Произошла ошибка при создании файла для транспортной компании.")

    async def calculate_total_cost(self, update: Update, context: CallbackContext) -> None:
        """Подсчет общей стоимости товаров в заказе"""
        try:
            await self.order_manager.calculate_total_cost(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при подсчете общей стоимости: {e}")
            await update.message.reply_text("Произошла ошибка при подсчете стоимости.")
