import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Plus, X, ShoppingCart, Package } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { eventEmitter } from '../utils/eventEmitter';

const CATEGORY_ICONS = { Pizzas: '🍕', Hamburguesas: '🍔', 'Platos Fuertes': '🍽️', Entradas: '🥗', Postres: '🍰', Bebidas: '🥤' };

export default function MenuPage() {
  const [items, setItems] = useState([]);
  const [activeTab, setActiveTab] = useState('Todos');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', price: '', category: 'Platos Fuertes' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [addingId, setAddingId] = useState(null);
  const { user } = useAuth();
  const { addToCart } = useCart();

  const fetchMenu = async () => {
    try {
      setLoading(true);
      const res = await api.get('/menu/');
      setItems(res.data || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchMenu(); }, []);

  const categories = useMemo(() => {
    const cats = [...new Set(items.map(i => i.category))];
    return ['Todos', ...cats];
  }, [items]);

  const filtered = useMemo(() => {
    let result = items;
    if (activeTab !== 'Todos') result = result.filter(i => i.category === activeTab);
    if (search.trim()) result = result.filter(i => i.name.toLowerCase().includes(search.toLowerCase()));
    return result;
  }, [items, activeTab, search]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      const price = parseFloat(formData.price);
      if (!Number.isFinite(price) || price <= 0 || price > 5000) return;
      await api.post('/menu/', {
        name: formData.name.trim().slice(0, 100),
        description: formData.description.trim().slice(0, 500),
        price,
        category: formData.category,
        is_available: true,
      });
      setShowModal(false);
      setFormData({ name: '', description: '', price: '', category: 'Platos Fuertes' });
      fetchMenu();
      eventEmitter.emit('globalError', 'Producto creado correctamente');
    } catch {
      /* interceptor */
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddToCart = async (item) => {
    if (addingId === item.id) return;
    setAddingId(item.id);
    try {
      await addToCart(item.id, 1);
      eventEmitter.emit('globalError', `${item.name} añadido al carrito`);
    } catch {
      /* interceptor */
    } finally {
      setAddingId(null);
    }
  };

  const canManage = user?.role === 'admin';
  const canOrder = user?.role !== 'delivery';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 className="text-h2" style={{ marginBottom: '4px' }}>Menú</h1>
          <p className="text-muted" style={{ fontSize: '0.95rem' }}>{canManage ? 'Administra los platillos de tu restaurante.' : 'Explora nuestros platillos disponibles.'}</p>
        </div>
        {canManage && (
          <button className="btn btn-gradient" onClick={() => setShowModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Plus size={18} /> Nuevo Producto
          </button>
        )}
      </div>

      {}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: '1 1 250px', maxWidth: '400px' }}>
          <Search size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input type="text" className="input" placeholder="Buscar platillos..." value={search} onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: '42px', borderRadius: 'var(--radius-full)', padding: '10px 14px 10px 42px' }} />
        </div>
        <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', padding: '4px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-full)' }}>
          {categories.map(cat => (
            <button key={cat} onClick={() => setActiveTab(cat)}
              style={{
                padding: '7px 16px', borderRadius: 'var(--radius-full)', border: 'none', cursor: 'pointer',
                fontWeight: 600, fontSize: '0.82rem', whiteSpace: 'nowrap',
                background: activeTab === cat ? 'var(--bg-primary)' : 'transparent',
                color: activeTab === cat ? 'var(--text-primary)' : 'var(--text-muted)',
                boxShadow: activeTab === cat ? 'var(--shadow-sm)' : 'none'
              }}>{cat}</button>
          ))}
        </div>
      </div>

      {}
      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Cargando menú...</div>
      ) : filtered.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>No se encontraron productos.</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
          <AnimatePresence>
            {filtered.map((item, i) => (
              <motion.div key={item.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ delay: i * 0.03 }}
                className="card glass-panel" style={{ padding: '0', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                {}
                <div style={{ height: '140px', background: 'linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '3rem', position: 'relative' }}>
                  {CATEGORY_ICONS[item.category] || <Package size={40} style={{ color: 'var(--text-muted)', opacity: 0.4 }} />}
                  {!item.is_available && (
                    <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: '0.9rem' }}>
                      Agotado
                    </div>
                  )}
                  <div style={{ position: 'absolute', top: 10, right: 10 }}>
                    <span style={{
                      padding: '3px 10px', borderRadius: '20px', fontSize: '0.7rem', fontWeight: 600,
                      background: 'rgba(0,0,0,0.5)', color: 'white', backdropFilter: 'blur(4px)'
                    }}>{item.category}</span>
                  </div>
                </div>
                <div style={{ padding: '16px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '4px', color: 'var(--text-primary)' }}>{item.name}</div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '12px', lineHeight: 1.4, flex: 1 }}>
                    {item.description || 'Delicioso platillo preparado con ingredientes frescos.'}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>${item.price.toFixed(2)}</span>
                    {canOrder && item.is_available && (
                      <button onClick={() => handleAddToCart(item)} disabled={addingId === item.id}
                        style={{ height: 34, padding: '0 14px', borderRadius: '8px', background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', border: 'none', cursor: addingId === item.id ? 'not-allowed' : 'pointer', color: 'white', fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px', opacity: addingId === item.id ? 0.6 : 1 }}>
                        <ShoppingCart size={14} /> {addingId === item.id ? '...' : 'Añadir'}
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, backdropFilter: 'blur(4px)' }}
          onClick={() => setShowModal(false)}>
          <div onClick={e => e.stopPropagation()} className="card glass-panel" style={{ width: '440px', maxWidth: '90%', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontWeight: 700, fontSize: '1.1rem' }}>Nuevo Producto</h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={20} /></button>
            </div>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.88rem' }}>Nombre</label>
                <input type="text" className="input" required value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} placeholder="Ej: Hamburguesa Triple" style={{ padding: '10px 14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.88rem' }}>Descripción</label>
                <input type="text" className="input" value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} placeholder="Descripción del producto" style={{ padding: '10px 14px' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.88rem' }}>Precio ($)</label>
                  <input type="number" step="0.01" className="input" required value={formData.price} onChange={e => setFormData({ ...formData, price: e.target.value })} placeholder="15.99" style={{ padding: '10px 14px' }} />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.88rem' }}>Categoría</label>
                  <select className="input" required value={formData.category} onChange={e => setFormData({ ...formData, category: e.target.value })} style={{ padding: '10px 14px' }}>
                    <option value="Platos Fuertes">Platos Fuertes</option>
                    <option value="Pizzas">Pizzas</option>
                    <option value="Hamburguesas">Hamburguesas</option>
                    <option value="Entradas">Entradas</option>
                    <option value="Postres">Postres</option>
                    <option value="Bebidas">Bebidas</option>
                  </select>
                </div>
              </div>
              <button type="submit" className="btn btn-gradient" disabled={isSubmitting} style={{ width: '100%', padding: '12px', marginTop: '4px', opacity: isSubmitting ? 0.7 : 1 }}>
                {isSubmitting ? 'Guardando...' : 'Crear Producto'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
