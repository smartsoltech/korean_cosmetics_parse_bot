import logging
from telegram import Update
from telegram.ext import CallbackContext

class CommandHandlerLogic:
    def __init__(self, order_manager, order_keyboard):
        self.order_manager = order_manager
        self.order_keyboard = order_keyboard
        self.logger = logging.getLogger(__name__)

    async def start_order(self, update: Update, context: CallbackContext) -> None:
        """Переход в режим заказа"""
        await self.order_manager.initiate_order_process(update, context)

    async def handle_uploaded_file(self, update: Update, context: CallbackContext) -> None:
        """Обработка загруженного файла"""
        try:
            await self.order_manager.process_uploaded_file(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при обработке файла: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке файла. Попробуйте снова или проверьте формат файла.")

    async def handle_text(self, update: Update, context: CallbackContext) -> None:
        """Обработка текстовых сообщений в режиме заказа"""
        try:
            if self.order_manager.waiting_for_order:
                await self.order_manager.process_order(update, context)
            else:
                await update.message.reply_text("ℹ️ Пожалуйста, используйте команду /заказ, чтобы начать добавление.")
        except Exception as e:
            self.logger.error(f"Ошибка при обработке текста: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке сообщения. Попробуйте снова.")

    async def supplement_order(self, update: Update, context: CallbackContext) -> None:
        """Дополнение заказа на основе загруженного файла"""
        try:
            await self.order_manager.supplement_order(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при дополнении заказа: {e}")
            await update.message.reply_text("❌ Произошла ошибка при дополнении заказа. Попробуйте снова.")

    async def generate_shipping_file(self, update: Update, context: CallbackContext) -> None:
        """Создание файла для транспортной компании на основе загруженного заказа"""
        try:
            await self.order_manager.generate_shipping_file(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при создании файла для транспортной компании: {e}")
            await update.message.reply_text("❌ Произошла ошибка при создании файла для транспортной компании. Попробуйте снова.")

    async def calculate_total_cost(self, update: Update, context: CallbackContext) -> None:
        """Подсчет общей стоимости товаров в заказе"""
        try:
            await self.order_manager.calculate_total_cost(update, context)
        except Exception as e:
            self.logger.error(f"Ошибка при подсчете общей стоимости: {e}")
            await update.message.reply_text("❌ Произошла ошибка при подсчете стоимости. Попробуйте снова.")