import type { LoadPattern } from '../types';

// ID идут с пропусками намеренно (как в БД после удалений)
export const mockPatterns: LoadPattern[] = [
  {
    id: 1, pattern_name: 'Пик продаж (Black Friday)', pattern_code: 'black_friday', status: 'published',
    expected_request_count: 108_000_000, requests_per_second: 5000, peak_multiplier: 3, duration_hours: 6,
    description: 'Резкий рост трафика во время распродаж.', use_case: 'Интернет-магазин',
    image_url: '/mock/pattern-1.svg', video_url: null, created_at: '2026-10-01T10:00:00', likes_count: 12,
  },
  {
    id: 2, pattern_name: 'Ночной штиль', pattern_code: 'night_idle', status: 'published',
    expected_request_count: 1_440_000, requests_per_second: 50, peak_multiplier: 1.2, duration_hours: 8,
    description: 'Минимальная фоновая нагрузка в ночные часы.', use_case: 'Корпоративный портал',
    image_url: null, video_url: null, created_at: '2026-10-02T10:00:00', likes_count: 3,
  },
  {
    id: 4, pattern_name: 'Утренний пик', pattern_code: 'morning_peak', status: 'published',
    expected_request_count: 8_640_000, requests_per_second: 800, peak_multiplier: 2, duration_hours: 3,
    description: 'Всплеск при начале рабочего дня.', use_case: 'Почтовый сервис',
    image_url: '/mock/pattern-2.svg', video_url: null, created_at: '2026-10-03T10:00:00', likes_count: 7,
  },
  {
    id: 5, pattern_name: 'Равномерная нагрузка', pattern_code: 'steady', status: 'published',
    expected_request_count: 25_920_000, requests_per_second: 300, peak_multiplier: 1.1, duration_hours: 24,
    description: 'Стабильный поток запросов в течение суток.', use_case: 'API мониторинга',
    image_url: null, video_url: null, created_at: '2026-10-04T10:00:00', likes_count: 5,
  },
  {
    id: 7, pattern_name: 'Flash Crowd', pattern_code: 'flash_crowd', status: 'published',
    expected_request_count: 43_200_000, requests_per_second: 12000, peak_multiplier: 5, duration_hours: 1,
    description: 'Внезапный наплыв пользователей после анонса.', use_case: 'Стриминговая платформа',
    image_url: '/mock/pattern-3.svg', video_url: null, created_at: '2026-10-05T10:00:00', likes_count: 21,
  },
  {
    id: 9, pattern_name: 'Постепенный рост', pattern_code: 'ramp_up', status: 'published',
    expected_request_count: 64_800_000, requests_per_second: 1500, peak_multiplier: 1.5, duration_hours: 12,
    description: 'Плавное увеличение нагрузки в течение дня.', use_case: 'Образовательная платформа',
    image_url: null, video_url: null, created_at: '2026-10-06T10:00:00', likes_count: 9,
  },
];
