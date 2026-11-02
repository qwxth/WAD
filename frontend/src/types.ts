// Поля совпадают с ответом REST API (/api/load_patterns)
export interface LoadPattern {
  id: number;
  pattern_name: string;
  pattern_code: string;
  status: 'published';
  expected_request_count: number;
  requests_per_second: number;
  peak_multiplier: number;
  duration_hours: number;
  description: string;
  use_case: string;
  image_url: string | null;
  video_url: string | null;
  created_at: string;
  likes_count: number;
}

export interface PatternFilterValues {
  search: string;
  maxExpected: number;
  minRps: string;
  maxRps: string;
}
