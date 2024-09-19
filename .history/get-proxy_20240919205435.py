import requests
from bs4 import BeautifulSoup
import random

def fetch_proxies():
    """Функция для парсинга прокси с сайта"""
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    proxies = []
    table = soup.find('table', id='proxylisttable')

    for row in table.tbody.find_all('tr'):
        cols = row.find_all('td')
        ip = cols[0].text
        port = cols[1].text
        https = cols[6].text

        # Используем только HTTPS прокси
        if https == 'yes':
            proxy = f"{ip}:{port}"
            proxies.append(proxy)

    return proxies

def save_proxies_to_file(proxies, filename="proxies.txt"):
    """Функция для сохранения списка прокси в файл"""
    with open(filename, 'w') as file:
        for proxy in proxies:
            file.write(proxy + "\n")

# Получаем прокси и сохраняем их в файл
proxies = fetch_proxies()
save_proxies_to_file(proxies)

print(f"Найдено и сохранено {len(proxies)} прокси.")
