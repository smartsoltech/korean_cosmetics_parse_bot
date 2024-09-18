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
