# import os
# import pandas as pd
# import re
# from telegram import Update
# from telegram.ext import CallbackContext
# from parser import Parser
# import logging
# from datetime import datetime

# class OrderManager:
#     def __init__(self, order_keyboard, file_options_keyboard):
#         self.order_keyboard = order_keyboard
#         self.file_options_keyboard = file_options_keyboard
#         self.current_order = {}
#         self.waiting_for_order = False
#         self.loaded_file = None  # Переменная для хранения пути к загруженному файлу

#     async def initiate_order_process(self, update: Update, context):
#         self.waiting_for_order = True
#         self.current_order.clear()
#         await update.message.reply_text("Введите ссылку на товар.", reply_markup=self.order_keyboard)

#     async def process_order(self, update: Update, context):
#         """Обработка заказа и сохранение в файл. Бот не выходит из режима до команды 'конец'."""
#         message_text = update.message.text.lower()

#         if message_text == 'конец':
#             await self.finalize_order(update)
#             return

#         if 'url' not in self.current_order:
#             urls = re.findall(r'(https?://[^\s]+)', message_text)
#             if urls:
#                 self.current_order['url'] = urls[0]
#                 await update.message.reply_text("Ссылка получена. Введите количество.")
#             else:
#                 await update.message.reply_text("Неверная ссылка. Попробуйте снова.")
#         elif 'quantity' not in self.current_order:
#             try:
#                 quantity = int(message_text)
#                 self.current_order['quantity'] = quantity
#                 await update.message.reply_text("Введите опции или нажмите 'нет'.")
#             except ValueError:
#                 await update.message.reply_text("Введите корректное количество.")
#         elif 'options' not in self.current_order:
#             self.current_order['options'] = message_text if message_text != 'нет' else 'Без опций'
#             await update.message.reply_text("Опции товара добавлены. Начинаем парсинг данных товара...")

#             # Начало парсинга данных товара
#             parser = Parser(self.current_order['url'])
#             product_info = parser.parse_product_info()

#             if product_info:
#                 self.current_order['product_info'] = product_info
#                 await update.message.reply_text(f"Товар добавлен: {product_info.get('Название товара', 'Неизвестно')}.")

#                 # Сохранение данных заказа в файл (учитываем загруженный файл)
#                 self.save_order_to_file(update)
#                 await update.message.reply_text("Заказ успешно добавлен. Введите ссылку на новый товар или завершите ввод командой 'конец'.", reply_markup=self.order_keyboard)

#                 # Очищаем данные текущего заказа и продолжаем ожидание новых данных
#                 self.current_order.clear()
#             else:
#                 await update.message.reply_text("Не удалось получить данные о товаре. Попробуйте снова.")

#     def save_order_to_file(self, update: Update):
#         """Сохранение заказа в новый файл."""
#         orders_file = self.order_file_path

#         # Проверяем, существует ли файл
#         if os.path.exists(orders_file):
#             df = pd.read_excel(orders_file)
#         else:
#             # Если файл не существует, создаем новый DataFrame
#             df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

#         # Создаем новую запись для таблицы заказов
#         new_order = pd.DataFrame([{
#             'Ссылка': self.current_order['url'],
#             'Количество': self.current_order['quantity'],
#             'Опции': self.current_order['options'],
#             'Название товара': self.current_order['product_info'].get('Название товара', ''),
#             'Оригинальная цена': self.current_order['product_info'].get('Оригинальная цена', ''),
#             'Стоимость доставки': self.current_order['product_info'].get('Стоимость доставки', ''),
#             'Продавец': self.current_order['product_info'].get('Продавец', '')
#         }])

#         # Добавляем новую строку к существующим данным
#         df = pd.concat([df, new_order], ignore_index=True)

#         # Сохраняем файл
#         df.to_excel(orders_file, index=False)
#         logging.info(f"Заказ успешно добавлен в файл: {orders_file}")

#         """Сохранение заказа в файл. Если файл был загружен, дополняем его."""
#         orders_file = self.loaded_file if self.loaded_file else self.generate_order_filename()

#         # Проверяем, существует ли файл
#         if os.path.exists(orders_file):
#             df = pd.read_excel(orders_file)
#         else:
#             # Если файл не существует, создаем новый DataFrame
#             df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

#         # Создаем новую запись для таблицы заказов
#         new_order = pd.DataFrame([{
#             'Ссылка': self.current_order['url'],
#             'Количество': self.current_order['quantity'],
#             'Опции': self.current_order['options'],
#             'Название товара': self.current_order['product_info'].get('Название товара', ''),
#             'Оригинальная цена': self.current_order['product_info'].get('Оригинальная цена', ''),
#             'Стоимость доставки': self.current_order['product_info'].get('Стоимость доставки', ''),
#             'Продавец': self.current_order['product_info'].get('Продавец', '')
#         }])

#         # Добавляем новую строку к существующим данным
#         df = pd.concat([df, new_order], ignore_index=True)

#         # Сохраняем файл (загруженный или новый)
#         df.to_excel(orders_file, index=False)
#         logging.info(f"Заказ успешно добавлен в файл: {orders_file}")


#     async def process_uploaded_file(self, update: Update, context):
#         """Обработка загруженного файла и переход в режим добавления заказа."""
#         document = update.message.document

#         # Сохраняем файл на сервере
#         file = await document.get_file()
#         file_path = f"/tmp/{document.file_name}"
#         await file.download_to_drive(file_path)

#         try:
#             # Проверяем, соответствует ли структура файла
#             df = pd.read_excel(file_path)
#             required_columns = ['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец']

#             if all(col in df.columns for col in required_columns):
#                 self.loaded_file = file_path  # Сохраняем путь к загруженному файлу
#                 await update.message.reply_text("Файл успешно загружен. Выберите действие: 'Дополнить заказ' или 'Сформировать ТН'.", reply_markup=self.file_options_keyboard)
#             else:
#                 await update.message.reply_text("Файл не соответствует ожидаемой структуре.")
#         except Exception as e:
#             logging.error(f"Ошибка при обработке файла: {e}")
#             await update.message.reply_text("Произошла ошибка при обработке файла.")

#     async def finalize_order(self, update: Update):
#         """Завершение режима заказа, создание и отправка файлов orders и shipping."""
#         orders_file = self.loaded_file if self.loaded_file else self.generate_order_filename()
#         shipping_file = self.generate_shipping_filename()

#         if os.path.exists(orders_file):
#             await update.message.reply_text("Режим заказа завершен. Отправляем файлы...")

#             with open(orders_file, 'rb') as file:
#                 await update.message.reply_document(document=file, caption="Вот ваш файл заказов.")

#             # Создаем файл shipping.xlsx на основе orders.xlsx
#             self.create_shipping_file(orders_file)

#             # Отправляем файл shipping.xlsx
#             if os.path.exists(shipping_file):
#                 with open(shipping_file, 'rb') as file:
#                     await update.message.reply_document(document=file, caption="Вот ваш файл для отправки товаров.")
            
#             # Удаляем файлы после отправки
#             os.remove(orders_file)
#             os.remove(shipping_file)
#             logging.info(f"Файлы {orders_file} и {shipping_file} удалены после отправки.")
#         else:
#             await update.message.reply_text("Файл заказов не найден.")

#     def create_shipping_file(self, orders_file):
#         """Создание файла shipping.xlsx с колонками 'Название товара' и 'Количество'."""
#         if os.path.exists(orders_file):
#             df = pd.read_excel(orders_file)

#             # Берем только наименование товара и количество
#             shipping_df = df[['Название товара', 'Количество']]

#             # Генерируем имя для файла shipping
#             shipping_file = self.generate_shipping_filename()

#             # Сохраняем в файл shipping.xlsx
#             shipping_df.to_excel(shipping_file, index=False)
#             logging.info(f"Таблица {shipping_file} успешно создана.")

#     def generate_order_filename(self):
#         """Генерация уникального имени для файла заказов."""
#         current_date = datetime.now().strftime('%Y-%m-%d')
#         return f"order_{current_date}.xlsx"

#     def generate_shipping_filename(self):
#         """Генерация уникального имени для файла shipping."""
#         current_date = datetime.now().strftime('%Y-%m-%d')
#         return f"shipping_{current_date}.xlsx"


#     async def process_uploaded_file(self, update: Update, context):
#         """Обработка загруженного файла."""
#         document = update.message.document
#         file = await document.get_file()
#         self.loaded_file_path = f"/tmp/{document.file_name}"
#         await file.download_to_drive(self.loaded_file_path)

#         try:
#             df = pd.read_excel(self.loaded_file_path)
#             required_columns = ['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец']

#             if all(col in df.columns for col in required_columns):
#                 await update.message.reply_text("Файл успешно загружен. Выберите действие.", reply_markup=self.file_options_keyboard)
#             else:
#                 await update.message.reply_text("Файл не соответствует ожидаемой структуре.")
#         except Exception as e:
#             await update.message.reply_text(f"Ошибка при обработке файла: {e}")

#     def create_new_order_file(self, old_file):
#         """Создание нового файла для заказов с переносом данных из старого файла."""
#         new_orders_file = self.generate_order_filename()

#         # Проверяем, существует ли старый файл
#         if os.path.exists(old_file):
#             df = pd.read_excel(old_file)
#             df.to_excel(new_orders_file, index=False)  # Сохраняем данные в новый файл
#             logging.info(f"Старый файл {old_file} перенесен в новый файл {new_orders_file}.")
#         else:
#             # Если старого файла нет (что не должно происходить), создаем новый DataFrame
#             df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])
#             df.to_excel(new_orders_file, index=False)
#             logging.info(f"Создан новый файл {new_orders_file}.")

#         return new_orders_file

#     async def supplement_order(self, update: Update, context: CallbackContext):
#         """Дополнение заказа на основе загруженного файла."""
#         if not self.loaded_file:
#             await update.message.reply_text("Файл не был загружен.")
#             return

#         # Создаем новый файл заказов и копируем в него данные из загруженного файла
#         self.order_file_path = self.create_new_order_file(self.loaded_file)
#         self.waiting_for_order = True

#         await update.message.reply_text("Файл загружен. Теперь вы можете добавлять новые заказы.")


#     async def generate_shipping_file(self, update: Update, context):
#         """Генерация ТН на основе заказа."""
#         if not self.loaded_file_path:
#             await update.message.reply_text("Файл не был загружен.")
#             return

#         df = pd.read_excel(self.loaded_file_path)
#         shipping_df = df[['Название товара', 'Количество']]

#         shipping_file = self.generate_shipping_filename()
#         shipping_df.to_excel(shipping_file, index=False)

#         await update.message.reply_document(document=open(shipping_file, 'rb'), caption="Вот ваш файл для транспортной компании.")

#         # Удаляем файлы после отправки
#         os.remove(self.loaded_file_path)
#         os.remove(shipping_file)
#         self.loaded_file_path = None
#         self.order_file_path = None

#     async def calculate_total_cost(self, update: Update, context):
#         """Подсчет общей стоимости заказа."""
#         if not self.loaded_file_path:
#             await update.message.reply_text("Файл не был загружен.")
#             return

#         df = pd.read_excel(self.loaded_file_path)
#         total = 0

#         for index, row in df.iterrows():
#             url = row['Ссылка']
#             parser = Parser(url)
#             product_info = parser.parse_product_info()
#             if product_info:
#                 price_str = product_info['Оригинальная цена']
#                 price = int(re.sub(r'[^\d]', '', price_str))  # Убираем все символы кроме цифр
#                 total += price * row['Количество']

#         await update.message.reply_text(f"Общая стоимость заказа: {total}₩")
import os
import pandas as pd
import re
from telegram import Update
from parser import Parser
import logging
from datetime import datetime
from telegram.ext import CallbackContext
class OrderManager:
    def __init__(self, order_keyboard, file_options_keyboard):
        self.order_keyboard = order_keyboard
        self.file_options_keyboard = file_options_keyboard
        self.current_order = {}
        self.waiting_for_order = False
        self.loaded_file = None  # Переменная для хранения пути к загруженному файлу
        self.order_file_path = None  # Путь к новому файлу заказов

    async def initiate_order_process(self, update: Update, context):
        self.waiting_for_order = True
        self.current_order.clear()
        await update.message.reply_text("Введите ссылку на товар.", reply_markup=self.order_keyboard)

    async def process_order(self, update: Update, context):
        """Обработка заказа и сохранение в файл. Бот не выходит из режима до команды 'конец'."""
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

                # Сохранение данных заказа в файл (учитываем загруженный файл)
                self.save_order_to_file(update)
                await update.message.reply_text("Заказ успешно добавлен. Введите ссылку на новый товар или завершите ввод командой 'конец'.", reply_markup=self.order_keyboard)

                # Очищаем данные текущего заказа и продолжаем ожидание новых данных
                self.current_order.clear()
            else:
                await update.message.reply_text("Не удалось получить данные о товаре. Попробуйте снова.")

    def save_order_to_file(self, update: Update):
        """Сохранение заказа в файл. Если файл был загружен, дополняем его."""
        orders_file = self.order_file_path if self.order_file_path else self.generate_order_filename()

        # Проверяем, существует ли файл
        if os.path.exists(orders_file):
            df = pd.read_excel(orders_file)
        else:
            # Если файл не существует, создаем новый DataFrame
            df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])

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

        # Сохраняем файл (загруженный или новый)
        df.to_excel(orders_file, index=False)
        logging.info(f"Заказ успешно добавлен в файл: {orders_file}")

    async def process_uploaded_file(self, update: Update, context):
        """Обработка загруженного файла и переход в режим добавления заказа."""
        document = update.message.document

        # Сохраняем файл на сервере
        file = await document.get_file()
        file_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(file_path)

        try:
            # Проверяем, соответствует ли структура файла
            df = pd.read_excel(file_path)
            required_columns = ['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец']

            if all(col in df.columns for col in required_columns):
                self.loaded_file = file_path  # Сохраняем путь к загруженному файлу
                await update.message.reply_text("Файл успешно загружен. Выберите действие: 'Дополнить заказ' или 'Сформировать ТН'.", reply_markup=self.file_options_keyboard)
            else:
                await update.message.reply_text("Файл не соответствует ожидаемой структуре.")
        except Exception as e:
            logging.error(f"Ошибка при обработке файла: {e}")
            await update.message.reply_text("Произошла ошибка при обработке файла.")

    async def supplement_order(self, update: Update, context: CallbackContext):
        """Дополнение заказа на основе загруженного файла."""
        if not self.loaded_file:
            await update.message.reply_text("Файл не был загружен.")
            return

        # Создаем новый файл и переносим в него данные старого файла
        self.order_file_path = self.create_new_order_file(self.loaded_file)
        self.waiting_for_order = True
        await update.message.reply_text("Файл загружен. Теперь вы можете добавлять новые заказы.")

    def create_new_order_file(self, old_file):
        """Создание нового файла для заказов с переносом данных из старого файла."""
        new_orders_file = self.generate_order_filename()

        # Проверяем, существует ли старый файл
        if os.path.exists(old_file):
            df = pd.read_excel(old_file)
            df.to_excel(new_orders_file, index=False)  # Сохраняем данные в новый файл
            logging.info(f"Старый файл {old_file} перенесен в новый файл {new_orders_file}.")
        else:
            # Если старого файла нет, создаем новый DataFrame
            df = pd.DataFrame(columns=['Ссылка', 'Количество', 'Опции', 'Название товара', 'Оригинальная цена', 'Стоимость доставки', 'Продавец'])
            df.to_excel(new_orders_file, index=False)
            logging.info(f"Создан новый файл {new_orders_file}.")

        return new_orders_file

    async def finalize_order(self, update: Update):
        """Завершение режима заказа, создание и отправка файлов orders и shipping."""
        orders_file = self.order_file_path if self.order_file_path else self.generate_order_filename()
        shipping_file = self.generate_shipping_filename()

        if os.path.exists(orders_file):
            await update.message.reply_text("Режим заказа завершен. Отправляем файлы...")

            with open(orders_file, 'rb') as file:
                await update.message.reply_document(document=file, caption="Вот ваш файл заказов.")

            # Создаем файл shipping.xlsx на основе orders.xlsx
            self.create_shipping_file(orders_file)

            # Отправляем файл shipping.xlsx
            if os.path.exists(shipping_file):
                with open(shipping_file, 'rb') as file:
                    await update.message.reply_document(document=file, caption="Вот ваш файл для отправки товаров.")
            
            # Удаляем файлы после отправки
            os.remove(orders_file)
            os.remove(shipping_file)
            logging.info(f"Файлы {orders_file} и {shipping_file} удалены после отправки.")
        else:
            await update.message.reply_text("Файл заказов не найден.")

    def create_shipping_file(self, orders_file):
        """Создание файла shipping.xlsx с колонками 'Название товара' и 'Количество'."""
        if os.path.exists(orders_file):
            df = pd.read_excel(orders_file)

            # Берем только наименование товара и количество
            shipping_df = df[['Название товара', 'Количество']]

            # Генерируем имя для файла shipping
            shipping_file = self.generate_shipping_filename()

            # Сохраняем в файл shipping.xlsx
            shipping_df.to_excel(shipping_file, index=False)
            logging.info(f"Таблица {shipping_file} успешно создана.")

    def generate_order_filename(self):
        """Генерация уникального имени для файла заказов."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        return f"order_{current_date}.xlsx"

    def generate_shipping_filename(self):
        """Генерация уникального имени для файла shipping."""
        current_date = datetime.now().strftime('%Y-%m-%d')
        return f"shipping_{current_date}.xlsx"
