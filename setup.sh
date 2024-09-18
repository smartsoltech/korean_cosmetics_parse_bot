#!/bin/bash

# Проверка, существует ли файл .env
if [ -f ".env" ]; then
  echo ".env файл уже существует. Вы хотите его перезаписать? (y/n)"
  read overwrite

  if [ "$overwrite" != "y" ]; then
    echo "Настройка отменена."
    exit 1
  fi
fi

# Установка значений по умолчанию
DEFAULT_SELENIUM_URL="http://selenium-chrome:4444/wd/hub"
DEFAULT_CHROME_NO_SANDBOX="--no-sandbox"
DEFAULT_CHROME_DISABLE_DEV_SHM="--disable-dev-shm-usage"

# Запрашиваем у пользователя параметры с указанием значений по умолчанию
read -p "Введите Selenium URL [$DEFAULT_SELENIUM_URL]: " SELENIUM_URL
SELENIUM_URL=${SELENIUM_URL:-$DEFAULT_SELENIUM_URL}

read -p "Введите опцию для Chrome (no-sandbox) [$DEFAULT_CHROME_NO_SANDBOX]: " CHROME_NO_SANDBOX
CHROME_NO_SANDBOX=${CHROME_NO_SANDBOX:-$DEFAULT_CHROME_NO_SANDBOX}

read -p "Введите опцию для Chrome (disable-dev-shm-usage) [$DEFAULT_CHROME_DISABLE_DEV_SHM]: " CHROME_DISABLE_DEV_SHM
CHROME_DISABLE_DEV_SHM=${CHROME_DISABLE_DEV_SHM:-$DEFAULT_CHROME_DISABLE_DEV_SHM}

# Создание файла .env с введёнными параметрами
cat <<EOL > .env
# Selenium settings
SELENIUM_URL=$SELENIUM_URL
CHROME_NO_SANDBOX=$CHROME_NO_SANDBOX
CHROME_DISABLE_DEV_SHM=$CHROME_DISABLE_DEV_SHM
EOL

echo ".env файл успешно создан и настроен!"
