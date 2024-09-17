import os
import pandas as pd
import re
from telegram import Update
from telegram.ext import CallbackContext
from parser import Parser
import logging
from datetime import datetime
from shutil import move
from utility import Utils  # Импортируем новый класс Utils для очистки папок
import pytz

class OrderManager:
    def __init__(self, order_keyboard, file_options_keyboard):
        self.order_keyboard = order_keyboard
        self.file_options_keyboard = file_options_keyboard
        self.current_order = {}
        self.waiting_for_order = False
        self.income_folder = "/usr/src/app/income"
        self.outcome_folder = "/usr/src/app/outcome"
        self.order_file_path = None  # Путь к файлу заказа
        
        utils = Utils()
        
        # Создаем папки, если их нет
        if not os.path.exists(self.income_folder):
            os.makedirs(self.income_folder)
        if not os.path.exists(self.outcome_folder):
            os.makedirs(self.outcome_folder)
    
    def move_file_to_outcome(self):
        """Перемещение файла из папки 'income' в папку 'outcome'."""
        if not self.order_file_path:
            raise FileNotFoundError("Файл заказа не был загружен.")

        # Указываем исходный и целевой путь
        source_dir = 'income'
        target_dir = 'outcome'

        # Создаем директорию 'outcome', если она не существует
        os.makedirs(target_dir, exist_ok=True)

        # Получаем имя файла и создаем полный путь для перемещения
        file_name = os.path.basename(self.order_file_path)
        target_file_path = os.path.join(target_dir, file_name)

        # Перемещаем файл
        move(self.order_file_path, target_file_path)

        # Обновляем путь к файлу на новый, в папке 'outcome'
        self.order_file_path = target_file_path
        print(f"Файл перемещен в папку outcome: {target_file_path}")
        
    def generate_order_file(self):
        """Генерация уникального имени для файла заказов с таймштампом."""
        tz = pytz.timezone('Asia/Seoul')  # Задайте свою временную зону
        current_time = datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')
        return os.path.join(self.outcome_folder, f"order_{current_time}.xlsx")

    def generate_shipping_filename(self):
        """Генерация уникального имени для файла shipping с таймштампом."""
        tz = pytz.timezone('Asia/Seoul')  # Задайте свою временную зону
        current_time = datetime.now(tz).strftime('%Y-%m-%d_%H-%M-%S')
        return os.path.join(self.outcome_folder, f"shipping_{current_time}.xlsx")

    
    async def generate_shipping_file(self, update: Update, context: CallbackContext):
        """Генерация ТН на основе заказа."""
        if not self.order_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        df = pd.read_excel(self.order_file_path)
        shipping_df = df[['Название товара', 'Количество']]

        shipping_file = self.generate_shipping_filename()
        shipping_df.to_excel(shipping_file, index=False)

        await update.message.reply_document(document=open(shipping_file, 'rb'), caption="Вот ваш файл для транспортной компании.")

        # Перемещаем файл в папку outcome
        self.move_file_to_outcome()

    async def finalize_order(self, update: Update):
        """Завершение режима заказа и отправка файла с заказом."""
        if self.order_file_path and os.path.exists(self.order_file_path):
            
            print(self.order_file_path)
            print(f'--------Вызов self.generate_shipping_filename')
            shipping_file = self.generate_shipping_filename()

            # Создаем файл для транспортной компании
            self.create_shipping_file(self.order_file_path)
            print(shipping_file)
            # Отправляем файл заказов
            await update.message.reply_document(document=open(self.order_file_path, 'rb'), caption="Вот ваш файл заказов.")

            # Отправляем файл для транспортной компании
            await update.message.reply_document(document=open(shipping_file, 'rb'), caption="Вот ваш файл для отправки товаров.")
            
            # После отправки очищаем папки 'income' и 'outcome'
  
            utils.clear_dirs(self.income_folder)
            utils.clear_dirs(self.outcome_folder)

        else:
            await update.message.reply_text("Файл заказов не найден.")
    async def initiate_order_process(self, update: Update, context):
        self.waiting_for_order = True
        self.current_order.clear()
        await update.message.reply_text("Введите ссылку на товар.", reply_markup=self.order_keyboard)

    async def process_uploaded_file(self, update: Update, context):
        """Обработка загруженного файла."""
        document = update.message.document
        file = await document.get_file()
        file_name = f"{self.income_folder}/{document.file_name}"
        await file.download_to_drive(file_name)

        try:
            df = pd.read_excel(file_name)
            required_columns = ['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец']

            if all(col in df.columns for col in required_columns):
                # Переносим файл из income в outcome
                new_file_name = os.path.join(self.outcome_folder, document.file_name)
                move(file_name, new_file_name)

                self.order_file_path = new_file_name  # Устанавливаем путь к загруженному файлу
                await update.message.reply_text("Файл успешно загружен. Выберите действие.", reply_markup=self.file_options_keyboard)
            else:
                await update.message.reply_text("Файл не соответствует ожидаемой структуре.")
        except Exception as e:
            logging.error(f"Ошибка при обработке файла: {e}")
            await update.message.reply_text(f"Ошибка при обработке файла: {e}")

    async def supplement_order(self, update: Update, context):
        """Дополнение заказа на основе загруженного файла."""
        if not self.order_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        # Дополнение текущего файла заказа новыми товарами
        self.waiting_for_order = True
        await update.message.reply_text("Теперь вы можете добавлять новые заказы.", reply_markup=self.order_keyboard)

    async def process_order(self, update: Update, context):
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
            await update.message.reply_text("Опции товара добавлены. Начинаем парсинг данных товара...")

            # Начало парсинга данных товара
            parser = Parser(self.current_order['url'])
            product_info = parser.parse_product_info()

            if product_info:
                self.current_order['product_info'] = product_info
                await update.message.reply_text(f"Товар добавлен: {product_info.get('Название товара', 'Неизвестно')}.")

                # Сохранение данных заказа в существующий файл
                self.save_order_to_file(update)
                await update.message.reply_text("Заказ успешно добавлен. Введите ссылку на новый товар или завершите ввод командой 'конец'.", reply_markup=self.order_keyboard)

                # Очищаем данные текущего заказа и продолжаем ожидание новых данных
                self.current_order.clear()
            else:
                await update.message.reply_text("Не удалось получить данные о товаре. Попробуйте снова.")

    def save_order_to_file(self, update: Update):
        """Сохранение заказа в уже существующий или новый файл."""
        if not self.order_file_path:
            self.order_file_path = self.generate_order_file()  # Генерируем файл, если его нет
        
        # Проверяем, существует ли файл, если нет - создаем новый DataFrame
        if not os.path.exists(self.order_file_path):
            logging.info(f"Файл {self.order_file_path} не существует, создаем новый.")
            df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])
        else:
            df = pd.read_excel(self.order_file_path)

        # Создаем новую запись для таблицы заказов
        new_order = pd.DataFrame([{
            'Ссылка': self.current_order['url'],
            'Количество': self.current_order['quantity'],
            'Опции': self.current_order['options'],
            'Название товара': self.current_order['product_info'].get('Название товара', ''),
            'Оригинальная цена': self.current_order['product_info'].get('Оригинальная цена', ''),
            'Стоимость доставки': self.current_order['product_info'].get('Стоимость доставки', ''),
            'Продавец': self.current_order['product_info'].get('Продавец', '')
        }])

        # Добавляем новую строку к существующим данным
        df = pd.concat([df, new_order], ignore_index=True)

        # Сохраняем изменения
        df.to_excel(self.order_file_path, index=False)
        logging.info(f"Заказ успешно добавлен в файл: {self.order_file_path}")


    def create_shipping_file(self, orders_file):
        """Создание файла shipping.xlsx с колонками 'Название товара' и 'Количество'."""
        df = pd.read_excel(orders_file)
        shipping_df = df[['Название товара', 'Количество']]
        shipping_file = self.generate_shipping_filename()
        shipping_df.to_excel(shipping_file, index=False)
        logging.info(f"Таблица {shipping_file} успешно создана.")

    async def calculate_total_cost(self, update: Update, context):
        """Подсчет общей стоимости заказа."""
        if not self.order_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        df = pd.read_excel(self.order_file_path)
        total = 0

        for index, row in df.iterrows():
            url = row['Ссылка']
            parser = Parser(url)
            product_info = parser.parse_product_info()
            if product_info:
                price_str = product_info['Оригинальная цена']
                price = int(re.sub(r'[^\d]', '', price_str))  # Убираем все символы кроме цифр
                total += price * row['Количество']

        await update.message.reply_text(f"Общая стоимость заказа: {total}₩")

    # async def finalize_order(self, update: Update):
    #     """Завершение режима заказа и отправка файла с заказом."""
    #     if self.order_file_path and os.path.exists(self.order_file_path):
    #         logging.info(f"Завершаем заказ и создаем файлы для отправки: {self.order_file_path}")
            
    #         # Создаем файл для транспортной компании
    #         shipping_file = self.generate_shipping_filename()
    #         self.create_shipping_file(self.order_file_path)

    #         # Отправляем файл заказов
    #         await update.message.reply_document(document=open(self.order_file_path, 'rb'), caption="Вот ваш файл заказов.")

    #         # Отправляем файл для транспортной компании
    #         await update.message.reply_document(document=open(shipping_file, 'rb'), caption="Вот ваш файл для отправки товаров.")
    #     else:
    #         await update.message.reply_text("Файл заказов не найден.")
