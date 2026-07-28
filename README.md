# LMS Django REST Framework Project

Бэкенд-сервер для платформы онлайн-обучения (LMS-системы).

## Стек технологий
- Python 3
- Django / Django REST Framework (DRF)
- PostgreSQL
- Инструменты качества кода: Black, Flake8

## Как запустить проект

1. Клонировать репозиторий.
2. Создать файл `.env` в корне проекта и заполнить его переменными:
   ```env
   SECRET_KEY=твой_секретный_ключ
   DB_PASSWORD=твой_пароль_от_postgres
   ```
3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Применить миграции:
   ```bash
   python manage.py migrate
   ```
5. Запустить сервер:
   ```bash
   python manage.py runserver
   ```
