# tests/test_auth.py


class TestAuthentication:
    """Тесты аутентификации и регистрации"""

    # ПОЛОЖИТЕЛЬНЫЕ ТЕСТЫ

    def test_register_success(self, client):
        """Успешная регистрация пользователя"""
        user_data = {"email": "newuser@example.com", "password": "SecurePass123!"}

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 200
        assert "id" in response.json()
        assert response.json()["email"] == user_data["email"]
        assert "hashed_password" not in response.json()  # Пароль не возвращается

    def test_login_success(self, client):
        """Успешный вход в систему"""
        # Сначала регистрируем
        user_data = {"email": "loginuser@example.com", "password": "SecurePass123!"}
        client.post("/auth/register", json=user_data)

        # Потом логинимся
        response = client.post("/auth/login", json=user_data)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_get_current_user_success(self, client, test_user):
        """Успешное получение информации о текущем пользователе"""
        headers = {"Authorization": f"Bearer {test_user}"}
        response = client.get("/debug/my-info", headers=headers)

        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
        assert "id" in response.json()

    # ОТРИЦАТЕЛЬНЫЕ ТЕСТЫ

    def test_register_duplicate_email(self, client):
        """Регистрация с уже существующим email"""
        user_data = {"email": "duplicate@example.com", "password": "SecurePass123!"}

        # Первая регистрация - успешно
        client.post("/auth/register", json=user_data)

        # Вторая регистрация - должна быть ошибка
        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_wrong_password(self, client):
        """Вход с неверным паролем"""
        user_data = {"email": "wrongpass@example.com", "password": "SecurePass123!"}
        client.post("/auth/register", json=user_data)

        # Пробуем войти с неправильным паролем
        login_data = {"email": "wrongpass@example.com", "password": "WrongPassword123!"}
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_register_short_password(self, client):
        """Регистрация с коротким паролем"""
        user_data = {
            "email": "shortpass@example.com",
            "password": "123",  # Слишком короткий
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 400
        assert "8 characters" in response.json()["detail"].lower()
