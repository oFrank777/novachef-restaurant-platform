import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (roles && roles.length > 0 && !roles.includes(user?.role)) {
    return (
      <div className="page-container">
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h2 style={{ color: 'var(--error)' }}>Acceso Denegado</h2>
          <p style={{ color: 'var(--text-secondary)' }}>No tienes permiso para acceder a esta página.</p>
        </div>
      </div>
    );
  }

  return children;
}
