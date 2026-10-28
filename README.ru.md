# Taskboard

[![CI](https://github.com/Raphailinc/Taskboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Raphailinc/Taskboard/actions/workflows/ci.yml)

[English](README.md) · [Русский](README.ru.md)

Django-проект управления задачами через серверные HTML-формы и представления.

## Возможности

- Задачи со статусом, приоритетом, сроком и описанием.
- Поиск, фильтры и пагинация.
- Вложения с проверкой владельца при скачивании и удалении.
- Удаление вложений только POST-запросом с CSRF-защитой.
- SQLite локально и PostgreSQL в Docker Compose.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## Проверки

```bash
python manage.py test
```

## Условия запуска и границы проекта

Нужны Python 3.11+ и Django 5.2 LTS. Интерфейс: http://127.0.0.1:8000. Зарегистрируйтесь через /register/. Для Compose скопируйте .env.example в .env и выполните docker compose up --build; драйвер PostgreSQL включён в зависимости. Обычный python manage.py runserver использует переменные окружения процесса, а не читает .env. CI проверяет SQLite и PostgreSQL, применение миграций, CRUD, сортировку приоритетов и доступ к вложениям. Файлы обслуживаются аутентифицированными представлениями; при развёртывании MEDIA_ROOT должен находиться вне публично обслуживаемой директории.
