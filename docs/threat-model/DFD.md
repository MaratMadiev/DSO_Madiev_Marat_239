# Data Flow Diagram (DFD) - Suggestion Box System

## Контекстная диаграмма системы

```mermaid
graph TD
    subgraph External [Внешняя зона - Недоверенная]
        A[Пользователь<br/>User]
        B[Модератор<br/>Moderator]
    end

    subgraph Trust_Boundary_1 [Периметровая зона]
        C[Веб-браузер<br/>Web Browser]
        D[Мобильное приложение<br/>Mobile App]
    end

    subgraph Trust_Boundary_2 [Зона приложения]
        E[FastAPI Application<br/>Бэкенд сервис]
    end

    subgraph Trust_Boundary_3 [Зона данных]
        F[(База данных<br/>PostgreSQL/SQLite)]
        G[Файловое хранилище<br/>File Storage]
    end

    %% Потоки данных
    A -- F1: HTTPS/TLS --> C
    B -- F2: HTTPS/TLS --> D
    C -- F3: REST API/HTTPS --> E
    D -- F4: REST API/HTTPS --> E
    E -- F5: SQL Queries --> F
    E -- F6: File System API --> G
```

## Список потоков данных

| ID | Откуда → Куда | Протокол/Интерфейс | Данные/PII | Комментарий |
|---|---|---|---|---|
| F1 | User → Web Browser | HTTPS/TLS | Учетные данные, JWT токены | Клиентское соединение |
| F2 | Moderator → Mobile App | HTTPS/TLS | Учетные данные, JWT токены | Клиентское соединение |
| F3 | Web Browser → FastAPI | REST API/HTTPS | JSON данные, API запросы | Внешнее API |
| F4 | Mobile App → FastAPI | REST API/HTTPS | JSON данные, API запросы | Внешнее API |
| F5 | FastAPI → Database | SQL Queries | PII, предложения, метаданные | Взаимодействие с БД |
| F6 | FastAPI → File Storage | File System API | Файлы экспорта, логи | Операции с файлами |
