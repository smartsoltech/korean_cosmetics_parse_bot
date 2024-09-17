# parser.py
import requests
from bs4 import BeautifulSoup
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

    def fetch_page(self):
        """Получение HTML-кода страницы."""
        try:
            logger.info(f"Отправка запроса на страницу: {self.url}")
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                logger.info("Страница успешно загружена")
                return response.content
            else:
                logger.error(f"Ошибка при запросе страницы {self.url}, статус код: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Произошла ошибка при запросе страницы: {e}")
            return None

    def parse_prices(self):
        """Парсинг страницы и извлечение цен."""
        html_content = self.fetch_page()
        if not html_content:
            logger.error("Не удалось загрузить содержимое страницы.")
            return None

        try:
            logger.info("Начало парсинга страницы")
            soup = BeautifulSoup(html_content, 'lxml')
            product_prices = {}

            # Извлекаем "обычную" цену (если есть)
            origin_price_element = soup.find("span", class_="origin-price")
            if origin_price_element:
                product_prices["original_price"] = origin_price_element.get_text(strip=True)
                logger.info(f"Оригинальная цена: {product_prices['original_price']}")
            else:
                logger.info("Оригинальная цена не найдена")

            # Извлекаем "продажную" цену (если есть)
            sale_price_element = soup.find("div", class_="prod-sale-price").find("strong")
            if sale_price_element:
                product_prices["sale_price"] = sale_price_element.get_text(strip=True)
                logger.info(f"Продажная цена: {product_prices['sale_price']}")
            else:
                logger.info("Продажная цена не найдена")

            # Извлекаем цену со скидкой (если есть)
            coupon_price_element = soup.find("div", class_="prod-coupon-price").find("strong")
            if coupon_price_element:
                product_prices["coupon_price"] = coupon_price_element.get_text(strip=True)
                logger.info(f"Цена по купону: {product_prices['coupon_price']}")
            else:
                logger.info("Цена по купону не найдена")

            if product_prices:
                logger.info(f"Цены успешно извлечены: {product_prices}")
                return product_prices
            else:
                logger.error("Не удалось найти цены на странице.")
                return None

        except Exception as e:
            logger.error(f"Ошибка при парсинге HTML: {e}")
            return None
