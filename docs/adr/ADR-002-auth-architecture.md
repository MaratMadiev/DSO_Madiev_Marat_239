# ADR-002: Архитектура аутентификации и авторизации

## Context
Требуется система аутентификации, обеспечивающая анонимность предложений при сохранении контроля доступа. Пользователи должны управлять только своими предложениями, модераторы - видеть все.

## Decision
Реализовать JWT-based stateless аутентификацию с owner-only авторизацией:
- **JWT токены** с базовой валидацией (15 минут TTL)
- **User ID в токене** для проверки владения
- **404 для чужих данных** (security through obscurity)
- **Ролевая модель**: User, Moderator

## Alternatives
- **Session-based**: Stateful, сложнее масштабировать
- **OAuth2**: Избыточно для MVP

## Consequences
**Positive**: Простота реализации, масштабируемость, четкие права доступа
**Negative**: Короткий TTL токенов, ручное управление сессиями

## Security Impact
- **Угрозы**: Spoofing (SEC-NFR-001), Elevation of Privilege (SEC-NFR-003)
- **Контрмеры**: JWT signature validation, user_id проверка в каждом запросе
- **Риски**: R1, R4 - покрыты базовой реализацией

## Rollout Plan
1. Модели User/Role в БД
2. JWT middleware для FastAPI
3. Декораторы авторизации (@require_owner, @require_moderator)
4. Интеграция с эндпоинтами предложений

## Links
- NFR: SEC-NFR-001, SEC-NFR-003, SEC-NFR-004
- STRIDE: F1, F2 Spoofing; F5 Elevation of Privilege
- Потоки: F3, F4 (API с JWT), F5 (SQL с user_id)