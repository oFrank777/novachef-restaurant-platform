import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && isAuthenticated) navigate('/dashboard', { replace: true });
  }, [loading, isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const cleanEmail = email.trim().substring(0, 100);
    
    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres.');
      return;
    }
    
    setIsLoading(true);
    try {
      await login(cleanEmail, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Credenciales incorrectas. Verifica tus datos.');
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-primary)', position: 'relative', overflow: 'hidden' }}>
      
      {}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', position: 'relative', zIndex: 10 }}>
        <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, type: 'spring' }} style={{ width: '100%', maxWidth: '440px' }}>
          
          <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', marginBottom: '48px', textDecoration: 'none' }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>N</div>
            <span className="text-h4" style={{ fontWeight: 800 }}>NovaChef</span>
          </Link>

          <h1 className="text-h2" style={{ marginBottom: '12px', fontSize: '2.5rem' }}>Iniciar Sesión</h1>
          <p className="text-muted" style={{ marginBottom: '40px', fontSize: '1.1rem' }}>Ingresa tus credenciales para acceder a tu espacio.</p>
          
          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '16px', borderRadius: '8px', marginBottom: '24px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 600, fontSize: '0.95rem' }}>Correo Electrónico</label>
              <input type="text" className="input" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="correo@empresa.com" maxLength={100} style={{ padding: '14px 16px' }} disabled={isLoading} />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Contraseña</label>
                <Link to="#" className="text-muted" style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--accent-blue)' }}>¿Olvidaste tu contraseña?</Link>
              </div>
              <input type="password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" maxLength={100} style={{ padding: '14px 16px' }} disabled={isLoading} />
            </div>
            <button type="submit" className="btn btn-gradient" style={{ width: '100%', padding: '16px', fontSize: '1.1rem', marginTop: '8px', opacity: isLoading ? 0.7 : 1 }} disabled={isLoading}>
              {isLoading ? 'Iniciando sesión...' : 'Ingresa a tu Espacio'}
            </button>
          </form>
          
          <div style={{ textAlign: 'center', marginTop: '32px' }}>
            <p className="text-muted" style={{ fontSize: '1rem' }}>
              ¿No tienes una cuenta? <Link to="/register" style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>Crea una ahora</Link>
            </p>
          </div>
        </motion.div>
      </div>

      {}
      <div style={{ flex: 1, display: 'none', '@media (minWidth: 1024px)': { display: 'block' }, position: 'relative' }}>
         <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', opacity: 0.1 }} />
         <div className="bg-glow-effect-right" style={{ filter: 'blur(100px)', opacity: 0.5 }} />
         <div style={{ position: 'absolute', inset: '40px', borderRadius: 'var(--radius-xl)', background: 'url(https://images.unsplash.com/photo-1555396273-367ea4eb4db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80) center/cover', boxShadow: 'var(--shadow-2xl)' }}>
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)', borderRadius: 'var(--radius-xl)' }} />
            <div style={{ position: 'absolute', bottom: 40, left: 40, right: 40, color: 'white' }}>
              <div className="glass" style={{ display: 'inline-block', padding: '12px 24px', borderRadius: 'var(--radius-full)', marginBottom: '20px', background: 'rgba(255,255,255,0.1)' }}>
                "La mejor plataforma que hemos usado."
              </div>
              <h2 style={{ fontSize: '2rem', fontWeight: 600, lineHeight: 1.3 }}>NovaChef transformó toda nuestra operación, reduciendo los tiempos de entrega un 30%.</h2>
            </div>
         </div>
      </div>
    </div>
  );
}