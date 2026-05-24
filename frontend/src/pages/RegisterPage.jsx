import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

export default function RegisterPage() {
  const [formData, setFormData] = useState({ username: '', first_name: '', last_name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && isAuthenticated) navigate('/dashboard', { replace: true });
  }, [loading, isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const uName = formData.username.trim().substring(0, 30);
    const fName = formData.first_name.trim().substring(0, 50);
    const lName = formData.last_name.trim().substring(0, 50);
    const mail = formData.email.trim().substring(0, 100);
    const pwd = formData.password.substring(0, 50);

    if (uName.length < 3 || uName.length > 30) {
      setError('El nombre de usuario debe tener entre 3 y 30 caracteres.');
      return;
    }
    if (!/^[a-zA-Z0-9_]+$/.test(uName)) {
      setError('El nombre de usuario solo puede contener letras, números y guiones bajos.');
      return;
    }
    if (fName.length < 2) {
      setError('El nombre debe tener al menos 2 caracteres.');
      return;
    }
    if (lName.length < 2) {
      setError('El apellido debe tener al menos 2 caracteres.');
      return;
    }
    if (pwd.length < 8 || pwd.length > 20) {
      setError('La contraseña debe tener entre 8 y 20 caracteres.');
      return;
    }
    if (!/[A-Z]/.test(pwd) || !/[a-z]/.test(pwd) || !/[0-9]/.test(pwd)) {
      setError('La contraseña debe contener al menos una mayúscula, una minúscula y un número.');
      return;
    }
    
    setIsLoading(true);
    try {
      await register({ ...formData, username: uName, first_name: fName, last_name: lName, email: mail, password: pwd });
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Error al crear la cuenta. Verifica tus datos.');
      setIsLoading(false);
    }
  };

  const update = (key, value) => setFormData({ ...formData, [key]: value });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-primary)', position: 'relative', overflow: 'hidden' }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', position: 'relative', zIndex: 10 }}>
        <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, type: 'spring' }} style={{ width: '100%', maxWidth: '480px' }}>

          <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', marginBottom: '40px', textDecoration: 'none' }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>N</div>
            <span className="text-h4" style={{ fontWeight: 800 }}>NovaChef</span>
          </Link>

          <h1 className="text-h2" style={{ marginBottom: '12px', fontSize: '2.2rem' }}>Crear Cuenta</h1>
          <p className="text-muted" style={{ marginBottom: '32px', fontSize: '1.05rem' }}>Regístrate para gestionar tu restaurante o realizar pedidos.</p>

          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '14px 16px', borderRadius: '10px', marginBottom: '20px', border: '1px solid rgba(239, 68, 68, 0.2)', fontSize: '0.95rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '0.9rem' }}>Nombre</label>
                <input type="text" className="input" value={formData.first_name} onChange={(e) => update('first_name', e.target.value)} required placeholder="Juan" maxLength={50} style={{ padding: '12px 14px' }} disabled={isLoading} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '0.9rem' }}>Apellido</label>
                <input type="text" className="input" value={formData.last_name} onChange={(e) => update('last_name', e.target.value)} required placeholder="Pérez" maxLength={50} style={{ padding: '12px 14px' }} disabled={isLoading} />
              </div>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '0.9rem' }}>Usuario</label>
              <input type="text" className="input" value={formData.username} onChange={(e) => update('username', e.target.value)} required placeholder="juanperez_123" maxLength={30} style={{ padding: '12px 14px' }} disabled={isLoading} />
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '5px' }}>3-30 caracteres, letras, números y '_'</div>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '0.9rem' }}>Correo Electrónico</label>
              <input type="email" className="input" value={formData.email} onChange={(e) => update('email', e.target.value)} required placeholder="correo@empresa.com" maxLength={100} style={{ padding: '12px 14px' }} disabled={isLoading} />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '0.9rem' }}>Contraseña</label>
              <input type="password" className="input" value={formData.password} onChange={(e) => update('password', e.target.value)} required placeholder="••••••••" maxLength={50} style={{ padding: '12px 14px' }} disabled={isLoading} />
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '5px' }}>8-20 caracteres, 1 mayúscula, 1 minúscula, 1 número</div>
            </div>
            <button type="submit" className="btn btn-gradient" style={{ width: '100%', padding: '14px', fontSize: '1.05rem', marginTop: '6px', opacity: isLoading ? 0.7 : 1 }} disabled={isLoading}>
              {isLoading ? 'Creando cuenta...' : 'Crear Cuenta'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '28px' }}>
            <p className="text-muted" style={{ fontSize: '0.95rem' }}>
              ¿Ya tienes una cuenta? <Link to="/login" style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>Inicia sesión aquí</Link>
            </p>
          </div>
        </motion.div>
      </div>

      <div style={{ flex: 1, display: 'none', position: 'relative' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))', opacity: 0.1 }} />
        <div style={{ position: 'absolute', inset: '40px', borderRadius: 'var(--radius-xl)', background: 'url(https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80) center/cover', boxShadow: 'var(--shadow-2xl)' }}>
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)', borderRadius: 'var(--radius-xl)' }} />
          <div style={{ position: 'absolute', bottom: 40, left: 40, right: 40, color: 'white' }}>
            <h2 style={{ fontSize: '2.2rem', fontWeight: 700, lineHeight: 1.2, marginBottom: '20px' }}>La plataforma que tu restaurante necesita.</h2>
          </div>
        </div>
      </div>
    </div>
  );
}
