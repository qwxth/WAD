#!/bin/bash

echo "🚀 LoadForecast - Запуск проекта"
echo ""

# Проверка Docker
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker не запущен! Запустите Docker и попробуйте снова."
    exit 1
fi

# Запуск контейнеров
echo "📦 Запуск контейнеров (PostgreSQL, MinIO, Adminer)..."
docker-compose up -d

# Ожидание запуска PostgreSQL
echo "⏳ Ожидание запуска PostgreSQL..."
sleep 5

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "🐍 Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "❌ Виртуальное окружение не найдено! Создайте его: python3 -m venv venv"
    exit 1
fi

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip install -q -r requirements.txt

# Инициализация миграций (если нужно)
if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions)" ]; then
    echo "🔧 Инициализация миграций Alembic..."
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
fi

# Заполнение БД тестовыми данными
echo "📊 Заполнение БД тестовыми данными..."
python3 init_data.py

echo ""
echo "✅ Все готово!"
echo ""
echo "📌 Доступные сервисы:"
echo "   - Приложение:      http://127.0.0.1:8000"
echo "   - Adminer (БД):    http://localhost:8080"
echo "   - MinIO Console:   http://localhost:9001"
echo ""
echo "🔑 Доступы Adminer:"
echo "   Система: PostgreSQL"
echo "   Сервер: postgres"
echo "   Пользователь: loadforecast"
echo "   Пароль: loadforecast123"
echo "   База данных: loadforecast_db"
echo ""
echo "🔑 Доступы MinIO:"
echo "   Логин: root"
echo "   Пароль: rootpassword"
echo ""
echo "🚀 Запуск приложения..."
python3 main.py
