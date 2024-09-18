from selenium import webdriver
from selenium.common.exceptions import NoSuchSessionException
from utility import Utils

class Utils:
    def __init__(self):
        self.driver = None

    def start_webdriver_session(self):
        """Инициализирует новую сессию WebDriver, если она не существует, или восстанавливает её в случае потери."""
        if self.driver is None:
            self.driver = webdriver.Remote(
                command_executor='http://selenium-chrome:4444/wd/hub',
                desired_capabilities=webdriver.DesiredCapabilities.CHROME
            )
            print("Новая сессия WebDriver запущена")
        else:
            print("WebDriver сессия уже существует.")

    def get_url_with_webdriver(self, url):
        """Открывает URL с помощью WebDriver, перезапускает сессию, если она потеряна."""
        try:
            if self.driver is None:
                self.start_webdriver_session()
            self.driver.get(url)
        except NoSuchSessionException:
            print("Сессия не найдена. Перезапуск...")
            self.start_webdriver_session()
            self.driver.get(url)

    def quit_webdriver_session(self):
        """Корректно завершает сессию WebDriver, если она существует."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("Сессия WebDriver завершена.")
        else:
            print("Сессия WebDriver не была активна.")

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

