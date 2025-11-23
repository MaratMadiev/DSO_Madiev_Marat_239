# tests/test_security.py


class TestSecurity:
    """Тесты безопасности и граничных случаев"""

    # ПОЛОЖИТЕЛЬНЫЕ ТЕСТЫ (Security)

    def test_password_not_exposed_in_responses(self, client):
        """Пароль не раскрывается в ответах API"""
        user_data = {"email": "security@example.com", "password": "SecurePass123!"}

        response = client.post("/auth/register", json=user_data)
        user_response = response.json()

        # Проверяем что пароль не возвращается
        assert "password" not in user_response
        assert "hashed_password" not in user_response
        assert user_response["email"] == user_data["email"]

    def test_owner_only_policy_working(self, client, test_user, test_suggestion):
        """Owner-only политика работает корректно"""
        headers = {"Authorization": f"Bearer {test_user}"}

        # Пользователь может получить свое предложение
        response = client.get(f"/suggestions/{test_suggestion}", headers=headers)
        assert response.status_code == 200

        # Пользователь может обновить свое предложение
        update_response = client.put(
            f"/suggestions/{test_suggestion}",
            json={"title": "Updated Title"},
            headers=headers,
        )
        assert update_response.status_code == 200

    def test_jwt_token_required_for_protected_endpoints(self, client):
        """JWT токен требуется для защищенных эндпоинтов"""
        response = client.post("/suggestions", json={"title": "Test", "text": "Test"})

        # Должна быть ошибка авторизации
        assert response.status_code in [401, 422]

    # ОТРИЦАТЕЛЬНЫЕ ТЕСТЫ (Security)

    def test_invalid_jwt_token_rejected(self, client):
        """Невалидный JWT токен отклоняется"""
        headers = {"Authorization": "Bearer invalid_token_here"}

        response = client.get("/suggestions/1", headers=headers)

        assert response.status_code == 401
        assert "credentials" in response.json()["detail"].lower()

    def test_malformed_authorization_header(self, client):
        """Некорректный заголовок Authorization отклоняется"""
        # Без Bearer
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

        response = client.get("/suggestions/1", headers=headers)

        assert response.status_code == 401

    def test_sql_injection_attempt_blocked(self, client, test_user):
        """Попытка SQL инъекции блокируется"""
        headers = {"Authorization": f"Bearer {test_user}"}

        injection_attempt = {
            "title": "Test'; DROP TABLE users; --",
            "text": "SQL injection attempt",
        }

        response = client.post("/suggestions", json=injection_attempt, headers=headers)

        # Правильные проверки:
        assert response.status_code != 500

        assert response.status_code in [200, 201, 422, 400]

        if response.status_code == 200:
            data = response.json()

            assert data["title"] == injection_attempt["title"]
            # users_response = client.get("/debug/users", headers=headers)# если есть такой эндпоинт
