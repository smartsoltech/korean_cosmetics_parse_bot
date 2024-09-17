import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class WatchdogHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            logger.info(f"Создана новая директория: {event.src_path}")
        else:
            logger.info(f"Создан новый файл: {event.src_path}")
    
    def on_deleted(self, event):
        if event.is_directory:
            logger.info(f"Удалена директория: {event.src_path}")
        else:
            logger.info(f"Удален файл: {event.src_path}")
    
    def on_modified(self, event):
        if event.is_directory:
            logger.info(f"Изменена директория: {event.src_path}")
        else:
            logger.info(f"Изменен файл: {event.src_path}")
    
    def on_moved(self, event):
        logger.info(f"Перемещен {event.src_path} в {event.dest_path}")

def start_watchdog(path_to_watch):
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
    # Укажите путь для отслеживания изменений
    path_to_watch = "/usr/src/app/watched_directory"
    logger.info(f"Наблюдение за изменениями в директории: {path_to_watch}")
    start_watchdog(path_to_watch)
