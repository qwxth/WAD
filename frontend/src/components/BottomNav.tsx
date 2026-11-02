import { Container, Nav, Navbar } from 'react-bootstrap';
import { NavLink } from 'react-router-dom';

export default function BottomNav() {
  return (
    <Navbar fixed="bottom" bg="white" className="border-top">
      <Container>
        <Nav className="w-100 justify-content-around">
          <Nav.Link as={NavLink} to="/load_patterns/feed">Лента</Nav.Link>
          <Nav.Link disabled>Добавление</Nav.Link>
          <Nav.Link as={NavLink} to="/load_patterns" end>Плитка</Nav.Link>
          <Nav.Link disabled>Вход</Nav.Link>
        </Nav>
      </Container>
    </Navbar>
  );
}
