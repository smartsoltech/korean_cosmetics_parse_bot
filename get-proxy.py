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

def fetch_proxies_from_api(api_url):
    """Функция для получения списка прокси с API"""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        proxies = []
        for proxy_data in data['data']:
            ip = proxy_data['ip']
            port = proxy_data['port']
            https = proxy_data['protocols'] and 'https' in proxy_data['protocols']

            proxy = f"{ip}:{port}"
            proxies.append({
                "proxy": proxy,
                "https": https
            })

        return proxies
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return []

def check_proxy(proxy, https):
    """Проверяет, доступен ли прокси"""
    proxies = {
        "http": f"http://{proxy}",
        "https": f"https://{proxy}" if https else f"http://{proxy}"
    }
    try:
        # Отправляем запрос на Google для проверки прокси
        response = requests.get('https://www.coupang.com', proxies=proxies, timeout=5)
        if response.status_code == 200:
            print(f"Прокси {proxy} работает.")
            return True
    except requests.RequestException:
        print(f"Прокси {proxy} не работает.")
    return False

def save_proxies_to_file(proxies, filename="proxies.txt"):
    """Сохраняет список прокси в файл"""
    with open(filename, 'w') as file:
        for proxy in proxies:
            proxy_line = proxy["proxy"] + (" (HTTPS)" if proxy["https"] else "")
            file.write(proxy_line + "\n")

# Пример использования для HTML-страницы
url = 'https://free-proxy-list.net/#list'  # Реальная страница с прокси-серверами
html_content = fetch_proxies_from_webpage(url)  # Получаем HTML-контент

# # Парсим HTML для получения списка прокси
proxies = parse_proxies_from_html(html_content)

# Пример использования для API
api_url = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'
api_proxies = fetch_proxies_from_api(api_url)

# Объединяем прокси из обоих источников
all_proxies = proxies + api_proxies

# Фильтруем только рабочие прокси
working_proxies = [proxy for proxy in all_proxies if check_proxy(proxy["proxy"], proxy["https"])]

# Сохраняем рабочие прокси в файл
save_proxies_to_file(working_proxies)

print(f"Найдено {len(working_proxies)} рабочих прокси.")
for proxy in working_proxies:
    print(f"Рабочий прокси: {proxy['proxy']}")
