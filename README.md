# CertCost Pro - Telegram бот расчета стоимости сертификации

Бот автоматизирует расчет стоимости услуг сертификации и сбор заявок от клиентов.

## Что внутри

- Python 3.11
- aiogram 3.x
- SQLAlchemy 2 async
- PostgreSQL
- Redis для FSM
- Poetry
- Docker и Docker Compose

## Архитектура

- Бот работает через `aiogram` и хранит состояния диалога в Redis.
- Бизнес-данные и заявки сохраняются в PostgreSQL через SQLAlchemy async.
- Контейнерная схема включает 3 сервиса: `bot`, `postgres`, `redis`.

## Переменные окружения

Базовый шаблон находится в `.env.example`.

- `BOT_TOKEN` - токен Telegram бота
- `DATABASE_URL` - строка подключения к PostgreSQL
- `REDIS_URL` - строка подключения к Redis
- `ADMIN_TELEGRAM_IDS` - Telegram ID менеджеров через запятую
- `LOG_LEVEL` - уровень логирования

Пример `DATABASE_URL`:

```bash
postgresql+asyncpg://certcost:certcost@localhost:5432/certcost
```

## Локальный запуск без Docker

1. Скопируйте `.env.example` в `.env`.
2. Поднимите PostgreSQL и Redis локально.
3. Установите зависимости и запустите бота:

```bash
poetry install
poetry run python main.py
```

## Запуск через Docker Compose

1. Скопируйте `.env.example` в `.env`.
2. Запустите проект:

```bash
docker compose up -d --build
```

3. Проверьте состояние контейнеров:

```bash
docker compose ps
```

4. Просмотр логов бота:

```bash
docker compose logs -f bot
```

## Проверка Postgres и FSM Redis

- PostgreSQL используется как основная БД и подключается через `DATABASE_URL`.
- FSM хранится в Redis через `RedisStorage`.
- При запуске контейнеров `postgres` и `redis` должны быть в статусе healthy.

Проверить Redis:

```bash
docker compose exec redis redis-cli ping
```

Проверить PostgreSQL:

```bash
docker compose exec postgres pg_isready -U certcost
```

## Основной сценарий бота

1. Выбор услуги
2. Выбор страны
3. Выбор или ввод типа продукции
4. Ввод количества SKU
5. Выбор срочности
6. Подтверждение выезда эксперта
7. Получение расчета
8. Отправка заявки с контактами

## Админ команды

- `/stats` - расчеты, заявки, конверсия
- `/avg_check` - средний чек
- `/top_services` - топ услуг
- `/export_csv` - экспорт заявок в CSV

## GitHub deploy

### Что должно быть настроено

- GitHub Actions для CI
- GitHub Actions для release сборки Docker образа
- GitHub Secrets с обязательными переменными
- Environments для `staging` и `production` при необходимости

### Обязательные секреты

- `BOT_TOKEN`
- `DATABASE_URL`
- `REDIS_URL`
- `ADMIN_TELEGRAM_IDS`

### Базовый процесс

1. Push в ветку или Pull Request запускает CI.
2. CI проверяет код и сборку Docker образа.
3. Release workflow собирает и публикует Docker образ.
4. Целевая инфраструктура забирает новый образ и перезапускает сервис.

## Эксплуатация

- Логи приложения пишутся в `logs/`.
- Для контейнерного режима используйте `docker compose logs`.
- Рекомендуется ежедневный backup PostgreSQL на стороне хоста.
- Для production храните секреты только в менеджере секретов или GitHub Secrets.

## Troubleshooting

- Если бот не стартует, проверьте `BOT_TOKEN` и доступ к Telegram API.
- Если есть ошибки БД, проверьте корректность `DATABASE_URL` и доступность PostgreSQL.
- Если не работает FSM, проверьте `REDIS_URL` и ответ `PONG` от Redis.
- Если не приходят админ уведомления, проверьте `ADMIN_TELEGRAM_IDS`.
