import type { LoadPattern, PatternFilterValues } from '../types';

// Чистая функция: список + значения фильтра -> отфильтрованный список
export function filterPatterns(items: LoadPattern[], f: PatternFilterValues): LoadPattern[] {
  const search = f.search.trim().toLowerCase();
  const minRps = f.minRps === '' ? null : Number(f.minRps);
  const maxRps = f.maxRps === '' ? null : Number(f.maxRps);

  return items.filter(
    (p) =>
      (search === '' || p.pattern_name.toLowerCase().includes(search)) &&
      p.expected_request_count <= f.maxExpected &&
      (minRps === null || p.requests_per_second >= minRps) &&
      (maxRps === null || p.requests_per_second <= maxRps),
  );
}
