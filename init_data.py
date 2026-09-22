from data.database import SessionLocal
from data.models import User, LoadPattern, PatternLike, PatternStatus
from datetime import datetime

def init_data():
    db = SessionLocal()
    
    # Очищаем таблицы
    db.query(PatternLike).delete()
    db.query(LoadPattern).delete()
    db.query(User).delete()
    db.commit()
    
    # Создаем пользователей
    user1 = User(username="admin", email="admin@loadforecast.com")
    user2 = User(username="user1", email="user1@loadforecast.com")
    user3 = User(username="user2", email="user2@loadforecast.com")
    
    db.add_all([user1, user2, user3])
    db.commit()
    
    # Создаем паттерны
    pattern1 = LoadPattern(
        pattern_name="Равномерная нагрузка",
        pattern_code="uniform",
        status=PatternStatus.published,
        requests_per_second=500,
        peak_multiplier=1.0,
        duration_hours=24,
        expected_request_count=43200000,
        average_request_count=500,
        description="Стабильный равномерный поток запросов без резких всплесков. Характерен для корпоративных систем.",
        use_case="Внутренние корпоративные сервисы",
        image_url="http://localhost:9000/load-patterns/uniform.jpg",
        video_url="http://localhost:9000/load-patterns/uniform.mp4",
        base_cpu_cores=2,
        base_ram_gb=4,
        creator_id=user1.id
    )
    
    pattern2 = LoadPattern(
        pattern_name="Пиковая нагрузка",
        pattern_code="peak",
        status=PatternStatus.published,
        requests_per_second=2000,
        peak_multiplier=5.0,
        duration_hours=4,
        expected_request_count=28800000,
        average_request_count=2000,
        description="Резкий всплеск запросов в 5 раз. Типичен для онлайн-распродаж и акций.",
        use_case="Интернет-магазины в период распродаж",
        image_url="http://localhost:9000/load-patterns/peak.jpg",
        video_url="http://localhost:9000/load-patterns/peak.mp4",
        base_cpu_cores=8,
        base_ram_gb=16,
        creator_id=user1.id
    )
    
    pattern3 = LoadPattern(
        pattern_name="Растущая нагрузка",
        pattern_code="growing",
        status=PatternStatus.published,
        requests_per_second=300,
        peak_multiplier=2.5,
        duration_hours=168,
        expected_request_count=181440000,
        average_request_count=300,
        description="Постепенный рост числа запросов. Характерен для стартапов, набирающих аудиторию.",
        use_case="SaaS-стартапы, растущие платформы",
        image_url="http://localhost:9000/load-patterns/growing.jpg",
        video_url="http://localhost:9000/load-patterns/growing.mp4",
        base_cpu_cores=4,
        base_ram_gb=8,
        creator_id=user1.id
    )
    
    pattern4 = LoadPattern(
        pattern_name="DDoS-атака",
        pattern_code="ddos",
        status=PatternStatus.draft,
        requests_per_second=50000,
        peak_multiplier=100.0,
        duration_hours=1,
        expected_request_count=180000000,
        average_request_count=50000,
        description="Злоумышленное превышение запросов в сотни раз. Требуются WAF, CDN, rate limiting.",
        use_case="Симуляция атак для тестирования защиты",
        image_url="http://localhost:9000/load-patterns/ddos.jpg",
        video_url="http://localhost:9000/load-patterns/ddos.mp4",
        base_cpu_cores=64,
        base_ram_gb=128,
        creator_id=user1.id
    )
    
    pattern5 = LoadPattern(
        pattern_name="Ночной минимум",
        pattern_code="night",
        status=PatternStatus.deleted,
        requests_per_second=50,
        peak_multiplier=0.1,
        duration_hours=8,
        expected_request_count=1440000,
        average_request_count=50,
        description="Минимальная ночная нагрузка.",
        use_case="Фоновые задачи",
        image_url="http://localhost:9000/load-patterns/night.jpg",
        video_url="http://localhost:9000/load-patterns/night.mp4",
        base_cpu_cores=1,
        base_ram_gb=2,
        creator_id=user1.id
    )
    
    db.add_all([pattern1, pattern2, pattern3, pattern4, pattern5])
    db.commit()
    
    # Создаем лайки
    like1 = PatternLike(user_id=user1.id, pattern_id=pattern1.id)
    like2 = PatternLike(user_id=user2.id, pattern_id=pattern1.id)
    like3 = PatternLike(user_id=user3.id, pattern_id=pattern1.id)
    like4 = PatternLike(user_id=user2.id, pattern_id=pattern2.id)
    like5 = PatternLike(user_id=user3.id, pattern_id=pattern2.id)
    like6 = PatternLike(user_id=user1.id, pattern_id=pattern3.id)
    like7 = PatternLike(user_id=user2.id, pattern_id=pattern3.id)
    like8 = PatternLike(user_id=user3.id, pattern_id=pattern3.id)
    
    db.add_all([like1, like2, like3, like4, like5, like6, like7, like8])
    db.commit()
    
    print("✅ База данных заполнена тестовыми данными!")
    print(f"   - ID 1-3: опубликованные паттерны (PUBLISHED)")
    print(f"   - ID 4: черновик для заполнения (DRAFT)")
    print(f"   - ID 5: удалённый паттерн (DELETED)")
    db.close()


if __name__ == "__main__":
    init_data()
