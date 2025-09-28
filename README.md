# SecDev Course Template

## Быстрый старт

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

## Запуск приложения
### Локальная разработка
```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload --port 8000
```

### Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Проверка работоспособности
```bash
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/items?name=test-item"
curl http://localhost:8000/items/1
```

## Тестирование
### Базовые тесты

```bash
pytest -q
pytest -v
pytest --cov=app
pytest tests/test_main.py -v
```

### Структура тестов

- test_main.py - тесты основных эндпойнтов
- test_health.py - тесты health-check
- conftest.py - фикстуры для тестирования

## Development
### Ритуал перед PR

```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

### CI
В репозитории настроен workflow CI (GitHub Actions)

### Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
docker compose up --build
```

## Эндпойнты

- GET /health → {"status": "ok"}
- POST /items?name=... — демо-сущность
- GET /items/{id}

## Формат ошибок
```bash
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: SECURITY.md, .pre-commit-config.yaml, .github/workflows/ci.yml.
