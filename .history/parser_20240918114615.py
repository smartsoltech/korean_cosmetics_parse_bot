import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# Настраиваем логирование
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Настройка драйвера для подключения к Selenium, запущенному в Docker-контейнере"""
        try:
            logger.info("Настройка удаленного WebDriver для подключения к контейнеру")
            selenium_url = os.getenv("SELENIUM_URL")  # Загружаем URL Selenium из .env
            chrome_options = webdriver.ChromeOptions()

            # Получаем опции для Chrome из переменных окружения
            chrome_options.add_argument(os.getenv("CHROME_NO_SANDBOX", "--no-sandbox"))
            chrome_options.add_argument(os.getenv("CHROME_DISABLE_DEV_SHM", "--disable-dev-shm-usage"))

            # Устанавливаем соединение с Selenium
            self.driver = webdriver.Remote(
                command_executor=selenium_url,
                options=chrome_options,
                keep_alive=True  # Оставляем соединение открытым
            )
        except WebDriverException as e:
            logger.error(f"Ошибка при настройке WebDriver: {e}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при настройке WebDriver: {e}")
        finally:
            if self.driver:
                logger.info("WebDriver успешно настроен")
            else:
                logger.warning("WebDriver не был настроен")

    def fetch_page(self):
        """Метод для загрузки страницы"""
        try:
            logger.info(f"Загрузка страницы: {self.url}")
            self.driver.get(self.url)
        except WebDriverException as e:
            logger.error(f"Ошибка при загрузке страницы: {e}")
        finally:
            if self.driver:
                logger.info("Операция с WebDriver завершена")

    def parse_product_info(self):
        """Парсинг страницы и извлечение данных о товаре"""
        self.fetch_page()
        
        try:
            logger.info("Начало парсинга страницы")

            product_info = {}

            # Извлекаем название товара
            try:
                product_name = self.driver.find_element(By.CLASS_NAME, "prod-buy-header__title").text
                product_info["Название товара"] = product_name
                logger.info(f"Название товара: {product_name}")
            except Exception as e:
                logger.error(f"Не удалось найти название товара: {e}")

            # Извлекаем страну происхождения
            try:
                origin_country = self.driver.find_element(By.CLASS_NAME, "prod-buy-header__origin_country").text
                product_info["Страна происхождения"] = origin_country
                logger.info(f"Страна происхождения: {origin_country}")
            except Exception as e:
                logger.error(f"Не удалось найти страну происхождения: {e}")

            # Извлекаем рейтинг товара
            try:
                rating = self.driver.find_element(By.CLASS_NAME, "rds-rating-score").text
                product_info["Рейтинг"] = rating
                logger.info(f"Рейтинг товара: {rating}")
            except Exception as e:
                logger.error(f"Не удалось найти рейтинг товара: {e}")

            # Извлекаем количество отзывов
            try:
                review_count = self.driver.find_element(By.CLASS_NAME, "count").text
                product_info["Количество отзывов"] = review_count
                logger.info(f"Количество отзывов: {review_count}")
            except Exception as e:
                logger.error(f"Не удалось найти количество отзывов: {e}")

            # Извлекаем оригинальную цену товара
            try:
                original_price = self.driver.find_element(By.CLASS_NAME, "total-price").text
                product_info["Оригинальная цена"] = original_price
                logger.info(f"Оригинальная цена: {original_price}")
            except Exception as e:
                logger.error(f"Не удалось найти оригинальную цену: {e}")

            # Извлекаем стоимость доставки
            try:
                delivery_fee = self.driver.find_element(By.CLASS_NAME, "prod-shipping-fee-message").text
                product_info["Стоимость доставки"] = delivery_fee
                logger.info(f"Стоимость доставки: {delivery_fee}")
            except Exception as e:
                logger.error(f"Не удалось найти стоимость доставки: {e}")

            # Извлекаем продавца
            try:
                seller = self.driver.find_element(By.CLASS_NAME, "prod-sale-vendor-name").text
                product_info["Продавец"] = seller
                logger.info(f"Продавец: {seller}")
            except Exception as e:
                logger.error(f"Не удалось найти продавца: {e}")

            # Извлекаем опции товара
            try:
                product_options = self.driver.find_element(By.CLASS_NAME, "tab-selector__header-value").text
                product_info["Опции товара"] = product_options
                logger.info(f"Опции товара: {product_options}")
            except Exception as e:
                logger.error(f"Не удалось найти опции товара: {e}")

            # Закрываем драйвер после завершения парсинга
            self.driver.quit()

            if product_info:
                logger.info(f"Данные о товаре успешно извлечены: {product_info}")
                return product_info
            else:
                logger.error("Не удалось найти данные о товаре на странице.")
                return None

        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            self.driver.quit()
            return None

# import json
# import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.remote.webdriver import WebDriver

# class Parser:
#     def __init__(self, driver: WebDriver):
#         self.driver = driver

#     def log_parsing_step(self, step, description, execution_time, status):
#         """ Логирование данных о процессе парсинга в JSON файл """
#         data = {
#             'step': step,
#             'description': description,
#             'execution_time': execution_time,
#             'status': status
#         }

#         # Чтение текущих данных из JSON файла
#         try:
#             with open('parsing_data.json', 'r') as f:
#                 current_data = json.load(f)
#         except FileNotFoundError:
#             current_data = []

#         # Добавление новой записи
#         current_data.append(data)

#         # Запись обновленных данных обратно в JSON файл
#         with open('parsing_data.json', 'w') as f:
#             json.dump(current_data, f, ensure_ascii=False, indent=4)

#     def parse_product_info(self):
#         """ Основной метод парсинга страницы товара с мониторингом процесса """
#         try:
#             # Парсинг названия товара
#             start_time = time.time()
#             step = "Получение названия товара"
#             try:
#                 product_name = self.driver.find_element(By.CLASS_NAME, "prod-buy-header__title").text
#                 self.log_parsing_step(step, f"Название товара: {product_name}", time.time() - start_time, "Успешно")
#             except Exception as e:
#                 self.log_parsing_step(step, str(e), time.time() - start_time, "Ошибка")
#                 product_name = None

#             # Парсинг цены товара
#             start_time = time.time()
#             step = "Получение цены товара"
#             try:
#                 product_price = self.driver.find_element(By.CLASS_NAME, "total-price").text
#                 self.log_parsing_step(step, f"Цена товара: {product_price}", time.time() - start_time, "Успешно")
#             except Exception as e:
#                 self.log_parsing_step(step, str(e), time.time() - start_time, "Ошибка")
#                 product_price = None

#             # Парсинг информации о доставке
#             start_time = time.time()
#             step = "Получение информации о доставке"
#             try:
#                 shipping_info = self.driver.find_element(By.CLASS_NAME, "shipping-fee-txt").text
#                 self.log_parsing_step(step, f"Информация о доставке: {shipping_info}", time.time() - start_time, "Успешно")
#             except Exception as e:
#                 self.log_parsing_step(step, str(e), time.time() - start_time, "Ошибка")
#                 shipping_info = None

#             # Парсинг рейтинга товара
#             start_time = time.time()
#             step = "Получение рейтинга товара"
#             try:
#                 product_rating = self.driver.find_element(By.CLASS_NAME, "rds-rating-score").text
#                 self.log_parsing_step(step, f"Рейтинг товара: {product_rating}", time.time() - start_time, "Успешно")
#             except Exception as e:
#                 self.log_parsing_step(step, str(e), time.time() - start_time, "Ошибка")
#                 product_rating = None

#             # Парсинг количества отзывов
#             start_time = time.time()
#             step = "Получение количества отзывов"
#             try:
#                 reviews_count = self.driver.find_element(By.CLASS_NAME, "count").text
#                 self.log_parsing_step(step, f"Количество отзывов: {reviews_count}", time.time() - start_time, "Успешно")
#             except Exception as e:
#                 self.log_parsing_step(step, str(e), time.time() - start_time, "Ошибка")
#                 reviews_count = None

#             # Возвращаем собранные данные
#             return {
#                 'Название товара': product_name,
#                 'Цена': product_price,
#                 'Доставка': shipping_info,
#                 'Рейтинг': product_rating,
#                 'Отзывы': reviews_count
#             }

#         except Exception as e:
#             # Логирование общей ошибки, если что-то пошло не так
#             self.log_parsing_step("Парсинг страницы", str(e), 0, "Ошибка")
#             return None
