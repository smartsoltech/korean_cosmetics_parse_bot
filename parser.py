import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.setup_driver()
        self.setup_options()

    def setup_options(self):
        """Настройка опций браузера, включая User-Agent"""
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        options.add_argument("window-size=1920,1080")
        return options

    def setup_driver(self):
        """Настройка драйвера для подключения к Selenium, запущенному в Docker-контейнере"""
        try:
            logger.info("Настройка удаленного WebDriver для подключения к контейнеру")
            selenium_url = os.getenv("SELENIUM_URL")
            chrome_options = self.setup_options()

            # Устанавливаем соединение с Selenium
            self.driver = webdriver.Remote(
                command_executor=selenium_url,
                options=chrome_options,
                keep_alive=True
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

    def take_screenshot(self, step_name):
        """Делает скриншот текущего состояния страницы"""
        screenshot_path = f'screenshots/{step_name}_{int(time.time())}.png'
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"Скриншот сохранен: {screenshot_path}")

    def fetch_page(self):
        """Метод для загрузки страницы"""
        try:
            logger.info(f"Загрузка страницы: {self.url}")
            self.driver.get(self.url)
            self.take_screenshot("page_loaded")
        except WebDriverException as e:
            logger.error(f"Ошибка при загрузке страницы: {e}")
        finally:
            if self.driver:
                logger.info("Операция с WebDriver завершена")

    def wait_for_element(self, by, selector, timeout=10):
        """Явное ожидание элемента"""
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))
            return element
        except TimeoutException:
            logger.error(f"Элемент {selector} не найден за {timeout} секунд.")
            return None

    def parse_product_info(self):
        """Парсинг страницы и извлечение данных о товаре"""
        self.fetch_page()

        try:
            logger.info("Начало парсинга страницы")
            product_info = {}

            # Извлекаем название товара
            try:
                product_name_element = self.wait_for_element(By.CLASS_NAME, "prod-buy-header__title")
                if product_name_element:
                    product_info["Название товара"] = product_name_element.text
                    logger.info(f"Название товара: {product_info['Название товара']}")
                self.take_screenshot("product_name")
            except Exception as e:
                logger.error(f"Не удалось найти название товара: {e}")

            # Извлекаем страну происхождения
            try:
                origin_country_element = self.wait_for_element(By.CLASS_NAME, "prod-buy-header__origin_country")
                if origin_country_element:
                    product_info["Страна происхождения"] = origin_country_element.text
                    logger.info(f"Страна происхождения: {product_info['Страна происхождения']}")
                self.take_screenshot("origin_country")
            except Exception as e:
                logger.error(f"Не удалось найти страну происхождения: {e}")

            # Извлекаем рейтинг товара
            try:
                rating_element = self.wait_for_element(By.CLASS_NAME, "rds-rating-score")
                if rating_element:
                    product_info["Рейтинг"] = rating_element.text
                    logger.info(f"Рейтинг товара: {product_info['Рейтинг']}")
                self.take_screenshot("rating")
            except Exception as e:
                logger.error(f"Не удалось найти рейтинг товара: {e}")

            # Извлекаем количество отзывов
            try:
                review_count_element = self.wait_for_element(By.CLASS_NAME, "count")
                if review_count_element:
                    product_info["Количество отзывов"] = review_count_element.text
                    logger.info(f"Количество отзывов: {product_info['Количество отзывов']}")
                self.take_screenshot("review_count")
            except Exception as e:
                logger.error(f"Не удалось найти количество отзывов: {e}")

            # Извлекаем оригинальную цену товара
            try:
                original_price_element = self.wait_for_element(By.CLASS_NAME, "total-price")
                if original_price_element:
                    product_info["Оригинальная цена"] = original_price_element.text
                    logger.info(f"Оригинальная цена: {product_info['Оригинальная цена']}")
                self.take_screenshot("original_price")
            except Exception as e:
                logger.error(f"Не удалось найти оригинальную цену: {e}")

            # Извлекаем стоимость доставки
            try:
                delivery_fee_element = self.wait_for_element(By.CLASS_NAME, "prod-shipping-fee-message")
                if delivery_fee_element:
                    product_info["Стоимость доставки"] = delivery_fee_element.text
                    logger.info(f"Стоимость доставки: {product_info['Стоимость доставки']}")
                self.take_screenshot("delivery_fee")
            except Exception as e:
                logger.error(f"Не удалось найти стоимость доставки: {e}")

            # Извлекаем продавца
            try:
                seller_element = self.wait_for_element(By.CLASS_NAME, "prod-sale-vendor-name")
                if seller_element:
                    product_info["Продавец"] = seller_element.text
                    logger.info(f"Продавец: {product_info['Продавец']}")
                self.take_screenshot("seller")
            except Exception as e:
                logger.error(f"Не удалось найти продавца: {e}")

            # Извлекаем опции товара
            try:
                product_options_element = self.wait_for_element(By.CLASS_NAME, "tab-selector__header-value")
                if product_options_element:
                    product_info["Опции товара"] = product_options_element.text
                    logger.info(f"Опции товара: {product_info['Опции товара']}")
                self.take_screenshot("product_options")
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
