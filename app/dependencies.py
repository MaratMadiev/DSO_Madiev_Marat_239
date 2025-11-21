from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models
from app.auth import verify_token
from app.database import get_db
from app.logger import log_security_event

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    """Получает текущего пользователя из JWT токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        log_security_event("MISSING_TOKEN", None, "no_authorization_header")
        raise credentials_exception

    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        log_security_event("INVALID_TOKEN", None, "token_verification_failed")
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        log_security_event("INVALID_TOKEN_PAYLOAD", None, "missing_sub_field")
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        log_security_event("INVALID_USER_ID", None, f"user_id_str={user_id_str}")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        log_security_event("USER_NOT_FOUND", user_id, "user_id_from_token_not_in_db")
        raise credentials_exception

    return user


def require_owner(current_user: models.User, target_user_id: int):
    """Проверяет, что пользователь является владельцем или модератором"""
    if current_user.id != target_user_id and current_user.role != "moderator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
