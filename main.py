from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.handlers import router as html_router
from api.rest_patterns import router as rest_patterns_router
from api.rest_users import router as rest_users_router
from data.minio_client import ensure_bucket
import uvicorn

app = FastAPI(
    title="LoadForecast API",
    description="REST API для управления паттернами нагрузки",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(html_router)
app.include_router(rest_patterns_router)
app.include_router(rest_users_router)


@app.on_event("startup")
def on_startup():
    try:
        ensure_bucket()
        print("✅ MinIO bucket готов")
    except Exception as e:
        print(f"⚠️ MinIO недоступен: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
