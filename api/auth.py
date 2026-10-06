"""
Заглушка авторизации для лабы 3.
Текущий пользователь зафиксирован константой (singleton через функцию).
В лабе 4 будет заменено на реальную авторизацию через JWT/сессии.
"""
from sqlalchemy.orm import Session
from data.models import User

# ID пользователя-владельца сессии (константа)
CURRENT_USER_ID = 1


def get_current_user(db: Session) -> User:
    """Singleton: возвращает текущего пользователя (константно).
    В лабе 4 будет извлекать user_id из JWT-токена/сессии."""
    user = db.query(User).filter(User.id == CURRENT_USER_ID).first()
    if not user:
        user = db.query(User).first()
    if not user:
        raise RuntimeError("В БД нет пользователей! Запустите: python3 init_data.py")
    return user
