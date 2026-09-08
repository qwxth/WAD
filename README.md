# LoadForecast — Прогноз нагрузки на сервер

Лабораторная работа №1 по курсу "Разработка интернет приложений"

Предметная область: Прогноз нагрузки на сервер  
Услуги: Паттерны нагрузки (равномерная, пиковая, растущая, DDoS)  
Заявка: Расчёт требуемых ресурсов CPU и RAM для обработки прогнозируемого количества запросов в секунду

---

# Дизайн

Скопировано с: Amazon.com

Цветовая палитра:
- ######161D26 — основной тёмный (шапка, кнопки, таббар)
- ######232B37 — вторичный тёмный (hover, разделители)
- ######FFFFFF — белый (текст на тёмном, карточки, фон)

Figma-прототип: `figma_prototype/index.html`

---

# Быстрый старт

# 1. Клонируй репозиторий

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd WAD
```

# 2. Создай виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

# 3. Установи зависимости

```bash
pip install -r requirements.txt
```

# 4. Запусти MinIO

```bash
docker-compose up -d
```

# 5. Настрой MinIO (первый раз)

```bash
# Подключи клиента
docker exec -it minio_storage mc alias set myminio http://localhost:9000 root rootpassword

# Создай бакет
docker exec -it minio_storage mc mb myminio/media

# Сделай публичным
docker exec -it minio_storage mc anonymous set public myminio/media
```

# 6. Загрузи изображения и видео

Открой MinIO Console: http://localhost:9001
- Логин: `root`
- Пароль: `rootpassword`

Загрузи в бакет `media`:
- `uniform.jpg`, `uniform.mp4`
- `peak.jpg`, `peak.mp4`
- `growing.jpg`, `growing.mp4`
- `ddos.jpg`, `ddos.mp4`

# 7. Запусти приложение

```bash
python3 main.py
```

Приложение доступно: http://127.0.0.1:8000

---

# Структура проекта

```
WAD/
├── main.py                   # Точка входа FastAPI
├── requirements.txt          # Зависимости Python
├── docker-compose.yml        # MinIO контейнер
├── api/
│   ├── __init__.py
│   └── handlers.py           # Роутинг (контроллеры)
├── data/
│   ├── __init__.py
│   └── collections.py        # Модель данных (коллекция)
├── templates/
│   ├── patterns.html         # Плитка паттернов
│   ├── pattern_detail.html   # Лента (Reels)
│   └── forecast_form.html    # Заявка на расчёт
├── static/
│   ├── css/
│   │   └── style.css         # Стили
│   └── img/                  # (пусто, всё в MinIO)
└── figma_prototype/
    ├── index.html            # Прототип для Figma
    ├── style.css
    └── assets/               # Изображения для прототипа
```

---

# Маршруты приложения

| URL | Метод | Описание |
|-----|-------|----------|
| `/` | GET | Редирект → `/patterns` |
| `/patterns` | GET | Плитка паттернов нагрузки |
| `/patterns?max_rps=2000` | GET | Фильтрация по максимальному RPS |
| `/pattern/{id}` | GET | Лента (Reels) — просмотр паттерна по ID |
| `/pattern/{id}?next=true` | GET | Следующий паттерн после ID |
| `/forecast` | GET | Заявка — черновик + расчёт ресурсов |

---

# Модель данных

Коллекция: `load_patterns_db` (массив словарей)

Поля паттерна:
- `id` — уникальный идентификатор
- `pattern_name` — название (Равномерная нагрузка, Пиковая нагрузка, ...)
- `pattern_code` — код (`uniform`, `peak`, `growing`, `ddos`)
- `status` — статус (`published`, `draft`, `deleted`)
- `requests_per_second` — базовый RPS (запросов в секунду)
- `peak_multiplier` — пиковый множитель нагрузки
- `duration_hours` — длительность нагрузки (часов)
- `description` — текстовое описание
- `use_case` — сценарий применения
- `image_url` — URL изображения в MinIO
- `video_url` — URL видео в MinIO
- `likes` — массив ID пользователей (для подсчёта лайков)
- `base_cpu_cores` — базовое требование CPU
- `base_ram_gb` — базовое требование RAM

Статусы:
- `published` — отображается в плитке и ленте (3 шт)
- `draft` — отображается ТОЛЬКО на странице заявки (1 шт)
- `deleted` — НЕ отображается нигде (1 шт)

---

# Функциональность

# Плитка (`/patterns`)
- Отображение всех опубликованных паттернов в 2 колонки
- Фильтрация по максимальному RPS
- Вычисление количества лайков на сервере
- Переход на ленту по клику на карточку

# Лента (`/pattern/{id}`)
- Автоплей видео из MinIO (формат TikTok/Reels)
- Отображение полей по теме поверх видео
- Сворачиваемое описание (`details`)
- Навигация "Следующий" (`?next=true`)

# Заявка (`/forecast`)
- Отображение черновика паттерна
- Разделение полей: медиафайлы / параметры
- Расчёт ресурсов:
  - CPU = ceil(RPS × K / 200) ядер
  - RAM = ceil(RPS × K / 500) ГБ
  - где K — пиковый множитель

---

# Docker команды

```bash
# Запуск MinIO
docker-compose up -d

# Остановка
docker-compose down

# Полная очистка (удаление данных)
docker-compose down -v

# Проверка статуса
docker ps | grep minio

# Логи
docker logs minio_storage
```

---

# Технологический стек

- Backend: FastAPI (Python 3.10+)
- Шаблонизатор: Jinja2
- Хранилище: MinIO (S3-compatible)
- Стили: CSS (скопировано с Amazon.com)
- Контейнеризация: Docker Compose

---

# Контрольные вопросы

1. MVT (Model-View-Template):
   - Model — `data/collections.py`
   - View — `api/handlers.py`
   - Template — `templates/*.html`

2. Компоненты MVC в лабораторной:
   - Model — `load_patterns_db`
   - Controller — функции в `handlers.py`
   - View — Jinja2 шаблоны

3. Шаблонизация:
   - Jinja2 синтаксис: `{{ переменная }}`, `{% for %}`
   - Наследование: `{% extends %}`, `{% block %}`

4. HTTP и модель OSI:
   - HTTP — протокол прикладного уровня (7)
   - Методы: GET, POST, PUT, DELETE
   - Статусы: 200 OK, 404 Not Found, 206 Partial Content

5. Web и HTML:
   - HTML — язык разметки гипертекста
   - Семантические теги: `header`, `main`, `nav`
   - Формы: `form`, `input`, `button`

---

# Зависимости

```
fastapi==0.115.6
uvicorn==0.34.0
jinja2==3.1.5
python-multipart==0.0.20
aiofiles==24.1.0
sqlalchemy==2.0.36
alembic==1.14.0
```

---

# Автор

Студент: Герман А.  
Группа: ИУ5-53Б
Курс: РИП
Лабораторная: №1 — Прогноз нагрузки на сервер

---

# Лицензия

Учебный проект. Все права защищены.
