from flask import Flask, render_template
import threading
import time
import json

app = Flask(__name__)

# Хранение временных данных парсинга
parsing_data = []

# Функция для мониторинга процесса парсинга
def monitor_parsing_process():
    while True:
        with open('parsing_data.json', 'r') as f:
            global parsing_data
            parsing_data = json.load(f)
        time.sleep(1)  # Обновление данных каждую секунду

@app.route('/')
def index():
    return render_template('index.html', data=parsing_data)

if __name__ == "__main__":
    # Запуск мониторинга в отдельном потоке
    t = threading.Thread(target=monitor_parsing_process)
    t.start()

    # Запуск веб-сервера
    app.run(debug=True, port=5000)
