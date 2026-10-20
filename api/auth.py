"""
Авторизация для ЛР4: сессии хранятся в Redis, идентификатор сессии передаётся
клиенту через httponly-cookie session_id.

get_current_user        - обязательная авторизация (401, если нет сессии)
get_current_user_optional - необязательная (None, если гостя нет сессии) -
                            используется в GET-методах чтения, доступных без логина
"""
import hashlib
import secrets
from typing import Optional

import redis
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from data.database import get_db
from data.models import User

SESSION_COOKIE_NAME = "session_id"
SESSION_TTL_SECONDS = 60 * 60 * 24  # 24 часа

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Схема для Swagger UI: рисует кнопку "Authorize" (замочек),
# куда можно вручную вписать значение cookie session_id для теста защищённых методов.
cookie_scheme = APIKeyCookie(name=SESSION_COOKIE_NAME, auto_error=False)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_session(user_id: int) -> str:
    session_id = secrets.token_hex(32)
    redis_client.setex(f"session:{session_id}", SESSION_TTL_SECONDS, str(user_id))
    return session_id


def delete_session(session_id: str) -> None:
    redis_client.delete(f"session:{session_id}")


def _user_id_from_session(session_id: Optional[str]) -> Optional[int]:
    if not session_id:
        return None
    raw = redis_client.get(f"session:{session_id}")
    if raw is None:
        return None
    return int(raw)


def get_current_user_optional(
    session_id: Optional[str] = Depends(cookie_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Для методов чтения: гость получает None, зарегистрированный - объект User."""
    user_id = _user_id_from_session(session_id)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(
    session_id: Optional[str] = Depends(cookie_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Для методов создателя: без валидной сессии - 401."""
    user_id = _user_id_from_session(session_id)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Требуется аутентификация")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
