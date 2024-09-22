import os
import pandas as pd
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from parser import Parser
import logging
from datetime import datetime
from shutil import move
from utility import Utils  # Импортируем новый класс Utils для очистки папок
import pytz

utils = Utils()

class OrderManager:
    def __init__(self, order_keyboard, file_options_keyboard, parse_mode="auto"):
        self.order_keyboard = order_keyboard
        self.file_options_keyboard = file_options_keyboard
        self.current_order = {}
        self.waiting_for_order = False
        self.income_folder = "/usr/src/app/income"
        self.outcome_folder = "/usr/src/app/outcome"
        self.order_file_path = None
        self.parse_mode = parse_mode  # Добавляем опцию режима парсинга

        # Создаем папки, если их нет
        if not os.path.exists(self.income_folder):
            os.makedirs(self.income_folder)
        if not os.path.exists(self.outcome_folder):
            os.makedirs(self.outcome_folder)

    def generate_order_file(self):
        """Генерация уникального имени для файла заказов с таймштампом."""
        tz = pytz.timezone('Asia/Seoul')  # Задайте свою временную зону
        current_time = datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')
        return os.path.join(self.outcome_folder, f"order_{current_time}.xlsx")

    async def process_order(self, update: Update, context: CallbackContext):
        """Обработка нового заказа и сохранение в уже существующий файл."""
        message_text = update.message.text.lower()

        if message_text == 'конец':
            await self.finalize_order(update)
            return

        if 'url' not in self.current_order:
            urls = re.findall(r'(https?://[^\s]+)', message_text)
            if urls:
                self.current_order['url'] = urls[0]
                await update.message.reply_text("Ссылка получена. Введите количество.")
            else:
                await update.message.reply_text("Неверная ссылка. Попробуйте снова.")
        elif 'quantity' not in self.current_order:
            try:
                quantity = int(message_text)
                self.current_order['quantity'] = quantity
                await update.message.reply_text("Введите опции или нажмите 'нет'.")
            except ValueError:
                await update.message.reply_text("Введите корректное количество.")
        elif 'options' not in self.current_order:
            self.current_order['options'] = message_text if message_text != 'нет' else 'Без опций'
            await update.message.reply_text("Опции товара добавлены. Выберите режим работы.")

            # Клавиатура выбора режима работы
            keyboard = [["Автоматический ввод", "Ручной ввод"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text("Выберите режим ввода:", reply_markup=reply_markup)

    async def manual_input_mode(self, update: Update, context: CallbackContext):
        """Ручной ввод данных о товаре."""
        await update.message.reply_text("Введите ссылку на товар:")
        self.current_order['manual_input'] = True  # Указываем, что идет ручной ввод данных
        context.user_data['step'] = 'input_url'

    async def handle_manual_input(self, update: Update, context: CallbackContext):
        """Обрабатывает шаги ручного ввода товара."""
        message_text = update.message.text
        step = context.user_data.get('step', None)

        # Ввод ссылки на товар
        if step == 'input_url':
            urls = re.findall(r'(https?://[^\s]+)', message_text)
            if urls:
                self.current_order['url'] = urls[0]
                await update.message.reply_text("Введите название товара:")
                context.user_data['step'] = 'input_name'
            else:
                await update.message.reply_text("Неверная ссылка. Попробуйте снова.")

        # Ввод названия товара
        elif step == 'input_name':
            self.current_order['product_info'] = {'Название товара': message_text}
            await update.message.reply_text("Введите цену товара:")
            context.user_data['step'] = 'input_price'

        # Ввод цены товара
        elif step == 'input_price':
            self.current_order['product_info']['Оригинальная цена'] = message_text
            await update.message.reply_text("Данные о товаре успешно добавлены.")

            # Сохранение данных заказа в файл
            self.save_order_to_file(update)

            # Очищаем данные текущего заказа и продолжаем ожидание новых данных
            self.current_order.clear()

            await update.message.reply_text(
                "Заказ успешно добавлен. Введите ссылку на новый товар или завершите ввод командой 'конец'.", 
                reply_markup=self.order_keyboard
            )

            # Сброс шага
            context.user_data['step'] = None

    async def try_parsing_product(self, update: Update):
        """Попытка распарсить данные товара с помощью парсера."""
        try:
            parser = Parser(self.current_order['url'])
            product_info = parser.parse_product_info()
            if product_info:
                return product_info
        except Exception as e:
            logging.error(f"Ошибка при парсинге товара: {e}")
            await update.message.reply_text(f"Ошибка при парсинге товара: {e}")
        return None

    async def process_automatic_or_manual(self, update: Update, context: CallbackContext):
        """Обработка выбора между автоматическим и ручным вводом."""
        message_text = update.message.text.lower()

        if message_text == "автоматический ввод":
            product_info = await self.try_parsing_product(update)
            if product_info:
                self.current_order['product_info'] = product_info
                await update.message.reply_text(f"Товар добавлен: {product_info.get('Название товара', 'Неизвестно')}.")
                self.save_order_to_file(update)
            else:
                await update.message.reply_text("Не удалось получить данные о товаре автоматически. Переключаемся на ручной ввод.")
                await self.manual_input_mode(update, context)

        elif message_text == "ручной ввод":
            await self.manual_input_mode(update, context)

    def save_order_to_file(self, update: Update):
        """Сохранение заказа в уже существующий или новый файл."""
        if not self.order_file_path:
            self.order_file_path = self.generate_order_file()

        # Проверяем, существует ли файл, если нет - создаем новый DataFrame
        if not os.path.exists(self.order_file_path):
            logging.info(f"Файл {self.order_file_path} не существует, создаем новый.")
            df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена'])
        else:
            df = pd.read_excel(self.order_file_path)

        # Создаем новую запись для таблицы заказов
        new_order = pd.DataFrame([{
            'Ссылка': self.current_order['url'],
            'Количество': self.current_order['quantity'],
            'Опции': self.current_order['options'],
            'Название товара': self.current_order['product_info'].get('Название товара', ''),
            'Оригинальная цена': self.current_order['product_info'].get('Оригинальная цена', '')
        }])

        # Добавляем новую строку к существующим данным
        df = pd.concat([df, new_order], ignore_index=True)

        # Сохраняем изменения
        df.to_excel(self.order_file_path, index=False)
        logging.info(f"Заказ успешно добавлен в файл: {self.order_file_path}")
        
    async def initiate_order_process(self, update: Update, context: CallbackContext):
        self.waiting_for_order = True
        self.current_order.clear()
        await update.message.reply_text("Введите ссылку на товар.", reply_markup=self.order_keyboard)
        
    async def finalize_order(self, update: Update):
        """Завершение режима заказа и отправка файла с заказом."""
        if self.order_file_path and os.path.exists(self.order_file_path):
            await update.message.reply_document(document=open(self.order_file_path, 'rb'), caption="Вот ваш файл заказов.")
        else:
            await update.message.reply_text("Файл заказов не найден.")

    async def supplement_order(self, update: Update, context: CallbackContext):
        """Дополнение заказа на основе загруженного файла."""
        if not self.order_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        # Дополнение текущего файла заказа новыми товарами
        self.waiting_for_order = True
        await update.message.reply_text("Теперь вы можете добавлять новые заказы.", reply_markup=self.order_keyboard)
