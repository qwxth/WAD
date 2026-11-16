import { useEffect, useState } from 'react';
import { Card } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';
import Breadcrumbs from '../components/Breadcrumbs';
import PatternMedia from '../components/PatternMedia';
import { mockPatterns } from '../mocks/patterns';
import type { LoadPattern } from '../types';

const tilesCrumb = { label: 'Плитка', to: '/load_patterns' };

export default function PatternPage() {
  const { id } = useParams();
  // undefined — ещё ищем, null — не найден
  const [pattern, setPattern] = useState<LoadPattern | null | undefined>(undefined);

  useEffect(() => {
    setPattern(mockPatterns.find((p) => p.id === Number(id)) ?? null);
  }, [id]);

  return (
    <>
      <Breadcrumbs current={pattern?.pattern_name ?? 'Паттерн нагрузки'} ancestors={[tilesCrumb]} />
      {pattern === undefined && <p>Загрузка...</p>}
      {pattern === null && (
        <>
          <p>Паттерн не найден</p>
          <Link to="/load_patterns" className="btn btn-dark lf-btn-pill rounded-pill">К плитке</Link>
        </>
      )}
      {pattern && (
        <div className="d-flex justify-content-center">
          <Card className="lf-card" style={{ width: '40rem' }}>
            <PatternMedia imageUrl={pattern.image_url} videoUrl={pattern.video_url} title={pattern.pattern_name} />
            <Card.Body>
              <Card.Title as="h1" className="h5">{pattern.pattern_name}</Card.Title>
              <Card.Text>{pattern.description}</Card.Text>
              <ul className="list-unstyled">
                <li>Код: {pattern.pattern_code}</li>
                <li>Применение: {pattern.use_case}</li>
                <li>RPS: {pattern.requests_per_second.toLocaleString('ru-RU')}</li>
                <li>Пиковый коэффициент: {pattern.peak_multiplier}</li>
                <li>Длительность, ч: {pattern.duration_hours}</li>
                <li>Ожидаемое число запросов: {pattern.expected_request_count.toLocaleString('ru-RU')}</li>
                <li>Создан: {new Date(pattern.created_at).toLocaleDateString('ru-RU')}</li>
              </ul>
              <Link to="/load_patterns" className="btn btn-dark lf-btn-pill rounded-pill">К плитке</Link>
            </Card.Body>
          </Card>
        </div>
      )}
    </>
  );
}
