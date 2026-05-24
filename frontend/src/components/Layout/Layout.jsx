import { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, Menu as MenuIcon, ShoppingCart, Receipt,
  CreditCard, Package, Truck, BarChart3, LogOut, Sun, Moon, Bell, X
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Panel', icon: LayoutDashboard, roles: ['admin', 'cajero', 'delivery', 'cliente'] },
  { path: '/menu', label: 'Menú', icon: MenuIcon, roles: ['admin', 'cajero', 'cliente'] },
  { path: '/cart', label: 'Carrito', icon: ShoppingCart, roles: ['admin', 'cajero', 'cliente'] },
  { path: '/orders', label: 'Pedidos', icon: Receipt, roles: ['admin', 'cajero', 'cliente', 'delivery'] },
  { path: '/payments', label: 'Pagos', icon: CreditCard, roles: ['admin', 'cajero'] },
  { path: '/inventory', label: 'Inventario', icon: Package, roles: ['admin'] },
  { path: '/delivery', label: 'Entregas', icon: Truck, roles: ['admin', 'delivery'] },
  { path: '/reports', label: 'Reportes', icon: BarChart3, roles: ['admin'] },
];

const ROLE_LABELS = { admin: 'Administrador', cajero: 'Cajero', delivery: 'Repartidor', cliente: 'Cliente' };

function getUserInitials(user) {
  if (user?.first_name && user?.last_name) return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
  if (user?.username) return user.username.substring(0, 2).toUpperCase();
  return 'U';
}

function getUserDisplayName(user) {
  if (user?.first_name && user?.last_name) return `${user.first_name} ${user.last_name}`;
  return user?.username || 'Usuario';
}

export default function Layout() {
  const { user, logout, loading } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (!loading && !user) {
    return <Navigate to="/login" replace />;
  }

  const filteredNav = navItems.filter(item => item.roles.includes(user?.role || 'cliente'));

  const userSection = (
    <div style={{ padding: 'var(--space-4)', borderTop: '1px solid var(--border-light)' }}>
      <div style={{ padding: '12px', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px', background: 'var(--bg-tertiary)' }}>
        {user?.avatar_url ? (
          <img src={user.avatar_url} alt="" style={{ width: 40, height: 40, borderRadius: '50%', objectFit: 'cover' }} />
        ) : (
          <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: '0.9rem', flexShrink: 0 }}>
            {getUserInitials(user)}
          </div>
        )}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
            {getUserDisplayName(user)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>{ROLE_LABELS[user?.role] || user?.role}</div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button onClick={toggleTheme} className="btn btn-secondary" style={{ flex: 1, padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button onClick={() => { logout(); navigate('/login'); }} className="btn btn-secondary" style={{ flex: 1, padding: '10px', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LogOut size={18} />
        </button>
      </div>
    </div>
  );

  return (
    <>
      <div className="bg-glow-effect" />
      <div className="bg-glow-effect-right" />
      <div className="app-container" style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>

        {}
        <aside className="glass-panel hide-mobile" style={{ width: '260px', display: 'flex', flexDirection: 'column', borderRight: '1px solid var(--border-light)', zIndex: 10, flexShrink: 0 }}>
          <div style={{ padding: '20px 20px 16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'var(--shadow-glow)', fontWeight: 'bold', fontSize: '18px' }}>N</div>
            <div className="text-h4 text-gradient" style={{ fontWeight: 800 }}>NovaChef</div>
          </div>

          <nav style={{ flex: 1, padding: '0 12px', display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 600, padding: '12px 12px 8px', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
              Navegación
            </div>
            {filteredNav.map((item) => (
              <NavLink key={item.path} to={item.path} style={{ textDecoration: 'none' }}>
                {({ isActive }) => (
                  <motion.div whileHover={{ x: 3 }} whileTap={{ scale: 0.98 }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '14px', padding: '11px 16px',
                      borderRadius: 'var(--radius-md)',
                      color: isActive ? 'white' : 'var(--text-secondary)',
                      background: isActive ? 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))' : 'transparent',
                      fontWeight: isActive ? 600 : 500, fontSize: '0.92rem',
                      boxShadow: isActive ? 'var(--shadow-glow)' : 'none',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <item.icon size={20} style={{ opacity: isActive ? 1 : 0.65 }} />
                    {item.label}
                  </motion.div>
                )}
              </NavLink>
            ))}
          </nav>

          {userSection}
        </aside>

        {}
        <AnimatePresence>
          {mobileMenuOpen && (
            <>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 40, backdropFilter: 'blur(4px)' }}
                onClick={() => setMobileMenuOpen(false)}
              />
              <motion.aside initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }} transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="glass-panel"
                style={{ position: 'fixed', top: 0, bottom: 0, left: 0, width: '280px', display: 'flex', flexDirection: 'column', zIndex: 50, background: 'var(--bg-primary)' }}
              >
                <div style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>N</div>
                    <div className="text-h4 text-gradient" style={{ fontWeight: 800 }}>NovaChef</div>
                  </div>
                  <button onClick={() => setMobileMenuOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-primary)', cursor: 'pointer' }}><X size={24} /></button>
                </div>
                <nav style={{ flex: 1, padding: '0 12px', display: 'flex', flexDirection: 'column', gap: '4px', overflowY: 'auto' }}>
                  {filteredNav.map((item) => (
                    <NavLink key={item.path} to={item.path} onClick={() => setMobileMenuOpen(false)} style={{ textDecoration: 'none' }}>
                      {({ isActive }) => (
                        <div style={{
                          display: 'flex', alignItems: 'center', gap: '14px', padding: '12px 16px', borderRadius: 'var(--radius-md)',
                          color: isActive ? 'white' : 'var(--text-secondary)',
                          background: isActive ? 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))' : 'transparent',
                          fontWeight: isActive ? 600 : 500
                        }}>
                          <item.icon size={20} style={{ opacity: isActive ? 1 : 0.7 }} /> {item.label}
                        </div>
                      )}
                    </NavLink>
                  ))}
                </nav>
                {userSection}
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 5, overflow: 'hidden', width: '100%' }}>
          <header className="glass" style={{
            minHeight: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px',
            padding: '12px 24px', margin: '16px 16px 0', borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-light)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <button className="show-mobile" onClick={() => setMobileMenuOpen(true)} style={{ background: 'none', border: 'none', color: 'var(--text-primary)', cursor: 'pointer' }}>
                <MenuIcon size={24} />
              </button>
              <div>
                <div style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-primary)' }}>
                  {navItems.find(n => location.pathname.startsWith(n.path))?.label || 'NovaChef'}
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  {new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={() => navigate('/cart')} style={{ position: 'relative', color: 'var(--text-secondary)', background: 'none', border: 'none', cursor: 'pointer' }}>
                <ShoppingCart size={22} />
              </motion.button>
              <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} style={{ position: 'relative', color: 'var(--text-secondary)', background: 'none', border: 'none', cursor: 'pointer' }}>
                <Bell size={22} />
              </motion.button>
              <div className="hide-mobile" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="" style={{ width: 34, height: 34, borderRadius: '50%', objectFit: 'cover' }} />
                ) : (
                  <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: '0.8rem' }}>
                    {getUserInitials(user)}
                  </div>
                )}
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{getUserDisplayName(user)}</div>
              </div>
            </div>
          </header>

          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 32px', display: 'flex', flexDirection: 'column', width: '100%' }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                transition={{ duration: 0.25 }}
                style={{ width: '100%', flex: 1, display: 'flex', flexDirection: 'column' }}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </>
  );
}
