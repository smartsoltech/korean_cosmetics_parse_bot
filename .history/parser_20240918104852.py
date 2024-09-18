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

            # Извлекаем конечную цену товара
            try:
                final_price = self.driver.find_element(By.CSS_SELECTOR, ".prod-coupon-price .total-price strong").text
                product_info["Конечная цена"] = final_price
                logger.info(f"Конечная цена: {final_price}")
            except NoSuchElementException:
                logger.error("Не удалось найти конечную цену")

            # Извлекаем исходную цену товара
            try:
                original_price = self.driver.find_element(By.CSS_SELECTOR, ".prod-origin-price .origin-price").text
                product_info["Исходная цена"] = original_price
                logger.info(f"Исходная цена: {original_price}")
            except NoSuchElementException:
                logger.error("Не удалось найти исходную цену")

            # Закрываем сессию Selenium
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
