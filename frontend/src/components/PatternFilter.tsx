import { Button, Col, Form, Row } from 'react-bootstrap';
import { MAX_EXPECTED } from '../constants';
import type { PatternFilterValues } from '../types';

interface PatternFilterProps {
  values: PatternFilterValues;
  onChange: (values: PatternFilterValues) => void;
  onApply: () => void;
  onReset: () => void;
}

export default function PatternFilter({ values, onChange, onApply, onReset }: PatternFilterProps) {
  return (
    <Form
      className="p-3 mb-4 bg-white border rounded"
      onSubmit={(e) => {
        e.preventDefault();
        onApply();
      }}
    >
      <Row className="g-3 align-items-end">
        <Col md={3}>
          <Form.Label htmlFor="f-search">Название</Form.Label>
          <Form.Control
            id="f-search"
            value={values.search}
            placeholder="Например, пик"
            onChange={(e) => onChange({ ...values, search: e.target.value })}
          />
        </Col>
        <Col md={3}>
          <Form.Label htmlFor="f-expected">
            Ожидаемых запросов не более: {values.maxExpected.toLocaleString('ru-RU')}
          </Form.Label>
          <Form.Range
            id="f-expected"
            min={0}
            max={MAX_EXPECTED}
            step={1_000_000}
            value={values.maxExpected}
            onChange={(e) => onChange({ ...values, maxExpected: Number(e.target.value) })}
          />
        </Col>
        <Col md={2}>
          <Form.Label htmlFor="f-min-rps">RPS от</Form.Label>
          <Form.Control
            id="f-min-rps"
            type="number"
            min={0}
            value={values.minRps}
            onChange={(e) => onChange({ ...values, minRps: e.target.value })}
          />
        </Col>
        <Col md={2}>
          <Form.Label htmlFor="f-max-rps">RPS до</Form.Label>
          <Form.Control
            id="f-max-rps"
            type="number"
            min={0}
            value={values.maxRps}
            onChange={(e) => onChange({ ...values, maxRps: e.target.value })}
          />
        </Col>
        <Col md={2} className="d-flex gap-2">
          <Button type="submit" variant="dark" className="lf-btn-pill rounded-pill">
            Найти
          </Button>
          <Button type="button" variant="outline-dark" className="rounded-pill" onClick={onReset}>
            Сбросить
          </Button>
        </Col>
      </Row>
    </Form>
  );
}
