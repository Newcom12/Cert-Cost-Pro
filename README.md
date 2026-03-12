# CertCost Pro — Telegram-бот расчёта стоимости сертификации

Автоматический расчёт стоимости услуг сертификации и сбор заявок для компании по сертификации продукции.

## Стек

- Python 3.11, aiogram 3.x, SQLAlchemy 2, PostgreSQL, Redis (FSM), Poetry, Loguru, Docker.

## Быстрый старт

1. Скопировать `.env.example` в `.env` и заполнить:
   - `BOT_TOKEN` — токен бота от @BotFather
   - `ADMIN_TELEGRAM_IDS` — ID менеджеров через запятую (уведомления о заявках)

2. **Запустить PostgreSQL и Redis** (нужны для бота):

   **Вариант A — через Docker** (нужен [Docker Desktop](https://www.docker.com/products/docker-desktop/) или Docker Engine):
   ```bash
   docker compose up -d postgres redis
   ```
   После этого в `.env` должны быть:
   - `DATABASE_URL=postgresql+asyncpg://certcost:certcost@localhost:5432/certcost`
   - `REDIS_URL=redis://localhost:6379/0`

   **Вариант B — без Docker:** установить и запустить [PostgreSQL](https://www.postgresql.org/download/windows/) и [Redis для Windows](https://github.com/microsoftarchive/redis/releases) (или WSL), затем прописать в `.env` свои хост/порт/логин/пароль.

3. Запуск бота локально:
   ```bash
   poetry install
   poetry run python main.py
   ```

4. Либо запустить всё (postgres + redis + bot) в Docker:
   ```bash
   docker compose up -d
   ```

## Сценарий бота

1. Выбор услуги (ТР ТС, Декларация, ISO, CE, Халяль, ТМ)
2. Страна производства (Россия, Китай, Турция, ЕС, Другая)
3. Тип продукции (текст или типовые категории)
4. Количество SKU
5. Срочность (30 / 14 / 7 дней)
6. Выезд эксперта (да/нет)
7. Итоговый расчёт с формулой
8. Оставить заявку (имя, телефон, email)

После заявки менеджеры получают уведомление с кнопками: «Взять в работу», «Закрыть», «Написать клиенту».

## Админ-команды

- `/stats` — расчёты, заявки, конверсия
- `/avg_check` — средний чек
- `/top_services` — топ услуг
- `/export_csv` — экспорт заявок в CSV

## Формула расчёта

```
Итог = (База × K_страна × K_SKU × K_срочность) + Выезд эксперта
```
Округление до 100 ₽ вверх, минимум 25 000 ₽.
