import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Package, AlertTriangle, X, Download } from 'lucide-react';
import { api } from '../api/client';
import { eventEmitter } from '../utils/eventEmitter';

export default function InventoryPage() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [stockInput, setStockInput] = useState('');
  const [minStockInput, setMinStockInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const res = await api.get('/inventory/');
      setInventory(res.data || []);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchInventory(); }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    const stock = parseInt(stockInput, 10);
    const minStock = parseInt(minStockInput, 10);
    if (!Number.isFinite(stock) || stock < 0 || stock > 99999) return;
    if (!Number.isFinite(minStock) || minStock < 0 || minStock > 99999) return;
    setIsSubmitting(true);
    try {
      await api.put(`/inventory/${selectedItem.id}`, { stock, min_stock: minStock });
      setShowModal(false);
      fetchInventory();
      eventEmitter.emit('globalError', 'Inventario actualizado correctamente');
    } catch {
      /* interceptor */
    } finally {
      setIsSubmitting(false);
    }
  };

  const openUpdateModal = (item) => {
    setSelectedItem(item);
    setStockInput(item.stock.toString());
    setMinStockInput(item.min_stock.toString());
    setShowModal(true);
  };

  const lowCount = inventory.filter(i => i.stock <= i.min_stock).length;
  const totalStock = inventory.reduce((s, i) => s + i.stock, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 className="text-h2" style={{ marginBottom: '4px' }}>Inventario</h1>
          <p className="text-muted" style={{ fontSize: '0.95rem' }}>Monitorea y administra el stock de todos tus productos.</p>
        </div>
      </div>

      {}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div className="card glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Productos Rastreados</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>{inventory.length}</div>
        </div>
        <div className="card glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Stock Total</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>{totalStock}</div>
        </div>
        <div className="card glass-panel" style={{ padding: '20px', border: lowCount > 0 ? '1px solid rgba(239,68,68,0.3)' : undefined }}>
          <div style={{ fontSize: '0.82rem', color: lowCount > 0 ? '#ef4444' : 'var(--text-muted)', fontWeight: 600, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            {lowCount > 0 && <AlertTriangle size={14} />} Alertas de Stock Bajo
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: lowCount > 0 ? '#ef4444' : 'var(--text-primary)' }}>{lowCount}</div>
        </div>
      </div>

      {}
      <div className="card glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-light)', background: 'var(--bg-secondary)' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Producto</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Stock Actual</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Stock Mínimo</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estado</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Acción</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>Cargando inventario...</td></tr>
              ) : inventory.length === 0 ? (
                <tr><td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>No hay productos en el inventario.</td></tr>
              ) : (
                inventory.map(item => {
                  const isLow = item.stock <= item.min_stock;
                  return (
                    <tr key={item.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '14px 16px', fontWeight: 600, fontSize: '0.9rem' }}>
                        {item.menu_item?.name || `Producto #${item.menu_item_id}`}
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'center', fontWeight: 700, fontSize: '1rem', color: isLow ? '#ef4444' : 'var(--text-primary)' }}>
                        {item.stock}
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                        {item.min_stock}
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                        <span style={{
                          display: 'inline-block', padding: '3px 12px', borderRadius: '20px', fontSize: '0.76rem', fontWeight: 600,
                          background: isLow ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)',
                          color: isLow ? '#ef4444' : '#10b981'
                        }}>
                          {isLow ? 'Bajo' : 'Normal'}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button onClick={() => openUpdateModal(item)}
                          style={{ height: 32, padding: '0 14px', borderRadius: '8px', background: 'var(--bg-tertiary)', border: '1px solid var(--border-light)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                          Editar Stock
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {}
      {showModal && selectedItem && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, backdropFilter: 'blur(4px)' }}
          onClick={() => setShowModal(false)}>
          <div onClick={e => e.stopPropagation()} className="card glass-panel" style={{ width: '400px', maxWidth: '90%', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontWeight: 700, fontSize: '1.1rem' }}>Editar Inventario</h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={20} /></button>
            </div>
            <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px', marginBottom: '16px', fontWeight: 600, fontSize: '0.95rem' }}>
              {selectedItem.menu_item?.name || `Producto #${selectedItem.menu_item_id}`}
            </div>
            <form onSubmit={handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.88rem' }}>Stock Actual</label>
                <input type="number" min="0" className="input" required value={stockInput} onChange={e => setStockInput(e.target.value)} style={{ padding: '10px 14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.88rem' }}>Stock Mínimo (Alerta)</label>
                <input type="number" min="0" className="input" required value={minStockInput} onChange={e => setMinStockInput(e.target.value)} style={{ padding: '10px 14px' }} />
              </div>
              <button type="submit" className="btn btn-gradient" disabled={isSubmitting} style={{ width: '100%', padding: '12px', marginTop: '4px', opacity: isSubmitting ? 0.7 : 1 }}>
                {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
