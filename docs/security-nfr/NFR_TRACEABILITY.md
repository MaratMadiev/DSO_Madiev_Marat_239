# Матрица трассировки NFR ↔ Stories/Tasks

## Легенда приоритетов:
- **P0** - Критический (должен быть в MVP)
- **P1** - Высокий (должен быть в Release 1)
- **P2** - Средний (может быть в Release 2)

## Матрица трассировки:

| NFR ID | User Story / Task | Приоритет | Релизное окно | Комментарии |
|--------|-------------------|-----------|---------------|-------------|
| **SEC-NFR-001** | **US-001**: Как пользователь, я хочу регистрироваться в системе |  P0 | MVP | Базовая аутентификация |
| **SEC-NFR-001** | **US-002**: Как пользователь, я хочу входить в систему |  P0 | MVP | Логин/логаут |
| **SEC-NFR-002** | **TASK-011**: Реализовать хэширование паролей |  P0 | MVP | Argon2id implementation |
| **SEC-NFR-003** | **US-005**: Как пользователь, я хочу видеть только свои предложения |  P1 | Release 1 | Owner-only политика |
| **SEC-NFR-003** | **US-006**: Как пользователь, я хочу редактировать свои предложения |  P1 | Release 1 | Authorization checks |
| **SEC-NFR-004** | **TASK-015**: Реализовать JWT токены |  P1 | Release 1 | Token management |
| **SEC-NFR-005** | **TASK-021**: Настроить rate limiting |  P2 | Release 2 | Защита от brute-force |
| **SEC-NFR-006** | **TASK-025**: Настроить HTTPS/TLS |  P0 | MVP | Production security |
| **SEC-NFR-007** | **US-010**: Как админ, я хочу видеть логи безопасности |  P2 | Release 2 | Monitoring & Audit |
| **SEC-NFR-008** | **TASK-031**: Настроить security scanning в CI/CD | P2 | Release 2 | DevSecOps |

## План внедрения по релизам:

### MVP (Minimum Viable Product)
- SEC-NFR-001: Базовая аутентификация
- SEC-NFR-002: Защита паролей
- SEC-NFR-006: HTTPS/TLS
- SEC-NFR-003: Basic owner checks
- SEC-NFR-007: Базовое логирование

### Release 1
- SEC-NFR-004: JWT tokens с TTL
- SEC-NFR-003: Полная авторизация

### Release 2
- SEC-NFR-005: Rate limiting
- SEC-NFR-007: Расширенный мониторинг
- SEC-NFR-008: Security scanning
