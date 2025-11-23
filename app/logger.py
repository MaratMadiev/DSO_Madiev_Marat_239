import logging
import os
import sys
from datetime import datetime

# Создаем папку для логов если нет
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настройка формата логов
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Базовый логгер
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("suggestion_box")


# SEC-NFR-007: Логирование security events
def log_security_event(event_type: str, user_id: int = None, details: str = ""):
    """Логирование событий безопасности"""
    user_info = f"user_id={user_id}" if user_id else "anonymous"
    logger.warning(f"SECURITY - {event_type} - {user_info} - {details}")


def log_user_action(action: str, user_id: int, details: str = ""):
    """Логирование действий пользователей"""
    logger.info(f"USER_ACTION - {action} - user_id={user_id} - {details}")


def log_api_request(
    method: str, path: str, user_id: int = None, status_code: int = None
):
    """Логирование API запросов"""
    user_info = f"user_id={user_id}" if user_id else "anonymous"
    status_info = f"status={status_code}" if status_code else ""
    logger.info(f"API - {method} {path} - {user_info} - {status_info}")
