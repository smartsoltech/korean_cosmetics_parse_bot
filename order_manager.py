import os
import pandas as pd
import re
import random
import string
from telegram import Update
from telegram.ext import CallbackContext
import logging
from datetime import datetime, timedelta
from utility import Utils
import pytz

utils = Utils()

class OrderManager:
    def __init__(self, order_keyboard, file_options_keyboard):
        self.order_keyboard = order_keyboard
        self.file_options_keyboard = file_options_keyboard
        self.current_order = {}
        self.waiting_for_order = False
        self.income_folder = "/usr/src/app/income"
        self.outcome_folder = "/usr/src/app/outcome"
        self.order_file_path = None
        self.shipping_file_path = None

        # Create folders if they don't exist
        os.makedirs(self.income_folder, exist_ok=True)
        os.makedirs(self.outcome_folder, exist_ok=True)

    async def initiate_order_process(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        existing_order_file = self.find_existing_order_file(chat_id)

        if existing_order_file:
            await update.message.reply_text(
                "⚠️ У вас уже есть активная заявка, созданная менее 2 дней назад. Хотите изменить её? (да/нет)"
            )
            context.user_data['existing_order_file'] = existing_order_file
            self.waiting_for_order = False
        else:
            self.start_new_order(chat_id)
            await update.message.reply_text("✉️ Введите ссылку на товар.", reply_markup=self.order_keyboard)

    def start_new_order(self, chat_id):
        self.waiting_for_order = True
        self.current_order.clear()
        self.order_file_path = self.generate_order_file(chat_id)
        self.shipping_file_path = self.generate_shipping_file(chat_id)

    def find_existing_order_file(self, chat_id):
        for file_name in os.listdir(self.outcome_folder):
            if str(chat_id) in file_name:
                file_path = os.path.join(self.outcome_folder, file_name)
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if datetime.now() - file_mod_time <= timedelta(days=2):
                    return file_path
        return None

    async def process_order(self, update: Update, context: CallbackContext):
        message_text = update.message.text.strip()
        logging.info(f"Получено сообщение: {message_text}")

        if message_text.lower() == 'да' and 'existing_order_file' in context.user_data:
            self.order_file_path = context.user_data['existing_order_file']
            self.shipping_file_path = self.order_file_path.replace('order_', 'shipping_')
            self.waiting_for_order = True
            await update.message.reply_text("✉️ Вы можете продолжить добавление товаров в существующую заявку.")
            return
        elif message_text.lower() == 'нет' and 'existing_order_file' in context.user_data:
            os.remove(context.user_data['existing_order_file'])
            self.start_new_order(update.effective_chat.id)
            await update.message.reply_text("🗑️ Старая заявка удалена. ✉️ Введите ссылку на товар.", reply_markup=self.order_keyboard)
            return

        # Step by step input process
        if message_text.lower() == 'конец':
            await self.finalize_order(update)
            return

        if 'url' not in self.current_order:
            urls = re.findall(r'(https?://[^\s]+)', message_text)
            logging.info(f"Найдены ссылки: {urls}")

            if urls:
                self.current_order['url'] = urls[0]
                logging.info(f"Ссылка успешно сохранена: {self.current_order['url']}")
                await update.message.reply_text("✉️ Ссылка получена. Введите количество.")
            else:
                logging.error("Ошибка: Ссылка на товар не найдена в сообщении.")
                await update.message.reply_text("⚠️ Неверная ссылка. Пожалуйста, попробуйте снова.")
        elif 'quantity' not in self.current_order:
            try:
                quantity = int(message_text)
                self.current_order['quantity'] = quantity
                logging.info(f"Количество сохранено: {quantity}")
                await update.message.reply_text("✅ Количество принято. Пожалуйста, введите цену.")
            except ValueError:
                logging.error(f"Ошибка: {message_text} не является числом.")
                await update.message.reply_text("⚠️ Пожалуйста, введите корректное количество (число).")
        elif 'price' not in self.current_order:
            try:
                price = float(message_text)
                self.current_order['price'] = price
                logging.info(f"Цена сохранена: {price}")
                await update.message.reply_text("✅ Цена принята. Пожалуйста, введите название товара.")
            except ValueError:
                logging.error(f"Ошибка: {message_text} не является числом.")
                await update.message.reply_text("⚠️ Пожалуйста, введите корректную цену (число).")
        elif 'name' not in self.current_order:
            self.current_order['name'] = message_text
            logging.info(f"Название товара сохранено: {message_text}")
            await update.message.reply_text("✅ Название товара принято. Пожалуйста, введите опции товара (например, цвет, размер и т.д.).")
        elif 'options' not in self.current_order:
            self.current_order['options'] = message_text
            logging.info(f"Опции товара сохранены: {message_text}")
            await self.add_order(update)
            await update.message.reply_text("✅ Товар добавлен. Введите новый товар или напишите 'конец' для завершения заказа.")

    async def add_order(self, update: Update):
        if len(self.current_order) >= 5:
            self.save_order_to_file()
            self.save_shipping_file()
            self.current_order.clear()
        else:
            await update.message.reply_text("⚠️ Недостаточно данных для сохранения товара. Пожалуйста, введите все необходимые данные.")

    async def finalize_order(self, update: Update):
        if self.order_file_path and os.path.exists(self.order_file_path):
            await update.message.reply_text("✅ Заказ завершен и сохранен. Используйте команду /order, чтобы начать новый заказ.")

            with open(self.order_file_path, 'rb') as file:
                await update.message.reply_document(document=file, filename=os.path.basename(self.order_file_path))
            if self.shipping_file_path and os.path.exists(self.shipping_file_path):
                with open(self.shipping_file_path, 'rb') as file:
                    await update.message.reply_document(document=file, filename=os.path.basename(self.shipping_file_path))
        else:
            await update.message.reply_text("⚠️ Нет заказов для завершения. Пожалуйста, добавьте товары.")

    def save_order_to_file(self):
        if not self.order_file_path:
            return

        if not os.path.exists(self.order_file_path):
            logging.info(f"Файл {self.order_file_path} не существует, создаем новый.")
            df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Цена', 'Название', 'Опции'])
        else:
            df = pd.read_excel(self.order_file_path)

        new_order = pd.DataFrame([{
            'Ссылка': self.current_order.get('url', ''),
            'Количество': self.current_order.get('quantity', ''),
            'Цена': self.current_order.get('price', ''),
            'Название': self.current_order.get('name', ''),
            'Опции': self.current_order.get('options', '')
        }])

        df = pd.concat([df, new_order], ignore_index=True)
        df.to_excel(self.order_file_path, index=False)
        logging.info(f"Заказ успешно добавлен в файл: {self.order_file_path}")

    def save_shipping_file(self):
        if not self.shipping_file_path:
            return

        if not os.path.exists(self.shipping_file_path):
            logging.info(f"Файл {self.shipping_file_path} не существует, создаем новый.")
            df = pd.DataFrame(columns=['Название', 'Количество', 'Цена'])
        else:
            df = pd.read_excel(self.shipping_file_path)

        new_order = pd.DataFrame([{
            'Название': self.current_order.get('name', ''),
            'Количество': self.current_order.get('quantity', ''),
            'Цена': self.current_order.get('price', '')
        }])

        df = pd.concat([df, new_order], ignore_index=True)
        df.to_excel(self.shipping_file_path, index=False)
        logging.info(f"Файл для транспортной компании успешно добавлен: {self.shipping_file_path}")

    def generate_order_file(self, chat_id):
        tz = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return os.path.join(self.outcome_folder, f"order_{chat_id}_{random_code}_{current_time}.xlsx")

    def generate_shipping_file(self, chat_id):
        tz = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return os.path.join(self.outcome_folder, f"shipping_{chat_id}_{random_code}_{current_time}.xlsx")