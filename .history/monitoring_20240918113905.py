import time
import json
import logging
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parsing_data = {
    "status": "Initializing",
    "product_name": None,
    "price": None,
    "delivery": None,
    "reviews": None,
    "errors": []
}

# Функция для мониторинга процесса парсинга
def monitor_parsing_process():
    while True:
        try:
            with open('parsing_data.json', 'r') as f:
                data = json.load(f)
                parsing_data.update(data)
        except FileNotFoundError:
            logger.error("Файл 'parsing_data.json' не найден. Ожидание...")
        time.sleep(5)

# Эндпоинт для отображения текущих данных парсинга
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(parsing_data)

if __name__ == '__main__':
    # Запускаем мониторинг в отдельном потоке
    monitoring_thread = Thread(target=monitor_parsing_process)
    monitoring_thread.start()
    
    # Запускаем Flask сервер для мониторинга
    app.run(debug=False, use_reloader=False)
