#!/bin/bash

# Скрипт для очистки каталога /var на Ubuntu

# Очистка временных файлов в /var/tmp
echo "Очистка временных файлов в /var/tmp..."
sudo rm -rf /var/tmp/*
echo "Временные файлы удалены."

# Очистка кеша apt
echo "Очистка кеша apt..."
sudo apt-get clean
sudo apt-get autoclean
echo "Кеш apt очищен."

# Очистка журналов старше 7 дней
echo "Очистка системных журналов старше 7 дней..."
sudo journalctl --vacuum-time=7d
echo "Системные журналы очищены."

# Принудительная ротация логов через logrotate
echo "Принудительная ротация логов..."
sudo logrotate -f /etc/logrotate.conf
echo "Логи ротации выполнены."

# Удаление старых версий пакетов Snap
echo "Удаление старых версий Snap пакетов..."
sudo snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
    sudo snap remove --purge "$snapname" --revision="$revision"
done
echo "Старые Snap пакеты удалены."

# Вывод списка подкаталогов /var с их размером
echo "Список подкаталогов в /var и их размер:"
sudo du -sh /var/*

echo "Очистка /var завершена."
