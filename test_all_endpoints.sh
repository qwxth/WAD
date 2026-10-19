#!/bin/bash
BASE="http://127.0.0.1:8000"

echo "=== 01. GET список с фильтром ==="
curl -s "$BASE/api/load_patterns?max_expected=200&min_rps=100" | python3 -m json.tool

echo "=== 02. POST создать паттерн (с файлами) ==="
curl -s -X POST "$BASE/api/load_patterns" \
  -F "pattern_name=Test Pattern" \
  -F "description=Описание тестового паттерна" \
  -F "use_case=Нагрузочное тестирование" \
  -F "image=@/путь/к/фото.jpg" \
  -F "video=@/путь/к/видео.mp4" | python3 -m json.tool

echo "=== 03. GET черновик ==="
curl -s "$BASE/api/load_patterns/draft" | python3 -m json.tool

echo "=== 04. PUT публикация ==="
curl -s -X PUT "$BASE/api/load_patterns/4/publish" \
  -H "Content-Type: application/json" \
  -d '{"requests_per_second":1000,"peak_multiplier":2.5,"duration_hours":12,"description":"Обновлённое описание","base_cpu_cores":8,"base_ram_gb":16}' | python3 -m json.tool

echo "=== 05. GET лента без ID (один объект) ==="
curl -s "$BASE/api/load_patterns/feed" | python3 -m json.tool

echo "=== 06. GET лента по ID next=true ==="
curl -s "$BASE/api/load_patterns/1?next=true" | python3 -m json.tool

echo "=== 07. POST лайк (1) ==="
curl -s -X POST "$BASE/api/load_patterns/2/like" -H "Content-Type: application/json" -d '{"value":1}' | python3 -m json.tool

echo "=== 08. POST лайк (0) ==="
curl -s -X POST "$BASE/api/load_patterns/2/like" -H "Content-Type: application/json" -d '{"value":0}' | python3 -m json.tool

echo "=== 09. DELETE паттерн ==="
curl -s -X DELETE "$BASE/api/load_patterns/3" | python3 -m json.tool

echo "=== 10. POST регистрация ==="
curl -s -X POST "$BASE/api/users/register" -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"new@example.com","password":"secret123"}' | python3 -m json.tool
