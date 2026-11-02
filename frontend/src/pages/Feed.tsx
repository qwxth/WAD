import { useEffect, useState } from 'react';
import { Button, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import PatternMedia from '../components/PatternMedia';
import { mockPatterns } from '../mocks/patterns';
import type { LoadPattern } from '../types';

export default function Feed() {
  const [patterns, setPatterns] = useState<LoadPattern[]>([]);
  const [currentId, setCurrentId] = useState<number | null>(null);

  useEffect(() => {
    const sorted = [...mockPatterns].sort((a, b) => a.id - b.id);
    setPatterns(sorted);
    setCurrentId(sorted[0]?.id ?? null);
  }, []);

  const pattern = patterns.find((p) => p.id === currentId);

  // «Следующий»: первый id больше текущего, иначе циклический возврат к первому (ID могут идти с пропусками)
  function handleNext() {
    if (currentId === null) return;
    const next = patterns.find((p) => p.id > currentId) ?? patterns[0];
    setCurrentId(next.id);
  }

  if (!pattern) return <p>Нет данных</p>;

  return (
    <div className="d-flex justify-content-center">
      <Card className="lf-card" style={{ width: '32rem' }}>
        <PatternMedia imageUrl={pattern.image_url} videoUrl={pattern.video_url} title={pattern.pattern_name} />
        <Card.Body>
          <Card.Title>{pattern.pattern_name}</Card.Title>
          <Card.Text>
            RPS: {pattern.requests_per_second.toLocaleString('ru-RU')}
            <br />
            Ожидаемое число запросов: {pattern.expected_request_count.toLocaleString('ru-RU')}
            <br />
            Лайков: {pattern.likes_count}
          </Card.Text>
          <div className="d-flex gap-2">
            <Button variant="dark" className="lf-btn-pill rounded-pill" onClick={handleNext}>
              Следующий
            </Button>
            <Link to={`/load_patterns/${pattern.id}`} className="btn btn-outline-dark rounded-pill">
              Подробнее
            </Link>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
}
