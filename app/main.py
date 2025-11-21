from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_password_hash, verify_password
from app.database import engine, get_db
from app.dependencies import get_current_user, require_owner
from app.logger import log_api_request, log_security_event, log_user_action
from app.models import Base
from app.models import Suggestion as SuggestionModel
from app.models import User as UserModel
from app.schemas import Suggestion as SuggestionSchema
from app.schemas import SuggestionCreate, SuggestionUpdate, Token
from app.schemas import User as UserSchema
from app.schemas import UserCreate, UserLogin

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Suggestion Box MVP",
    description="API для системы предложений с анонимными отзывами",
    version="0.1.0",
)


# ==================== ЭНДПОИНТЫ АУТЕНТИФИКАЦИИ ====================


@app.post("/auth/register", response_model=UserSchema)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        # Валидация пароля
        if len(user_data.password) < 8:
            log_security_event(
                "REGISTER_PASSWORD_TOO_SHORT", None, f"email={user_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long",
            )

        # Проверяем существование пользователя
        existing_user = (
            db.query(UserModel).filter(UserModel.email == user_data.email).first()
        )
        if existing_user:
            log_security_event(
                "REGISTER_DUPLICATE_EMAIL", None, f"email={user_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Создаем пользователя
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(email=user_data.email, hashed_password=hashed_password)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        log_user_action("REGISTER_SUCCESS", db_user.id, f"email={user_data.email}")
        log_api_request("POST", "/auth/register", db_user.id, 200)

        return db_user

    except HTTPException:
        raise
    except Exception as e:
        log_security_event("REGISTER_ERROR", None, f"error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@app.post("/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Аутентификация пользователя и получение JWT токена"""
    try:
        user = db.query(UserModel).filter(UserModel.email == user_data.email).first()

        if not user or not verify_password(user_data.password, user.hashed_password):
            user_id = user.id if user else None
            log_security_event("LOGIN_FAILED", user_id, f"email={user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": str(user.id)})

        log_user_action("LOGIN_SUCCESS", user.id)
        log_api_request("POST", "/auth/login", user.id, 200)

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        log_security_event("LOGIN_ERROR", None, f"error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


# ==================== ОСНОВНЫЕ ЭНДПОИНТЫ ====================


@app.get("/")
def read_root():
    """Корневой эндпоинт - проверка работы сервера"""
    log_api_request("GET", "/", None, 200)
    return {"message": "Suggestion Box MVP работает!"}


# ==================== ЭНДПОИНТЫ ПРЕДЛОЖЕНИЙ ====================


@app.get("/suggestions", response_model=List[SuggestionSchema])
def get_suggestions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Получение списка предложений с возможностью фильтрации"""
    try:
        query = db.query(SuggestionModel)

        if status:
            query = query.filter(SuggestionModel.status == status)

        suggestions = query.offset(skip).limit(limit).all()

        log_api_request("GET", "/suggestions", None, 200)
        return suggestions

    except Exception as e:
        log_security_event("GET_SUGGESTIONS_ERROR", None, f"error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching suggestions",
        )


@app.post("/suggestions", response_model=SuggestionSchema)
def create_suggestion(
    suggestion: SuggestionCreate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Создание нового предложения"""
    try:
        db_suggestion = SuggestionModel(
            **suggestion.dict(), user_id=current_user.id, status="pending"
        )

        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)

        log_user_action(
            "SUGGESTION_CREATE", current_user.id, f"suggestion_id={db_suggestion.id}"
        )
        log_api_request("POST", "/suggestions", current_user.id, 200)

        return db_suggestion

    except Exception as e:
        log_security_event(
            "CREATE_SUGGESTION_ERROR", current_user.id, f"error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating suggestion",
        )


@app.get("/suggestions/{suggestion_id}", response_model=SuggestionSchema)
def get_suggestion(
    suggestion_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получение конкретного предложения (owner-only)"""
    try:
        suggestion = (
            db.query(SuggestionModel)
            .filter(SuggestionModel.id == suggestion_id)
            .first()
        )

        if not suggestion:
            log_api_request(
                "GET", f"/suggestions/{suggestion_id}", current_user.id, 404
            )
            raise HTTPException(status_code=404, detail="Suggestion not found")

        # Проверка прав доступа
        require_owner(current_user, suggestion.user_id)

        log_user_action(
            "SUGGESTION_VIEW", current_user.id, f"suggestion_id={suggestion_id}"
        )
        log_api_request("GET", f"/suggestions/{suggestion_id}", current_user.id, 200)

        return suggestion

    except HTTPException as e:
        if e.status_code == 403:
            log_security_event(
                "UNAUTHORIZED_ACCESS",
                current_user.id,
                f"attempted_suggestion_id={suggestion_id}, "
                f"owner_id={suggestion.user_id}",
            )
        log_api_request(
            "GET", f"/suggestions/{suggestion_id}", current_user.id, e.status_code
        )
        raise
    except Exception as e:
        log_security_event(
            "GET_SUGGESTION_ERROR",
            current_user.id,
            f"suggestion_id={suggestion_id}, error={str(e)}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching suggestion",
        )


@app.put("/suggestions/{suggestion_id}", response_model=SuggestionSchema)
def update_suggestion(
    suggestion_id: int,
    suggestion_update: SuggestionUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновление предложения (owner-only)"""
    try:
        suggestion = (
            db.query(SuggestionModel)
            .filter(SuggestionModel.id == suggestion_id)
            .first()
        )

        if not suggestion:
            log_api_request(
                "PUT", f"/suggestions/{suggestion_id}", current_user.id, 404
            )
            raise HTTPException(status_code=404, detail="Suggestion not found")

        # Проверка прав доступа
        require_owner(current_user, suggestion.user_id)

        # Обновляем только переданные поля
        update_data = suggestion_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(suggestion, field, value)

        db.commit()
        db.refresh(suggestion)

        log_user_action(
            "SUGGESTION_UPDATE", current_user.id, f"suggestion_id={suggestion_id}"
        )
        log_api_request("PUT", f"/suggestions/{suggestion_id}", current_user.id, 200)

        return suggestion

    except HTTPException as e:
        if e.status_code == 403:
            log_security_event(
                "UNAUTHORIZED_UPDATE",
                current_user.id,
                f"attempted_suggestion_id={suggestion_id}, "
                f"owner_id={suggestion.user_id}",
            )
        log_api_request(
            "PUT", f"/suggestions/{suggestion_id}", current_user.id, e.status_code
        )
        raise
    except Exception as e:
        log_security_event(
            "UPDATE_SUGGESTION_ERROR",
            current_user.id,
            f"suggestion_id={suggestion_id}, error={str(e)}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating suggestion",
        )


@app.delete("/suggestions/{suggestion_id}")
def delete_suggestion(
    suggestion_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Удаление предложения (owner-only)"""
    try:
        suggestion = (
            db.query(SuggestionModel)
            .filter(SuggestionModel.id == suggestion_id)
            .first()
        )

        if not suggestion:
            log_api_request(
                "DELETE", f"/suggestions/{suggestion_id}", current_user.id, 404
            )
            raise HTTPException(status_code=404, detail="Suggestion not found")

        # Проверка прав доступа
        require_owner(current_user, suggestion.user_id)

        db.delete(suggestion)
        db.commit()

        log_user_action(
            "SUGGESTION_DELETE", current_user.id, f"suggestion_id={suggestion_id}"
        )
        log_api_request("DELETE", f"/suggestions/{suggestion_id}", current_user.id, 200)

        return {"message": "Suggestion deleted successfully"}

    except HTTPException as e:
        if e.status_code == 403:
            log_security_event(
                "UNAUTHORIZED_DELETE",
                current_user.id,
                f"attempted_suggestion_id={suggestion_id}, "
                f"owner_id={suggestion.user_id}",
            )
        log_api_request(
            "DELETE", f"/suggestions/{suggestion_id}", current_user.id, e.status_code
        )
        raise
    except Exception as e:
        log_security_event(
            "DELETE_SUGGESTION_ERROR",
            current_user.id,
            f"suggestion_id={suggestion_id}, error={str(e)}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting suggestion",
        )


# ==================== ДЕБАГ И МОНИТОРИНГ ====================


@app.get("/debug/my-info")
def get_my_info(current_user: UserModel = Depends(get_current_user)):
    """Информация о текущем пользователе"""
    log_api_request("GET", "/debug/my-info", current_user.id, 200)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": (
            current_user.created_at.isoformat() if current_user.created_at else None
        ),
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья приложения и подключения к БД"""
    try:
        db.execute(text("SELECT 1"))
        log_api_request("GET", "/health", None, 200)
        return {
            "status": "healthy",
            "database": "connected",
            "version": "0.1.0",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log_security_event("HEALTH_CHECK_FAILED", None, f"database_error={str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get("/logs/health")
def logs_health():
    """Проверка здоровья системы логирования"""
    import os

    log_files = (
        [f for f in os.listdir("logs") if f.endswith(".log")]
        if os.path.exists("logs")
        else []
    )

    log_api_request("GET", "/logs/health", None, 200)

    return {
        "logging_status": "active",
        "log_files": log_files,
        "log_directory": "logs/",
        "timestamp": datetime.utcnow().isoformat(),
    }
