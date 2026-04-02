# async-payment-service

Асинхронный сервис процессинга платежей

## Стек

- **FastAPI** + **Pydantic v2** — API
- **SQLAlchemy 2.0** (async) + **PostgreSQL** — хранилище
- **RabbitMQ** + **FastStream** — брокер сообщений
- **Alembic** — миграции
- **Docker** + **docker-compose** — окружение

## Архитектура
```
POST /payments
    ↓
API: сохраняет Payment + OutboxEvent в одной транзакции
    ↓
Outbox Worker: читает OutboxEvent → публикует в RabbitMQ
    ↓
Consumer: обрабатывает платёж → обновляет статус → отправляет webhook
```

## Структура проекта
```
src/
├── api/v1/          # эндпоинты
├── common/          # auth, config, enums, constants
├── db/
│   └── models/      # Payment, Outbox
├── repositories/    # слой работы с БД
├── schemas/         # Pydantic схемы
├── services/        # бизнес логика
├── workers/         # outbox worker
├── broker.py        # FastStream брокер
├── consumer.py      # обработчик очереди
└── main.py          # точка входа API
```

## Запуск

### Требования

- Docker
- Docker Compose

### 1. Клонировать репозиторий
```bash
git clone https://github.com/username/async-payment-service.git
cd async-payment-service
```

### 2. Настроить переменные окружения
```bash
cp .env.example .env
```

### 3. Запустить
```bash
docker-compose up -d --build
```

### 4. Применить миграции
```bash
docker-compose exec api alembic upgrade head
```

### 5. Проверить

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672 (guest/guest)

## API

Все эндпоинты требуют заголовок `X-API-Key`.

### Создание платежа
```
POST /api/v1/payments/
```

Заголовки:
```
X-API-Key: your-api-key
Idempotency-Key: unique-key
```

Тело запроса:
```json
{
  "amount": "100.00",
  "currency": "RUB",
  "description": "Оплата заказа #123",
  "metadata": {"order_id": "123"},
  "webhook_url": "https://example.com/webhook"
}
```

Ответ `202 Accepted`:
```json
{
  "payment_id": "uuid",
  "status": "pending",
  "created_at": "2026-01-01T00:00:00Z"
}
```

### Получение платежа
```
GET /api/v1/payments/{payment_id}
```

Ответ `200 OK`:
```json
{
  "id": "uuid",
  "amount": "100.00",
  "currency": "RUB",
  "description": "Оплата заказа #123",
  "metadata": {"order_id": "123"},
  "status": "succeeded",
  "idempotency_key": "unique-key",
  "webhook_url": "https://example.com/webhook",
  "created_at": "2026-01-01T00:00:00Z",
  "processed_at": "2026-01-01T00:00:05Z"
}
```

## Тесты
```bash
pytest
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DATABASE_URL` | URL PostgreSQL | — |
| `RABBITMQ_URL` | URL RabbitMQ | — |
| `API_KEY` | Статический ключ аутентификации | — |
| `DB_POOL_SIZE` | Размер пула соединений | `5` |
| `MAX_WEBHOOK_RETRIES` | Попыток доставки webhook | `3` |
| `MAX_CONSUMER_RETRIES` | Попыток обработки сообщения | `3` |
