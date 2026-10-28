# Taskboard

[![CI](https://github.com/Raphailinc/Taskboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Raphailinc/Taskboard/actions/workflows/ci.yml)

[English](README.md) · [Русский](README.ru.md)

A Django portfolio project for managing tasks through server-rendered forms and views.

## What it does

- Create tasks with a status, priority, deadline and description.
- Search, filter and paginate task lists.
- Attach files to task records; downloads and deletion are restricted to the task owner.
- Delete attachments through CSRF-protected POST forms.
- Run with SQLite locally or PostgreSQL in Docker Compose.

Requires Python 3.11+ and Django 5.2 LTS.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

For Docker Compose, copy `.env.example` to `.env` and run `docker compose up --build`. The PostgreSQL driver is included. Local Django commands read process environment variables; they do not load `.env` automatically. Register at `/register/` after starting the UI.

## Checks

```bash
python manage.py test
```

## Scope and implementation notes

Local UI: `http://127.0.0.1:8000`. CI tests both SQLite and PostgreSQL, including migrations. Tests cover task CRUD, cross-account attachment access, CSRF, safe deletion methods and priority ordering. Files are served through authenticated views, including in development. Keep `MEDIA_ROOT` outside any publicly served directory when deploying.
