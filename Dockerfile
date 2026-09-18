# Указываем базовый образ
FROM python:3.12-slim

# Устанавливаем системные библиотеки для базы данных PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Копируем проект
COPY . .

EXPOSE 8000
