from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from data.database import get_db
from data.models import User
from api.schemas import UserRegisterRequest, UserLoginRequest, UserResponse, MessageResponse
from api.auth import (
    hash_password, verify_password,
    create_session, delete_session,
    SESSION_COOKIE_NAME, SESSION_TTL_SECONDS,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Регистрация нового пользователя",
    description="Создаёт пользователя. Пароль хранится как SHA-256 хэш и никогда не возвращается клиенту.",
)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=MessageResponse,
    summary="Аутентификация (вход)",
    description=(
        "Проверяет логин и пароль, создаёт сессию в Redis (TTL 24 часа) "
        "и устанавливает httponly cookie session_id. "
        "Эта cookie даёт доступ к методам создателя: создание, публикация, удаление, лайк."
    ),
)
def login(data: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")

    session_id = create_session(user.id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
    )
    return {"message": f"Добро пожаловать, {user.username}! Сессия сохранена в Redis."}


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Деавторизация (выход)",
    description="Удаляет сессию из Redis и очищает cookie session_id.",
)
def logout(request: Request, response: Response):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        delete_session(session_id)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Сессия завершена"}
