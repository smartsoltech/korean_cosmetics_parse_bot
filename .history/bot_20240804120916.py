import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import pandas as pd

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Global state
parsing_mode = False
parsed_data = []

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для парсинга ссылок.\n"
                        "Напишите @bot заказ чтобы начать парсинг.\n"
                        "Напишите конец чтобы завершить парсинг и получить таблицу.")

@dp.message_handler(lambda message: '@bot заказ' in message.text)
async def start_parsing(message: types.Message):
    global parsing_mode
    parsing_mode = True
    parsed_data.clear()
    await message.reply("Режим парсинга активирован. Отправьте ссылки и количество. Напишите 'конец' чтобы завершить.")

@dp.message_handler(lambda message: 'конец' in message.text.lower())
async def stop_parsing(message: types.Message):
    global parsing_mode
    parsing_mode = False

    if parsed_data:
        df = pd.DataFrame(parsed_data, columns=['Ссылка', 'Количество'])
        file_path = 'parsed_links.xlsx'
        df.to_excel(file_path, index=False)

        with open(file_path, 'rb') as file:
            await message.reply_document(file, caption="Вот ваша таблица.")
    else:
        await message.reply("Данных для записи нет.")

@dp.message_handler(lambda message: parsing_mode)
async def parse_message(message: types.Message):
    try:
        link, quantity = message.text.split()
        parsed_data.append((link, int(quantity)))
        await message.reply(f"Добавлено: {link} - {quantity}")
    except ValueError:
        await message.reply("Ошибка! Убедитесь, что отправляете сообщение в формате 'ссылка количество'.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
