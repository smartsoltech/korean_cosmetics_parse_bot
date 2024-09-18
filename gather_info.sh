#!/bin/bash

# Указываем файл для записи данных
OUTPUT_FILE="system_info_report.txt"

# Функция для записи в файл
function write_to_file {
    echo -e "\n### $1 ###" >> $OUTPUT_FILE
    shift
    echo -e "$@" >> $OUTPUT_FILE
}

# Очистить предыдущие результаты
> $OUTPUT_FILE

# 1. Версии системных компонентов
write_to_file "Python Version" "$(python3 --version)"
write_to_file "Selenium Version" "$(pip freeze | grep selenium)"
write_to_file "ChromeDriver Version" "$(chromedriver --version)"
write_to_file "Chrome Version" "$(google-chrome --version || chromium-browser --version)"

# 2. Переменные окружения
write_to_file "Environment Variables" "$(env)"

# 3. Проверка открытых портов (например, порт 4444 для Selenium Grid)
write_to_file "Listening Ports" "$(sudo lsof -i -P -n | grep LISTEN)"

# 4. Сетевые настройки
write_to_file "Network Configuration" "$(ifconfig)"
write_to_file "DNS Configuration" "$(cat /etc/resolv.conf)"

# 5. Логи ошибок
write_to_file "System Error Logs (last 100 lines)" "$(dmesg | tail -n 100)"
write_to_file "Docker Logs (if applicable)" "$(docker ps && docker logs selenium-chrome_1 2>/dev/null || echo 'Docker контейнер не найден')"

# 6. Проверка процессов Selenium
write_to_file "Selenium Processes" "$(ps aux | grep selenium)"

# 7. Дополнительные сведения о файловой системе
write_to_file "Disk Space" "$(df -h)"
write_to_file "Memory Usage" "$(free -m)"

# 8. Проверка установленных библиотек (только для Python)
write_to_file "Installed Python Packages" "$(pip freeze)"

# 9. Проверка Docker конфигураций
write_to_file "Docker Containers" "$(docker ps -a)"

# 10. Проверка SELinux (если используется)
if command -v getenforce &> /dev/null; then
    write_to_file "SELinux Status" "$(getenforce)"
fi

echo "Сбор данных завершен. Информация записана в $OUTPUT_FILE"
