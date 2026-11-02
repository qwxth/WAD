import { Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import type { LoadPattern } from '../types';
import PatternMedia from './PatternMedia';

interface PatternCardProps {
  pattern: LoadPattern;
}

export default function PatternCard({ pattern }: PatternCardProps) {
  return (
    <Card className="lf-card h-100">
      <PatternMedia
        imageUrl={pattern.image_url}
        videoUrl={pattern.video_url}
        title={pattern.pattern_name}
        showVideo={false}
        height={160}
      />
      <Card.Body className="d-flex flex-column">
        <Card.Title>{pattern.pattern_name}</Card.Title>
        <Card.Text>
          RPS: {pattern.requests_per_second.toLocaleString('ru-RU')}
          <br />
          Ожидаемое число запросов: {pattern.expected_request_count.toLocaleString('ru-RU')}
        </Card.Text>
        <Link
          to={`/load_patterns/${pattern.id}`}
          className="btn btn-dark lf-btn-pill rounded-pill mt-auto align-self-start"
        >
          Подробнее
        </Link>
      </Card.Body>
    </Card>
  );
}
