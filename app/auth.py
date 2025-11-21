import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# Загружаем переменные окружения
load_dotenv()

# SEC-NFR-002: Используем Argon2 для хэширования паролей
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Безопасное получение секретов из .env
# SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = "your-super-secret-key-here-minimum-32-chars"
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Проверяем что SECRET_KEY установлен
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY not found in environment variables. Check your .env file"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против хэша"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Создает хэш пароля"""
    if len(password) < 8:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Проверяет JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
