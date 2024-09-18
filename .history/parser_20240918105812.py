import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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

    def parse_product_page(self):
        """Парсинг страницы товара и извлечение всех данных с обработкой ошибок."""
        product_info = {}

        try:
            # Извлекаем название товара
            try:
                product_name = self.driver.find_element(By.CSS_SELECTOR, ".prod-buy-header__title").text
                product_info["Название товара"] = product_name
                logger.info(f"Название товара: {product_name}")
            except NoSuchElementException:
                product_info["Название товара"] = "Не найдено"
                logger.error("Не удалось найти название товара")

            # Извлекаем исходную цену
            try:
                original_price = self.driver.find_element(By.CSS_SELECTOR, ".origin-price").text
                product_info["Исходная цена"] = original_price
                logger.info(f"Исходная цена: {original_price}")
            except NoSuchElementException:
                product_info["Исходная цена"] = "Не найдена"
                logger.error("Не удалось найти исходную цену")

            # Извлекаем конечную цену (со скидкой)
            try:
                discount_price = self.driver.find_element(By.CSS_SELECTOR, ".total-price strong").text
                product_info["Конечная цена"] = discount_price
                logger.info(f"Конечная цена: {discount_price}")
            except NoSuchElementException:
                product_info["Конечная цена"] = "Не найдена"
                logger.error("Не удалось найти конечную цену")

            # Извлекаем рейтинг товара
            try:
                rating = self.driver.find_element(By.CSS_SELECTOR, ".rds-rating-score").text
                product_info["Рейтинг товара"] = rating
                logger.info(f"Рейтинг товара: {rating}")
            except NoSuchElementException:
                product_info["Рейтинг товара"] = "Не найден"
                logger.error("Не удалось найти рейтинг товара")

            # Извлекаем количество отзывов
            try:
                review_count = self.driver.find_element(By.CSS_SELECTOR, ".count").text
                product_info["Количество отзывов"] = review_count
                logger.info(f"Количество отзывов: {review_count}")
            except NoSuchElementException:
                product_info["Количество отзывов"] = "Не найдено"
                logger.error("Не удалось найти количество отзывов")

            # Извлекаем информацию о доставке
            try:
                delivery_info = self.driver.find_element(By.CSS_SELECTOR, ".shipping-fee-title-txt").text
                product_info["Стоимость доставки"] = delivery_info
                logger.info(f"Стоимость доставки: {delivery_info}")
            except NoSuchElementException:
                product_info["Стоимость доставки"] = "Не найдена"
                logger.error("Не удалось найти информацию о доставке")

            # Извлекаем информацию о продавце
            try:
                seller_info = self.driver.find_element(By.CSS_SELECTOR, ".prod-vendor-info").text
                product_info["Продавец"] = seller_info
                logger.info(f"Продавец: {seller_info}")
            except NoSuchElementException:
                product_info["Продавец"] = "Не найден"
                logger.error("Не удалось найти информацию о продавце")

            # Извлекаем доступные опции товара
            try:
                options = self.driver.find_element(By.CSS_SELECTOR, ".prod-option__list").text
                product_info["Опции товара"] = options
                logger.info(f"Опции товара: {options}")
            except NoSuchElementException:
                product_info["Опции товара"] = "Не найдены"
                logger.error("Не удалось найти опции товара")

            logger.info(f"Данные о товаре успешно извлечены: {product_info}")
            return product_info

        except TimeoutException:
            logger.error("Не удалось загрузить страницу товара в течение установленного времени")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при парсинге страницы: {e}")
            return None