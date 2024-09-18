import os
import logging

class Utils:
    @staticmethod
    def clear_dirs(folder: str):
        """Удаление всех файлов и папок в указанной директории."""
        if not os.path.exists(folder):
            logging.error(f"Папка не существует: {folder}")
            return

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logging.info(f"Удален файл: {file_path}")
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
                    logging.info(f"Удалена папка: {file_path}")
            except Exception as e:
                logging.error(f"Ошибка при удалении {file_path}: {e}")

