from selenium import webdriver
from selenium.common.exceptions import NoSuchSessionException
from utility import Utils

class Utils:
    def __init__(self):
        self.driver = None
    
    # Пример использования метода для очистки папок
    def clear_dirs(self, folder):
        """Очищает указанную папку."""
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"Файл {file_path} был удален.")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Папка {file_path} была удалена.")
            except Exception as e:
                print(f'Не удалось удалить {file_path}. Причина: {e}')

