# tests/conftest.py
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Создает тестовую БД для каждого теста"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Тестовый клиент FastAPI"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    """Создает тестового пользователя и возвращает токен"""
    user_data = {"email": "test@example.com", "password": "SecurePass123!"}

    # Регистрируем пользователя
    client.post("/auth/register", json=user_data)

    # Логинимся и получаем токен
    response = client.post("/auth/login", json=user_data)
    return response.json()["access_token"]


@pytest.fixture
def test_suggestion(client, test_user):
    """Создает тестовое предложение"""
    headers = {"Authorization": f"Bearer {test_user}"}
    suggestion_data = {"title": "Test Suggestion", "text": "This is a test suggestion"}
    response = client.post("/suggestions", json=suggestion_data, headers=headers)
    return response.json()["id"]
