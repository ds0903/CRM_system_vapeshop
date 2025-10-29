# Vapeshop CRM System

CRM система для управління вейпшопом з Telegram ботом та веб-адміністративною панеллю.

## Структура проекту

- `bot/` - Telegram бот
  - `routers/` - обробники команд
  - `utils/` - допоміжні функції
- `database/` - підключення до БД
- `entities/` - моделі даних
- `configuration/` - налаштування
- `webapp/` - веб-адмінка
  - `templates/` - HTML шаблони
  - `static/` - статичні файли

## Встановлення

1. Створіть віртуальне середовище:
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Встановіть залежності:
```bash
pip install -r requirements.txt
```

3. Налаштуйте .env файл (скопіюйте .env.example)

4. Створіть БД та таблиці через Alembic або вручну

## Запуск

Веб-сервер (FastAPI):
```bash
uvicorn webapp.main:app --reload
```

Telegram бот:
```bash
python -m bot
```

## Функціонал

- Команда /admin для доступу до адмін-панелі
- JWT авторизація для веб-панелі
- PostgreSQL база даних
