from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import logging

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, driver):
        """Инициализация драйвера для работы с Selenium."""
        self.driver = driver

    def parse_product_info(self):
        """Парсинг страницы товара и извлечение всех данных с обработкой ошибок."""
        product_info = {}
        wait = WebDriverWait(self.driver, 20)  # Увеличено время ожидания до 20 секунд для медленных страниц

        try:
            # 1. Название товара
            product_info["Название товара"] = self._find_element(wait, ".prod-buy-header__title", "Не найдено")

            # 2. Количество отзывов
            product_info["Количество отзывов"] = self._find_element(wait, ".count", "Не найдено")

            # 3. Оригинальная цена
            product_info["Оригинальная цена"] = self._find_element(wait, ".total-price strong", "Не найдена")

            # 4. Стоимость доставки
            product_info["Стоимость доставки"] = self._find_element(wait, ".shipping-fee-title-txt", "Не найдена")

            # 5. Страна происхождения (если есть)
            product_info["Страна происхождения"] = self._find_element(wait, ".prod-buy-header__origin_country", "Не найдена")

            # 6. Рейтинг товара
            product_info["Рейтинг товара"] = self._find_element(wait, ".rds-rating-score", "Не найден")

            # 7. Продавец
            product_info["Продавец"] = self._find_element(wait, ".prod-sale-vendor-name", "Не найден")

            # 8. Опции товара
            product_info["Опции товара"] = self._find_element(wait, ".tab-selector__header-value", "Не найдены")

            logger.info(f"Данные о товаре успешно извлечены: {product_info}")
            return product_info

        except WebDriverException as e:
            logger.error(f"Неожиданная ошибка WebDriver: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при парсинге страницы: {e}")
            return None

    def _find_element(self, wait, selector, default_value):
        """Попытка найти элемент по селектору с обработкой ошибок."""
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector))).text
            logger.info(f"Элемент найден: {element}")
            return element
        except (NoSuchElementException, TimeoutException) as e:
            logger.warning(f"Не удалось найти элемент по селектору {selector}: {e}")
            return default_value


def setup_selenium_driver():
    """Настройка драйвера для подключения к Selenium, запущенному в Docker-контейнере."""
    logger.info("Настройка удаленного WebDriver для подключения к контейнеру")
    
    selenium_url = os.getenv("SELENIUM_URL")  # Загружаем URL Selenium из переменной окружения
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Подключаемся к удаленному WebDriver
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=chrome_options,
            keep_alive=True,
            timeout=30  # Увеличено время ожидания
        )
        logger.info("WebDriver успешно настроен")
        return driver
    except WebDriverException as e:
        logger.error(f"Ошибка при настройке WebDriver: {e}")
        return None
    