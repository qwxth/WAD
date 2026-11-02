import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import BottomNav from './components/BottomNav';
import Feed from './pages/Feed';
import PatternPage from './pages/PatternPage';
import Tiles from './pages/Tiles';

export default function App() {
  return (
    <BrowserRouter>
      <Container className="py-4">
        <Routes>
          <Route path="/" element={<Navigate to="/load_patterns/feed" replace />} />
          <Route path="/load_patterns" element={<Tiles />} />
          <Route path="/load_patterns/feed" element={<Feed />} />
          <Route path="/load_patterns/:id" element={<PatternPage />} />
          <Route path="*" element={<Navigate to="/load_patterns/feed" replace />} />
        </Routes>
      </Container>
      <BottomNav />
    </BrowserRouter>
  );
}
