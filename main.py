from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.handlers import router as html_router
from api.rest_patterns import router as rest_patterns_router
from api.rest_users import router as rest_users_router
from data.minio_client import ensure_bucket
import uvicorn

tags_metadata = [
    {"name": "load_patterns", "description": "Паттерны нагрузки. Чтение - без авторизации, создание/публикация/удаление/лайк - требуют вход через /api/users/login."},
    {"name": "users", "description": "Регистрация, вход (создаёт сессию в Redis + cookie), выход."},
]

app = FastAPI(
    title="LoadForecast API",
    description=(
        "REST API для управления паттернами нагрузки.\n\n"
        "Авторизация построена на сессиях: POST /api/users/login создаёт сессию в Redis "
        "и возвращает httponly cookie session_id. Для вызова защищённых методов в Swagger "
        "нажмите Authorize и укажите значение cookie, либо просто выполните /login в этом же "
        "браузере - cookie подставится автоматически."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# allow_origins="*" несовместимо с allow_credentials=True по спецификации CORS,
# поэтому для локальной разработки перечисляем конкретные источники.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(html_router, include_in_schema=False)
app.include_router(rest_patterns_router)
app.include_router(rest_users_router)


@app.on_event("startup")
def on_startup():
    try:
        ensure_bucket()
        print("MinIO bucket готов")
    except Exception as e:
        print(f"MinIO недоступен: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
