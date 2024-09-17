# parser.py
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # Чтобы автоматически загружать ChromeDriver

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
        # chrome_options.add_argument("--headless")  # Отключаем фоновый режим
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def fetch_page(self):
        """Имитируем заход на страницу через браузер и загружаем её"""
        try:
            logger.info(f"Открытие страницы: {self.url}")
            self.driver.get(self.url)

            # Ожидание, пока страница полностью загрузится (например, по наличию элемента с ценой)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "prod-price"))
            )
            logger.info("Страница успешно загружена")

        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы: {e}")
            self.driver.quit()
            return None

    def parse_prices(self):
        """Парсинг страницы и извлечение цен с помощью Selenium"""
        self.fetch_page()
        
        try:
            logger.info("Начало парсинга страницы")

            product_prices = {}

            # Извлекаем "обычную" цену (если есть)
            try:
                origin_price_element = self.driver.find_element(By.CLASS_NAME, "origin-price")
                product_prices["original_price"] = origin_price_element.text.strip()
                logger.info(f"Оригинальная цена: {product_prices['original_price']}")
            except Exception:
                logger.info("Оригинальная цена не найдена")

            # Извлекаем "продажную" цену (если есть)
            try:
                sale_price_element = self.driver.find_element(By.CSS_SELECTOR, "div.prod-sale-price strong")
                product_prices["sale_price"] = sale_price_element.text.strip()
                logger.info(f"Продажная цена: {product_prices['sale_price']}")
            except Exception:
                logger.info("Продажная цена не найдена")

            # Извлекаем цену со скидкой (если есть)
            try:
                coupon_price_element = self.driver.find_element(By.CSS_SELECTOR, "div.prod-coupon-price strong")
                product_prices["coupon_price"] = coupon_price_element.text.strip()
                logger.info(f"Цена по купону: {product_prices['coupon_price']}")
            except Exception:
                logger.info("Цена по купону не найдена")

            # Закрываем драйвер после завершения парсинга
            self.driver.quit()

            if product_prices:
                logger.info(f"Цены успешно извлечены: {product_prices}")
                return product_prices
            else:
                logger.error("Не удалось найти цены на странице.")
                return None

        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            self.driver.quit()
            return None
