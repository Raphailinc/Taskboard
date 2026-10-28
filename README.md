# Taskboard

[![CI](https://github.com/Raphailinc/Taskboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Raphailinc/Taskboard/actions/workflows/ci.yml)

[English](README.md) · [Русский](README.ru.md)

A Django portfolio project for managing tasks through server-rendered forms and views.

## What it does

- Create tasks with a status, priority, deadline and description.
- Search, filter and paginate task lists.
- Attach files to task records.
- Run with SQLite locally or PostgreSQL in Docker Compose.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

## Checks

```bash
python manage.py test
```

## Scope and implementation notes

Local UI: `http://127.0.0.1:8000`. This is a learning and portfolio application with a small smoke-test suite. Review account isolation and file-access policies before adapting it to a shared production service.
