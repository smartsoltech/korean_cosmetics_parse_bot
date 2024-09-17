# parser.py
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Настройка драйвера для Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Фоновый режим
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def fetch_page(self):
        """Имитируем заход на страницу через браузер и загружаем её"""
        try:
            logger.info(f"Открытие страницы: {self.url}")
            self.driver.get(self.url)

            # Ожидание, пока страница полностью загрузится
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "prod-buy-header"))
            )
            logger.info("Страница успешно загружена")

        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы: {e}")
            self.driver.quit()
            return None

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
            except Exception:
                logger.info("Название товара не найдено")

            # Извлекаем страну происхождения
            try:
                origin_country = self.driver.find_element(By.CLASS_NAME, "prod-buy-header__origin_country").text
                product_info["Страна происхождения"] = origin_country
                logger.info(f"Страна происхождения: {origin_country}")
            except Exception:
                logger.info("Страна происхождения не найдена")

            # Извлекаем рейтинг товара
            try:
                rating = self.driver.find_element(By.CLASS_NAME, "rds-rating-score").text
                product_info["Рейтинг"] = rating
                logger.info(f"Рейтинг товара: {rating}")
            except Exception:
                logger.info("Рейтинг товара не найден")

            # Извлекаем количество отзывов
            try:
                review_count = self.driver.find_element(By.CLASS_NAME, "count").text
                product_info["Количество отзывов"] = review_count
                logger.info(f"Количество отзывов: {review_count}")
            except Exception:
                logger.info("Количество отзывов не найдено")

            # Извлекаем оригинальную цену товара
            try:
                original_price = self.driver.find_element(By.CLASS_NAME, "total-price").text
                product_info["Оригинальная цена"] = original_price
                logger.info(f"Оригинальная цена: {original_price}")
            except Exception:
                logger.info("Оригинальная цена не найдена")

            # Извлекаем стоимость доставки
            try:
                delivery_fee = self.driver.find_element(By.CLASS_NAME, "prod-shipping-fee-message").text
                product_info["Стоимость доставки"] = delivery_fee
                logger.info(f"Стоимость доставки: {delivery_fee}")
            except Exception:
                logger.info("Стоимость доставки не найдена")

            # Извлекаем продавца
            try:
                seller = self.driver.find_element(By.CLASS_NAME, "prod-sale-vendor-name").text
                product_info["Продавец"] = seller
                logger.info(f"Продавец: {seller}")
            except Exception:
                logger.info("Продавец не найден")

            # Извлекаем опции товара
            try:
                product_options = self.driver.find_element(By.CLASS_NAME, "tab-selector__header-value").text
                product_info["Опции товара"] = product_options
                logger.info(f"Опции товара: {product_options}")
            except Exception:
                logger.info("Опции товара не найдены")

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
