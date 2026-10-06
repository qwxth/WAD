import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from data.database import get_db
from data.models import User
from api.schemas import UserRegisterRequest, UserLoginRequest, UserResponse, MessageResponse

router = APIRouter(prefix="/api/users", tags=["users"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ========== POST регистрация ==========
@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ========== POST аутентификация (заглушка для лабы 4) ==========
@router.post("/login", response_model=MessageResponse)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"message": f"Заглушка. В лабе 4 здесь будет JWT. Пользователь: {user.username}"}


# ========== POST деавторизация (заглушка для лабы 4) ==========
@router.post("/logout", response_model=MessageResponse)
def logout():
    return {"message": "Заглушка. В лабе 4 здесь будет инвалидация сессии/токена."}
