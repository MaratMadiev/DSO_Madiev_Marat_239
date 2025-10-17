# STRIDE - Анализ угроз для Suggestion Box

| Поток/Элемент | Угроза | Описание угрозы | Контрмеры | Ссылка на NFR | Проверка |
|---|---|---|---|---|---|
| **F1, F2** | **Spoofing** | Злоумышленник выдает себя за легитимного пользователя | JWT токены, сессионные cookie, многофакторная аутентификация | SEC-NFR-001 | Auth penetration testing |
| **F1, F2** | **Tampering** | Изменение данных в транзите (MITM) | HTTPS/TLS, цифровые подписи, проверка целостности | SEC-NFR-006 | SSL/TLS configuration scan |
| **F3, F4** | **Information Disclosure** | Перехват конфиденциальных данных через API | Шифрование, маскирование данных, безопасные заголовки | SEC-NFR-006 | Security headers audit |
| **F3, F4** | **Denial of Service** | DDoS-атака на API эндпоинты | Rate limiting, WAF, мониторинг трафика | SEC-NFR-005 | Load and stress testing |
| **F5** | **Elevation of Privilege** | SQL injection для получения прав | Parameterized queries, ORM, input validation | SEC-NFR-003 | SQL injection testing |
| **F5** | **Information Disclosure** | Утечка данных через неправильные запросы | Query validation, минимальные привилегии БД | SEC-NFR-006 | Database access audit |
| **F6** | **Tampering** | Несанкционированное изменение файлов | File integrity checks, цифровые подписи | SEC-NFR-006 | File system permissions audit |
| **F6** | **Information Disclosure** | Несанкционированный доступ к файлам | File permissions, шифрование файлов | SEC-NFR-006 | Access control testing |
| **FastAPI Application** | **Repudiation** | Отказ от действий в системе | Audit logs, временные метки, цифровые подписи | SEC-NFR-007 | Audit trail verification |
| **Database** | **Information Disclosure** | Прямой доступ к БД минуя приложение | Шифрование БД, сетевые ACL, мониторинг | SEC-NFR-006 | Database security assessment |
