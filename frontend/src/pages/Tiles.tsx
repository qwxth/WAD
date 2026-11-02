import { useEffect, useState } from 'react';
import { Col, Row } from 'react-bootstrap';
import PatternCard from '../components/PatternCard';
import PatternFilter from '../components/PatternFilter';
import { EMPTY_FILTER } from '../constants';
import { mockPatterns } from '../mocks/patterns';
import type { LoadPattern, PatternFilterValues } from '../types';
import { filterPatterns } from '../utils/filterPatterns';

export default function Tiles() {
  const [patterns, setPatterns] = useState<LoadPattern[]>([]);
  const [draft, setDraft] = useState<PatternFilterValues>(EMPTY_FILTER);     // то, что вводит пользователь
  const [applied, setApplied] = useState<PatternFilterValues>(EMPTY_FILTER); // применяется только по «Найти»

  useEffect(() => {
    setPatterns(mockPatterns); // позже здесь будет запрос к веб-сервису
  }, []);

  const visible = filterPatterns(patterns, applied);

  return (
    <>
      <h2 className="mb-3">Плитка паттернов нагрузки</h2>
      <PatternFilter
        values={draft}
        onChange={setDraft}
        onApply={() => setApplied(draft)}
        onReset={() => {
          setDraft(EMPTY_FILTER);
          setApplied(EMPTY_FILTER);
        }}
      />
      {visible.length === 0 ? (
        <p>Ничего не найдено</p>
      ) : (
        <Row xs={1} md={3} className="g-4">
          {visible.map((p) => (
            <Col key={p.id}>
              <PatternCard pattern={p} />
            </Col>
          ))}
        </Row>
      )}
    </>
  );
}
