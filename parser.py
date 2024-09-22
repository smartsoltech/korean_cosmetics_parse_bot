import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


class Parser:
    def __init__(self, url: str, proxy=None):
        self.url = url
        self.proxy = proxy
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Настройка драйвера для подключения к Selenium, запущенному в Docker-контейнере"""
        try:
            logging.info("Настройка удаленного WebDriver для подключения к контейнеру")
            chrome_options = Options()

            # Добавляем настройки браузера
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
            chrome_options.add_argument("window-size=1920,1080")

            if self.proxy:
                chrome_options.add_argument(f"--proxy-server={self.proxy}")
                logging.info(f"Используем прокси: {self.proxy}")

            # Устанавливаем соединение с Selenium
            self.driver = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                options=chrome_options
            )
            logging.info("WebDriver успешно настроен")

        except WebDriverException as e:
            logging.error(f"Ошибка при настройке WebDriver: {e}")
        except Exception as e:
            logging.error(f"Неизвестная ошибка при настройке WebDriver: {e}")

    def fetch_page(self):
        """Метод для загрузки страницы"""
        try:
            logging.info(f"Загрузка страницы: {self.url}")
            self.driver.get(self.url)
        except WebDriverException as e:
            logging.error(f"Ошибка при загрузке страницы: {e}")

    def wait_for_element(self, by, selector, timeout=10):
        """Явное ожидание элемента на странице"""
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))
            return element
        except TimeoutException:
            logging.error(f"Элемент {selector} не найден за {timeout} секунд.")
            return None

    def parse_product_info(self):
        """Парсинг страницы и извлечение данных о товаре"""
        self.fetch_page()

        try:
            logging.info("Начало парсинга страницы")
            product_info = {}

            # Извлекаем название товара
            product_name_element = self.wait_for_element(By.CLASS_NAME, "prod-buy-header__title")
            if product_name_element:
                product_info["Название товара"] = product_name_element.text
                logging.info(f"Название товара: {product_info['Название товара']}")
            else:
                logging.error("Не удалось найти название товара")

            # Извлекаем страну происхождения
            origin_country_element = self.wait_for_element(By.CLASS_NAME, "prod-buy-header__origin_country")
            if origin_country_element:
                product_info["Страна происхождения"] = origin_country_element.text
                logging.info(f"Страна происхождения: {product_info['Страна происхождения']}")
            else:
                logging.error("Не удалось найти страну происхождения")

            # Извлекаем рейтинг товара
            rating_element = self.wait_for_element(By.CLASS_NAME, "rds-rating-score")
            if rating_element:
                product_info["Рейтинг"] = rating_element.text
                logging.info(f"Рейтинг товара: {product_info['Рейтинг']}")
            else:
                logging.error("Не удалось найти рейтинг товара")

            # Извлекаем количество отзывов
            review_count_element = self.wait_for_element(By.CLASS_NAME, "count")
            if review_count_element:
                product_info["Количество отзывов"] = review_count_element.text
                logging.info(f"Количество отзывов: {product_info['Количество отзывов']}")
            else:
                logging.error("Не удалось найти количество отзывов")

            # Извлекаем оригинальную цену товара
            original_price_element = self.wait_for_element(By.CLASS_NAME, "total-price")
            if original_price_element:
                product_info["Оригинальная цена"] = original_price_element.text
                logging.info(f"Оригинальная цена: {product_info['Оригинальная цена']}")
            else:
                logging.error("Не удалось найти оригинальную цену")

            # Извлекаем стоимость доставки
            delivery_fee_element = self.wait_for_element(By.CLASS_NAME, "prod-shipping-fee-message")
            if delivery_fee_element:
                product_info["Стоимость доставки"] = delivery_fee_element.text
                logging.info(f"Стоимость доставки: {product_info['Стоимость доставки']}")
            else:
                logging.error("Не удалось найти стоимость доставки")

            # Извлекаем продавца
            seller_element = self.wait_for_element(By.CLASS_NAME, "prod-sale-vendor-name")
            if seller_element:
                product_info["Продавец"] = seller_element.text
                logging.info(f"Продавец: {product_info['Продавец']}")
            else:
                logging.error("Не удалось найти продавца")

            # Извлекаем опции товара
            product_options_element = self.wait_for_element(By.CLASS_NAME, "tab-selector__header-value")
            if product_options_element:
                product_info["Опции товара"] = product_options_element.text
                logging.info(f"Опции товара: {product_info['Опции товара']}")
            else:
                logging.error("Не удалось найти опции товара")

            # Закрываем драйвер после завершения парсинга
            self.driver.quit()

            return product_info if product_info else None

        except Exception as e:
            logging.error(f"Ошибка при парсинге страницы: {e}")
            self.driver.quit()
            return None

    def is_proxy_working(self, proxy):
        """Проверяем доступность прокси"""
        try:
            proxies = {
                "http": proxy,
                "https": proxy
            }
            response = requests.get("https://www.google.com", proxies=proxies, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logging.error(f"Прокси {proxy} недоступен: {e}")
            return False

    def get_working_proxy(self, proxies_list):
        """Возвращает первый доступный прокси из списка"""
        for proxy in proxies_list:
            if self.is_proxy_working(proxy):
                return proxy
        return None
