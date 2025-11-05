# ADR-003: Стратегия защиты данных и коммуникаций
Дата: 2025-10-21

## Context
Система обрабатывает PII (учетные данные) и пользовательский контент (предложения). Необходимо обеспечить конфиденциальность и целостность данных как в хранилище, так и при передаче.

## Decision
Реализовать многоуровневую защиту данных:
1. **Transport**: HTTPS/TLS для всех внешних коммуникаций
2. **Storage**: Argon2id для паролей, подготовка к шифрованию БД
3. **Application**: Parameterized queries, input validation
4. **Infrastructure**: Network segmentation (зоны доверия)

## Alternatives
- **Full Encryption**: Шифрование всей БД - избыточно для MVP
- **No Encryption**: Только TLS - риск утечек при компрометации БД

## Consequences
**Positive**: Защита от основных векторов атак, соответствие best practices
**Negative**: Сложность конфигурации, необходимость управления сертификатами

## Security Impact
- **Угрозы**: Tampering (F1, F2), Information Disclosure (F3-F6)
- **Контрмеры**: TLS, хэширование, ORM, валидация
- **Риски**: R1, R2, R5, R8 - существенно снижены

## Rollout Plan
1. Настройка reverse proxy с TLS терминацией
2. Миграция на Argon2id для существующих паролей
3. Внедрение SQLAlchemy ORM везде
4. Настройка файловых permissions для F6

## Links
- NFR: SEC-NFR-002, SEC-NFR-006
- STRIDE: F1, F2 Tampering; F3, F4 Information Disclosure; F5, F6 Various
- Риски: R1, R2, R5, R8, R10
- DFD: Все потоки F1-F6