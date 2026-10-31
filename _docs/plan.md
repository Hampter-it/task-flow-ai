# TaskFlow API — учебный backend-проект

Цель: пройти путь разработки backend-приложения в порядке, в котором его обычно строят на практике: от Git и первого endpoint до PostgreSQL, SQLAlchemy, Alembic, Docker и тестов.

## Технологии

- Python 3.13+
- FastAPI — REST API
- PostgreSQL — реляционная база данных
- SQLAlchemy 2.0 — ORM
- Alembic — миграции базы данных
- Pydantic — валидация запросов и ответов
- `uv` — зависимости и запуск проекта
- Docker + Docker Compose — контейнеры
- Git — ветки, коммиты, merge
- pytest + HTTPX — тестирование

## План разработки

1. Создать репозиторий и первый endpoint.
2. Запустить PostgreSQL через Docker Compose.
3. Подключить SQLAlchemy и описать модель `Task`.
4. Добавить миграции Alembic.
5. Реализовать CRUD API.
6. Контейнеризировать API.
7. Добавить тесты.
8. Самостоятельно реализовать фильтрацию в отдельной Git-ветке.

---

## Этап 0. Подготовить окружение

Установи Python, Git, Docker Desktop (или Docker Engine) и `uv`. Проверь установку:

```bash
python --version
git --version
docker --version
docker compose version
uv --version
```

Создай проект:

```bash
mkdir taskflow
cd taskflow

git init -b main
uv init --package taskflow

uv add fastapi "uvicorn[standard]"
uv add sqlalchemy "psycopg[binary]" pydantic-settings alembic
uv add --dev pytest httpx

git status
```

Что нужно понять:

- `uv init --package` создаёт пакет Python с исходным кодом в `src/`.
- `uv add` добавляет зависимости и обновляет `pyproject.toml` и `uv.lock`.
- `--dev` добавляет зависимости, необходимые для разработки и тестов.
- `git init -b main` создаёт репозиторий с основной веткой `main`.

Открой `pyproject.toml` и посмотри, что находится в `src/taskflow/`.

## Этап 1. Первый endpoint FastAPI

Создай ветку:

```bash
git switch -c feature/health-endpoint
```

Открой `src/taskflow/main.py` и напиши:

```python
from fastapi import FastAPI

app = FastAPI(title="TaskFlow API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

Запусти сервер:

```bash
uv run uvicorn taskflow.main:app --reload
```

Проверь:

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

Сохрани изменения в Git:

```bash
git status
git add pyproject.toml uv.lock src/
git commit -m "feat: add health endpoint"
git switch main
git merge --no-ff feature/health-endpoint
```

Ветка `feature/health-endpoint` — отдельная работа над одной функцией. После её завершения мы возвращаемся в `main` и объединяем изменения через merge.

## Этап 2. PostgreSQL через Docker Compose

Создай ветку:

```bash
git switch -c feature/postgres
```

Создай `compose.yaml` в корне проекта:

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: taskflow
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: taskflow_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskflow -d taskflow"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Запусти базу и посмотри логи:

```bash
docker compose up -d db
docker compose ps
docker compose logs db
```

Если установлен `psql`, проверь подключение:

```bash
psql "postgresql://taskflow:taskflow_dev@localhost:5432/taskflow"
```

Внутри выполни:

```sql
SELECT version();
\q
```

Сохрани конфигурацию:

```bash
git add compose.yaml
git commit -m "feat: add PostgreSQL service"
git switch main
git merge --no-ff feature/postgres
```

Что важно:

- `image` задаёт образ PostgreSQL.
- `ports` публикует порт базы на компьютере.
- `volumes` сохраняет данные между перезапусками контейнера.
- `healthcheck` проверяет готовность базы принимать подключения.

Пароль `taskflow_dev` годится только для локального учебного проекта. Не используй такие пароли в production.

## Этап 3. Настройки приложения

Создай ветку:

```bash
git switch -c feature/database-model
```

Создай `src/taskflow/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://taskflow:taskflow_dev@localhost:5432/taskflow"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
```

Создай `.env` в корне:

```dotenv
DATABASE_URL=postgresql+psycopg://taskflow:taskflow_dev@localhost:5432/taskflow
```

Создай `.env.example` с такой же строкой, чтобы другим разработчикам было понятно, какие настройки нужны.

Добавь в `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.py[cod]
```

Не коммить `.env`: он предназначен для локальных настроек и может содержать секреты.

## Этап 4. Подключение SQLAlchemy

Создай `src/taskflow/database.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from taskflow.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

Разберись с понятиями:

- `engine` управляет подключениями к базе.
- `SessionLocal` создаёт сессии, через которые выполняются запросы.
- `get_db()` — dependency FastAPI, которая предоставляет сессию endpoint и закрывает её после запроса.

Здесь используется синхронный SQLAlchemy. Для первого проекта это проще, чем сразу изучать асинхронный стек.

## Этап 5. Модель Task

Создай `src/taskflow/models.py`:

```python
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
```

Это описание таблицы, но пока не сама таблица. Alembic создаст её в PostgreSQL.

Обрати внимание:

- `Mapped[int]` описывает тип поля.
- `mapped_column()` задаёт параметры столбца.
- `nullable=False` запрещает `NULL`.
- `server_default=func.now()` задаёт время на стороне базы.

## Этап 6. Миграции Alembic

Инициализируй Alembic:

```bash
uv run alembic init migrations
```

В `alembic.ini` найди `prepend_sys_path` и установи:

```ini
prepend_sys_path = %(here)s/src
```

В `migrations/env.py` найди импорт `target_metadata` и настройку метаданных. Добавь импорты и настройку ниже, сохранив остальную структуру файла, созданного Alembic:

```python
from taskflow.config import settings
from taskflow.database import Base
from taskflow import models  # noqa: F401

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%"),
)

target_metadata = Base.metadata
```

Важно, чтобы `models` импортировался: так SQLAlchemy зарегистрирует модель `Task` в метаданных.

Создай миграцию:

```bash
uv run alembic revision --autogenerate -m "create tasks table"
```

Открой файл в `migrations/versions/` и проверь, что Alembic обнаружил таблицу `tasks`, её столбцы и первичный ключ.

Примени миграцию и проверь версию:

```bash
uv run alembic upgrade head
uv run alembic current
```

Если миграция не видит `Task`, проверь импорт `models` и значение `target_metadata`.

## Этап 7. Pydantic-схемы

Создай `src/taskflow/schemas.py`:

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    is_completed: bool | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

Зачем отдельные схемы:

- `TaskCreate` — что клиент может отправить при создании.
- `TaskUpdate` — какие поля можно менять.
- `TaskRead` — какие данные API возвращает клиенту.

Не принимай SQLAlchemy-модель напрямую из запроса. Pydantic проверяет входные данные и отделяет публичный API от внутреннего представления базы.

## Этап 8. CRUD endpoints

Создай каталог `src/taskflow/routers/` и пустой файл `src/taskflow/routers/__init__.py`.

Создай `src/taskflow/routers/tasks.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from taskflow.database import get_db
from taskflow.models import Task
from taskflow.schemas import TaskCreate, TaskRead, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["Tasks"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(payload: TaskCreate, db: DbSession) -> Task:
    task = Task(
        title=payload.title,
        description=payload.description,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    db: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Task]:
    statement = (
        select(Task)
        .order_by(Task.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: DbSession) -> Task:
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: DbSession,
) -> Task:
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    changes = payload.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DbSession) -> Response:
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

Обрати внимание на `payload.model_dump(exclude_unset=True)`: он позволяет отличить поле, которое клиент не передал, от поля, которое клиент явно хочет изменить на `null`.

Для `PATCH` это важно. Если клиент передал только `is_completed`, заголовок и описание не должны случайно сброситься.

## Этап 9. Подключение роутера

Замени содержимое `src/taskflow/main.py`:

```python
from fastapi import FastAPI

from taskflow.routers import tasks


app = FastAPI(
    title="TaskFlow API",
    version="0.1.0",
)

app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

Запусти сервер:

```bash
uv run uvicorn taskflow.main:app --reload
```

Открой Swagger: http://127.0.0.1:8000/docs

Проверь сценарий:

1. `POST /tasks` — создай задачу с заголовком `Learn FastAPI`.
2. `GET /tasks` — получи список.
3. `GET /tasks/1` — получи задачу по ID `1`, если он действительно назначен этой задаче.
4. `PATCH /tasks/1` — установи `is_completed` в `true`.
5. `DELETE /tasks/1` — удали её.
6. Повтори `GET /tasks/1` — ожидай `404`.

Сохрани изменения в Git:

```bash
git add src/taskflow
git commit -m "feat: implement task CRUD endpoints"
git switch main
git merge --no-ff feature/tasks-crud
```

Если работа над CRUD ещё не находится в отдельной ветке, перед началом этапа создай её:

```bash
git switch main
git switch -c feature/tasks-crud
```

## Этап 10. Dockerfile

До этого FastAPI запускался непосредственно на компьютере. Теперь сделаем так, чтобы его можно было запускать в контейнере, а PostgreSQL — в отдельном контейнере.

Создай ветку:

```bash
git switch main
git switch -c feature/docker
```

Создай `Dockerfile` в корне проекта:

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "taskflow.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Что нужно понять:

- `FROM` выбирает базовый образ.
- `WORKDIR` задаёт рабочую директорию контейнера.
- `COPY` переносит файлы в образ.
- `uv sync --frozen --no-dev` устанавливает зависимости по lock-файлу, не меняя его, и не устанавливает dev-зависимости.
- `0.0.0.0` позволяет приложению принимать подключения через опубликованный порт контейнера.

Если в проекте нет `README.md`, создай его или убери соответствующую строку `COPY`.

## Этап 11. Добавляем API в Compose

Замени `compose.yaml` на следующую версию:

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: taskflow
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: taskflow_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskflow -d taskflow"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://taskflow:taskflow_dev@db:5432/taskflow
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
```

Разница в адресах:

- Когда Python запускается на компьютере: `localhost:5432`.
- Когда API запускается внутри Compose: `db:5432`.

В сети Docker Compose имя `db` — имя сервиса. `localhost` внутри API-контейнера указывал бы на сам API-контейнер, а не на PostgreSQL.

Создай `.dockerignore`:

```dockerignore
.git
.venv
__pycache__
.pytest_cache
.env
*.py[cod]
```

Собери и запусти:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Примени миграции внутри контейнера API:

```bash
docker compose run --rm api alembic upgrade head
```

Проверь:

- http://localhost:8000/health
- http://localhost:8000/docs

Создай задачу через Swagger и перезапусти контейнеры:

```bash
docker compose restart
```

Снова запроси список задач. Если всё настроено правильно, задача останется в PostgreSQL благодаря Docker volume.

Команды для диагностики:

```bash
docker compose logs -f api
docker compose logs -f db
docker compose down
docker compose up -d
```

`docker compose down` по умолчанию удаляет контейнеры, но не именованный volume. Не используй `docker compose down -v`, если хочешь сохранить учебную базу.

Сохрани изменения:

```bash
git add Dockerfile .dockerignore compose.yaml
git commit -m "feat: containerize API and database"
git switch main
git merge --no-ff feature/docker
```

## Этап 12. Автоматические тесты

API, который работает вручную, ещё не обязательно надёжен. Добавим автоматические проверки.

Создай ветку:

```bash
git switch main
git switch -c feature/tests
```

Создай `tests/test_tasks.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from taskflow.database import Base, get_db
from taskflow.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_create_and_get_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn SQLAlchemy",
            "description": "Practice ORM",
        },
    )

    assert response.status_code == 201

    created_task = response.json()
    assert created_task["title"] == "Learn SQLAlchemy"
    assert created_task["is_completed"] is False

    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Learn Docker"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"is_completed": True},
    )

    assert response.status_code == 200
    assert response.json()["is_completed"] is True
    assert response.json()["title"] == "Learn Docker"


def test_missing_task_returns_404(client):
    response = client.get("/tasks/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_empty_title_is_rejected(client):
    response = client.post(
        "/tasks",
        json={"title": ""},
    )

    assert response.status_code == 422
```

Здесь SQLite используется только для тестов, чтобы они были изолированными и не зависели от работающего PostgreSQL. В приложении остаётся PostgreSQL.

Запусти тесты:

```bash
uv run pytest -v
```

Сохрани результат:

```bash
git add tests/
git commit -m "test: cover task API endpoints"
git switch main
git merge --no-ff feature/tests
```

## Этап 13. Проверяем Git

Посмотри на историю:

```bash
git switch main
git log --oneline --graph --decorate --all
git branch
git status
```

Ветки проекта:

```text
main
feature/health-endpoint
feature/postgres
feature/database-model
feature/tasks-crud
feature/docker
feature/tests
```

Каждая ветка отвечает за отдельную задачу. Мы не делали всю программу одним огромным коммитом — каждая функция развивалась отдельно.

## Этап 14. Самостоятельная функция: фильтрация задач

Попробуй самостоятельно реализовать фильтрацию задач по статусу.

Создай ветку:

```bash
git switch main
git switch -c feature/filter-tasks
```

Добавь в `GET /tasks` параметр `is_completed`, чтобы можно было вызывать:

```text
GET /tasks?is_completed=true
GET /tasks?is_completed=false
```

Подсказка: используй `select(Task)` и добавляй `.where(Task.is_completed == is_completed)`, если параметр был передан.

После этого:

1. Проверь оба варианта через Swagger.
2. Добавь тесты.
3. Сделай коммит.
4. Переключись на `main`.
5. Выполни merge.

Это будет первая самостоятельная feature-ветка.

## Итоговая структура проекта

```text
taskflow/
├── .dockerignore
├── .env                  # локальный файл, не коммитить
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
├── alembic.ini
├── pyproject.toml
├── uv.lock
├── README.md
├── migrations/
│   ├── env.py
│   └── versions/
├── src/
│   └── taskflow/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       └── routers/
│           ├── __init__.py
│           └── tasks.py
└── tests/
    └── test_tasks.py
```

## Что добавить после основной версии

| Следующий шаг | Чему научишься |
|---|---|
| Фильтрация и пагинация | SQLAlchemy `where`, `order_by`, `limit` |
| Service-слой | Разделение бизнес-логики и HTTP |
| Пользователи и авторизация | JWT, хеширование паролей, зависимости FastAPI |
| Связь задач с пользователями | Foreign keys, relationships, JOIN |
| Более строгие тесты | PostgreSQL для интеграционных тестов |
| CI через GitHub Actions | Автоматический запуск тестов при push |
| Логирование и обработка ошибок | Практики production backend |

## Рекомендуемый учебный цикл

Для каждого этапа:

1. Прочитай код и попробуй объяснить, что делает каждая функция.
2. Напиши его самостоятельно, не подглядывая в готовый вариант.
3. Запусти программу и проверь поведение.
4. Намеренно сломай что-нибудь и найди причину.
5. Сделай коммит только после проверки.

**Первое задание:** реализуй этапы 0–2 и добейся, чтобы `/health` отвечал `{"status": "ok"}`, а PostgreSQL запускался через Docker Compose. Не переходи к SQLAlchemy, пока не поймёшь, как работают `uv`, первый endpoint и контейнер базы.

## Улучшения перед production

Учебная версия не готова для production без дополнительной работы. Следующие полезные задачи:

- корректно обрабатывать ошибки транзакций и делать rollback;
- запретить `null` для обязательного `title` в `PATCH`;
- добавить ограничения для описания;
- безопасно хранить секреты и не коммитить `.env`;
- закрепить версии базовых Docker-образов;
- использовать PostgreSQL для интеграционных тестов;
- добавить CI, линтер и форматтер;
- продумать аутентификацию, авторизацию, логирование и миграции при деплое.
