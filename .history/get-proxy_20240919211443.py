import requests
from bs4 import BeautifulSoup

def fetch_proxies_from_webpage(url):
    """Функция для загрузки и парсинга страницы с прокси-серверами"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    # Отправляем запрос на сайт
    response = requests.get(url, headers=headers)
    
    # Проверяем успешность запроса
    if response.status_code != 200:
        raise Exception(f"Не удалось загрузить страницу: {response.status_code}")
    
    # Возвращаем HTML-контент страницы
    return response.text

def parse_proxies_from_html(html_content):
    """Функция для парсинга прокси из HTML-кода таблицы"""
    soup = BeautifulSoup(html_content, 'html.parser')
    proxies = []

    # Найти таблицу
    table = soup.find('table', {'class': 'table table-striped table-bordered'})

    # Найти все строки таблицы (кроме заголовка)
    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        ip = cols[0].text.strip()  # IP-адрес
        port = cols[1].text.strip()  # Порт
        https = cols[6].text.strip().lower() == 'yes'  # Проверяем поддержку HTTPS

        # Добавляем IP и порт в формате ip:port
        proxy = f"{ip}:{port}"
        proxies.append({
            "proxy": proxy,
            "https": https
        })

    return proxies

def save_proxies_to_file(proxies, filename="proxies.txt"):
    """Сохраняет список прокси в файл"""
    with open(filename, 'w') as file:
        for proxy in proxies:
            proxy_line = proxy["proxy"] + (" (HTTPS)" if proxy["https"] else "")
            file.write(proxy_line + "\n")

# Пример использования
url = 'https://free-proxy-list.net/#list'  # Реальная страница с прокси-серверами
html_content = fetch_proxies_from_webpage(url)  # Получаем HTML-контент

# Парсим HTML для получения списка прокси
proxies = parse_proxies_from_html(html_content)

# Сохраняем прокси в файл
save_proxies_to_file(proxies)

print(f"Найдено {len(proxies)} прокси.")
for proxy in proxies:
    print(f"Прокси: {proxy['proxy']})
