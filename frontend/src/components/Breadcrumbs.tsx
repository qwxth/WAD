import { Link } from 'react-router-dom';

interface BreadcrumbsProps {
  current: string;
  ancestors?: { label: string; to: string }[];
}

export default function Breadcrumbs({ current, ancestors = [] }: BreadcrumbsProps) {
  return (
    <nav aria-label="Навигационная цепочка">
      <ol className="breadcrumb">
        {ancestors.map(({ label, to }) => (
          <li key={to} className="breadcrumb-item">
            <Link to={to}>{label}</Link>
          </li>
        ))}
        <li className="breadcrumb-item active" aria-current="page">{current}</li>
      </ol>
    </nav>
  );
}
