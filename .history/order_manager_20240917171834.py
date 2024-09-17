import os
import pandas as pd
import re
from telegram import Update
from parser import Parser
import logging
from datetime import datetime

class OrderManager:
    def __init__(self, order_keyboard, file_options_keyboard):
        self.order_keyboard = order_keyboard
        self.file_options_keyboard = file_options_keyboard
        self.current_order = {}
        self.waiting_for_order = False

    async def initiate_order_process(self, update: Update, context):
        self.waiting_for_order = True
        self.current_order.clear()
        await update.message.reply_text("Введите ссылку на товар.", reply_markup=self.order_keyboard)

    async def process_order(self, update: Update, context):
        """Обработка заказа и сохранение в файл. Бот не выходит из режима до команды 'конец'."""
        message_text = update.message.text.lower()

        if message_text == 'конец':
            self.waiting_for_order = False
            await update.message.reply_text("Режим заказа завершен.")
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
                
                # Сохранение данных заказа в файл
                self.save_order_to_file()
                await update.message.reply_text("Заказ успешно добавлен. Введите ссылку на новый товар или завершите ввод командой 'конец'.", reply_markup=self.order_keyboard)
                
                # Очищаем данные текущего заказа и продолжаем ожидание новых данных
                self.current_order.clear()
            else:
                await update.message.reply_text("Не удалось получить данные о товаре. Попробуйте снова.")

    def save_order_to_file(self):
        """Сохранение заказа в файл."""
        orders_file = self.generate_order_filename()

        if os.path.exists(orders_file):
            df = pd.read_excel(orders_file)
        else:
            df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

        new_order = pd.DataFrame([{
            'Ссылка': self.current_order['url'],
            'Количество': self.current_order['quantity'],
            'Опции': self.current_order['options'],
            'Название товара': self.current_order['product_info'].get('Название товара', ''),
            'Оригинальная цена': self.current_order['product_info'].get('Оригинальная цена', ''),
            'Стоимость доставки': self.current_order['product_info'].get('Стоимость доставки', ''),
            'Продавец': self.current_order['product_info'].get('Продавец', '')
        }])

        df = pd.concat([df, new_order], ignore_index=True)
        df.to_excel(orders_file, index=False)
        logging.info(f"Заказ успешно добавлен в файл: {orders_file}")

    def generate_order_filename(self):
        """Генерация имени файла с заказами на основе текущей даты."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        return f"order_{current_date}.xlsx"


    def generate_shipping_file_name(self):
        """Генерация уникального имени файла для ТН (Транспортная накладная)."""
        current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        return f"shipping_{current_date}.xlsx"

    async def process_uploaded_file(self, update: Update, context):
        """Обработка загруженного файла."""
        document = update.message.document
        file = await document.get_file()
        self.loaded_file_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(self.loaded_file_path)

        try:
            df = pd.read_excel(self.loaded_file_path)
            required_columns = ['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец']

            if all(col in df.columns for col in required_columns):
                await update.message.reply_text("Файл успешно загружен. Выберите действие.", reply_markup=self.file_options_keyboard)
            else:
                await update.message.reply_text("Файл не соответствует ожидаемой структуре.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при обработке файла: {e}")

    async def supplement_order(self, update: Update, context):
        """Дополнение заказа на основе загруженного файла."""
        if not self.loaded_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        self.order_file_path = self.loaded_file_path
        self.waiting_for_order = True
        await update.message.reply_text("Файл загружен. Теперь вы можете добавлять новые заказы.")

    async def generate_shipping_file(self, update: Update, context):
        """Генерация ТН на основе заказа."""
        if not self.loaded_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        df = pd.read_excel(self.loaded_file_path)
        shipping_df = df[['Название товара', 'Количество']]

        shipping_file = self.generate_shipping_file_name()
        shipping_df.to_excel(shipping_file, index=False)

        await update.message.reply_document(document=open(shipping_file, 'rb'), caption="Вот ваш файл для транспортной компании.")

        # Удаляем файлы после отправки
        os.remove(self.loaded_file_path)
        os.remove(shipping_file)
        self.loaded_file_path = None
        self.order_file_path = None

    async def calculate_total_cost(self, update: Update, context):
        """Подсчет общей стоимости заказа."""
        if not self.loaded_file_path:
            await update.message.reply_text("Файл не был загружен.")
            return

        df = pd.read_excel(self.loaded_file_path)
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
