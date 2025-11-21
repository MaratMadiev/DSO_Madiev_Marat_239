# tests/test_suggestions.py


class TestSuggestions:
    """Тесты работы с предложениями"""

    # ПОЛОЖИТЕЛЬНЫЕ ТЕСТЫ

    def test_create_suggestion_success(self, client, test_user):
        """Успешное создание предложения"""
        headers = {"Authorization": f"Bearer {test_user}"}
        suggestion_data = {
            "title": "New Feature Request",
            "text": "Please add dark mode to the application",
        }

        response = client.post("/suggestions", json=suggestion_data, headers=headers)

        assert response.status_code == 200
        assert response.json()["title"] == suggestion_data["title"]
        assert response.json()["status"] == "pending"
        assert "id" in response.json()
        assert "user_id" in response.json()

    def test_get_own_suggestion_success(self, client, test_user, test_suggestion):
        """Успешное получение своего предложения"""
        headers = {"Authorization": f"Bearer {test_user}"}

        response = client.get(f"/suggestions/{test_suggestion}", headers=headers)

        assert response.status_code == 200
        assert response.json()["id"] == test_suggestion
        assert response.json()["title"] == "Test Suggestion"

    def test_get_suggestions_list_anonymous(self, client, test_user):
        """Анонимное получение списка предложений"""
        # Создаем предложение
        headers = {"Authorization": f"Bearer {test_user}"}
        client.post(
            "/suggestions",
            json={
                "title": "Public Suggestion",
                "text": "This should be visible to everyone",
            },
            headers=headers,
        )

        # Получаем список без авторизации
        response = client.get("/suggestions")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    # ОТРИЦАТЕЛЬНЫЕ ТЕСТЫ

    def test_create_suggestion_unauthorized(self, client):
        """Попытка создания предложения без авторизации"""
        suggestion_data = {
            "title": "Unauthorized Suggestion",
            "text": "This should fail",
        }

        response = client.post("/suggestions", json=suggestion_data)
        # Должен быть 401, но FastAPI может вернуть 422 из-за отсутствия зависимости
        assert response.status_code in [401, 422]

    def test_get_others_suggestion_forbidden(self, client, test_user):
        """Попытка получения чужого предложения"""
        # Создаем второго пользователя
        user2_data = {"email": "user2@example.com", "password": "SecurePass123!"}
        client.post("/auth/register", json=user2_data)
        user2_login = client.post("/auth/login", json=user2_data)
        user2_token = user2_login.json()["access_token"]

        # user2 создает предложение
        headers2 = {"Authorization": f"Bearer {user2_token}"}
        suggestion_response = client.post(
            "/suggestions",
            json={"title": "User2 Suggestion", "text": "This belongs to user2"},
            headers=headers2,
        )
        suggestion_id = suggestion_response.json()["id"]

        # user1 пытается получить предложение user2
        headers1 = {"Authorization": f"Bearer {test_user}"}
        response = client.get(f"/suggestions/{suggestion_id}", headers=headers1)

        assert response.status_code == 403
        assert "permissions" in response.json()["detail"].lower()

    def test_update_suggestion_unauthorized(self, client, test_user):
        """Попытка обновления чужого предложения"""
        # Создаем второго пользователя
        user2_data = {"email": "user3@example.com", "password": "SecurePass123!"}
        client.post("/auth/register", json=user2_data)
        user2_login = client.post("/auth/login", json=user2_data)
        user2_token = user2_login.json()["access_token"]

        # user2 создает предложение
        headers2 = {"Authorization": f"Bearer {user2_token}"}
        suggestion_response = client.post(
            "/suggestions",
            json={"title": "User2 Suggestion", "text": "This belongs to user2"},
            headers=headers2,
        )
        suggestion_id = suggestion_response.json()["id"]

        # user1 пытается обновить предложение user2
        headers1 = {"Authorization": f"Bearer {test_user}"}
        update_data = {"title": "Hacked Title"}
        response = client.put(
            f"/suggestions/{suggestion_id}", json=update_data, headers=headers1
        )

        assert response.status_code == 403
