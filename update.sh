#!/usr/bin/env bash

#Сборка и перезапуск контейнеров
docker-compose build && docker-compose down && docker-compose up -d

#Очистка docker от мусора
docker system prune -f

#Очистка директорий с файлами бота
rm outcome/*
rm income/*