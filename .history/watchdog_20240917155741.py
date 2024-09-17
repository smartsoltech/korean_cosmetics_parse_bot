import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Настройка логирования для watchdog
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class WatchdogHandler(FileSystemEventHandler):
    def on_created(self, event):
        """Обрабатывает создание новых файлов или папок"""
        if event.is_directory:
            logger.info(f"Создана новая директория: {event.src_path}")
        else:
            logger.info(f"Создан новый файл: {event.src_path}")
            # Вы можете добавить сюда логику обработки созданных файлов, например, загрузка в Telegram

    def on_deleted(self, event):
        """Обрабатывает удаление файлов или папок"""
        if event.is_directory:
            logger.info(f"Удалена директория: {event.src_path}")
        else:
            logger.info(f"Удален файл: {event.src_path}")

    def on_modified(self, event):
        """Обрабатывает изменение файлов или папок"""
        if event.is_directory:
            logger.info(f"Изменена директория: {event.src_path}")
        else:
            logger.info(f"Изменен файл: {event.src_path}")

    def on_moved(self, event):
        """Обрабатывает перемещение файлов или папок"""
        logger.info(f"Перемещен {event.src_path} в {event.dest_path}")

def start_watchdog(path_to_watch):
    """Запуск наблюдателя watchdog"""
    observer = Observer()
    event_handler = WatchdogHandler()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    path = "./"  # Укажите путь к директории, за которой хотите наблюдать
    logger.info(f"Наблюдение за изменениями в директории: {path}")
    start_watchdog(path)
