# Distributed Task Queue System

Async task queue backend built with **FastAPI**, **Celery**, **PostgreSQL**, **RabbitMQ**, and **Redis**.

## Architecture

| Component   | Role                                    |
|-------------|-----------------------------------------|
| FastAPI     | REST API (CRUD, health checks)          |
| Celery      | Distributed task worker                 |
| RabbitMQ    | Celery message broker                   |
| Redis       | Celery result backend + caching         |
| PostgreSQL  | Persistent task store (async SQLAlchemy)|
| Alembic     | Database migrations                     |

## Quick Start

```bash
# 1. Copy env file
cp .env.example .env

# 2. Start all services
docker compose up -d --build

# 3. Health check
curl http://localhost:8000/api/v1/health

# 4. Run tests
docker compose exec api pytest /app/backend/tests

# 5. Stop
docker compose down
```

## API Endpoints

| Method | Path                    | Description           |
|--------|-------------------------|-----------------------|
| GET    | `/api/v1/health`        | Health check          |
| POST   | `/api/v1/tasks`         | Create task           |
| GET    | `/api/v1/tasks`         | List tasks (filterable)|
| GET    | `/api/v1/tasks/{id}`    | Get task by ID        |
| PATCH  | `/api/v1/tasks/{id}`    | Update task           |
| DELETE | `/api/v1/tasks/{id}`    | Delete task           |

## Project Layout

```
backend/app/
├── main.py          # FastAPI app, lifespan, router wiring
├── config.py        # Environment-driven settings
├── db.py            # Async SQLAlchemy engine + session
├── models.py        # SQLAlchemy ORM models
├── schemas.py       # Pydantic validation schemas
├── celery_app.py    # Celery app with RabbitMQ + Redis
├── tasks.py         # Celery task definitions
├── routers/
│   ├── health.py    # Health endpoint
│   └── tasks.py     # Task CRUD endpoints
└── utils/
    └── retry.py     # Exponential-backoff retry decorator
```

## Development

```bash
# Install dependencies
cd backend && pip install -e ".[dev]"

# Lint
ruff check app/

# Type-check
mypy app/

# Run tests
pytest tests/ -v
```

## License

MIT